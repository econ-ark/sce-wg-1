"""The runner: every toolkit on an experiment's members and levels, the verification of every results file, and the
registry's records. The `wg1core` command.

    wg1core list
    wg1core run <experiment.yaml> --toolkits hark,dolo [--levels low,medium] [--members <id>,...] [--jobs 8] \\
        [--out <run folder>] [--runtime uv|docker] [--cpus 2] [--memory 8g] [--wall-seconds 3600]
    wg1core verify <run folder>
    wg1core register <run folder>

Every command reads a model repository's registry file, `--registry`, `harness/toolkits.yaml` under the current
directory by default. The file names the toolkits, each with its adapter, the files its runs depend on, its
environment, its stone, its levels and its thread cap, and under `model` what the core needs of the repository: its
results schema, its source page's anchors, its experiments folder, its verifier and its registry folder (README.md).
The repository's root is the git top level of the registry file's folder.

`run` checks the experiment and refuses one with problems. It then runs one job for each toolkit, member and level,
in parallel, each through the toolkit's adapter: with `--runtime uv`, the default, in the adapter's uv project on this
machine; with `--runtime docker`, in an image built from the adapter's environment directory and run under the
container contract (the repository mounted read-only at /src, the job's folder at /out, no network, the thread cap, a
scratch /tmp, and the caps given). Each toolkit's first job runs alone before its others, so that one process writes
what the toolkit compiles and caches. A job writes into <run folder>/<toolkit>/<member>/level-<n>/ and leaves there
the adapter's log, `job.json`, its status and a fingerprint of everything its output depends on, and `record.json`,
its execution record for the registry. A job whose fingerprint is unchanged and whose results file exists is skipped.
With `--runtime docker` each toolkit's image is built first and its build record written as
<run folder>/<toolkit>/build.json. `manifest.json` in the run folder names every hash.

`verify` runs the model's verifier on every results file, or validates it against the results schema when the model
names none, checks that each carries the quantities the experiment's `reports` names, and writes `verification.json`
and each record's verdict. `register` copies a run's records into the registry folder, one file per job and one per
build, validating each.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import jsonschema
import yaml

from . import VERSION, canonical, records
from . import experiment as experiments

LEVEL_NUMBER = {"low": 1, "medium": 2, "high": 3}
THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
OUTPUTS = ("results.json", "methods.yaml", "settings.yaml")
IMAGE_PREFIX = "sce-wg-1"
TOOLKIT_KEYS = {"adapter", "code", "environment", "stone", "levels", "threads"}
MODEL_KEYS = {"results_schema", "anchors", "experiments", "verifier", "registry_dir"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# The model repository ---------------------------------------------------------------------------------------------------

class Model:
    """The model repository a registry file describes: its root, its toolkits, and what the core needs of it."""

    def __init__(self, registry_file: Path):
        self.file = Path(registry_file).resolve()
        if not self.file.is_file():
            raise SystemExit(f"no registry file at {self.file}")
        self.dir = self.file.parent
        raw = yaml.safe_load(self.file.read_text(encoding="utf-8")) or {}
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=self.dir, capture_output=True, text=True)
        self.root = Path(top.stdout.strip()).resolve() if top.returncode == 0 and top.stdout.strip() else self.dir.parent
        m = raw.get("model") or {}
        unknown = set(m) - MODEL_KEYS
        if unknown:
            raise SystemExit(f"{self.file.name}: model: unknown keys {sorted(unknown)}")
        self.results_schema_file = (self.dir / m["results_schema"]).resolve() if m.get("results_schema") else None
        self.results_schema = (json.loads(self.results_schema_file.read_text(encoding="utf-8"))
                               if self.results_schema_file else None)
        anchors = (self.dir / m["anchors"]).resolve() if m.get("anchors") else None
        self.anchors = experiments.read_anchors(anchors) if anchors and anchors.is_file() else None
        self.experiments_dir = (self.dir / m["experiments"]).resolve() if m.get("experiments") else self.root
        self.verifier = [str(a) for a in m["verifier"]] if m.get("verifier") else None
        self.registry_dir = (self.dir / m.get("registry_dir", "runs.registry")).resolve()
        self.toolkits = self._toolkits(raw.get("toolkits") or {})

    def _toolkits(self, raw: dict) -> dict:
        out = {}
        for name, entry in raw.items():
            unknown = set(entry) - TOOLKIT_KEYS
            if unknown or not {"adapter", "levels"} <= set(entry):
                raise SystemExit(f"{self.file.name}: {name}: unknown keys {sorted(unknown)} or no adapter or levels")
            tk = {"name": name, "adapter": (self.dir / entry["adapter"]).resolve(),
                  "levels": dict(entry["levels"]), "threads": int(entry.get("threads", 2))}
            tk["environment"] = (self.dir / entry["environment"]).resolve() if entry.get("environment") else None
            tk["stone"] = (self.dir / entry["stone"]).resolve() if entry.get("stone") else None
            files = set()
            for pattern in entry.get("code", []) + [entry["adapter"]]:
                for f in glob.glob(str(self.dir / pattern)):
                    if not Path(f).name.startswith("test_"):
                        files.add(Path(f).resolve())
            tk["code"] = sorted(files)
            out[name] = tk
        return out

    def rel(self, path: Path) -> str:
        """A path relative to the repository's root, for the records; absolute if it lies outside."""
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(Path(path).resolve())


def environment_identity(tk: dict, model: Model) -> dict | None:
    """What identifies a toolkit's environment: its lock file and interpreter, its Dockerfile when it has one, and
    the image it was built into when the run is in containers."""
    env = tk["environment"]
    if env is None:
        return None
    version = env / ".python-version"
    out = {"project": model.rel(env), "lock_sha256": sha256_file(env / "uv.lock") if (env / "uv.lock").is_file() else None,
           "python": version.read_text(encoding="utf-8").strip() if version.is_file() else None}
    if (env / "Dockerfile").is_file():
        out["dockerfile_sha256"] = sha256_file(env / "Dockerfile")
    if tk.get("image_id"):
        out["image_id"] = tk["image_id"]
    return out


def code_sha256(tk: dict, model: Model) -> str:
    h = hashlib.sha256()
    for f in tk["code"]:
        h.update(model.rel(f).encode() + b"\0" + Path(f).read_bytes() + b"\0")
    return h.hexdigest()


# The experiment and the jobs ------------------------------------------------------------------------------------------

def load_experiment(path: Path, model: Model) -> tuple[dict, str]:
    """The experiment and its hash; refuses one with problems."""
    path = Path(path).resolve()
    data = canonical.load_strict(path.read_text(encoding="utf-8"))
    problems = experiments.problems(data, path.parent, model.results_schema, model.anchors)
    if problems:
        raise SystemExit("the experiment has problems:\n  " + "\n  ".join(problems))
    return data, canonical.model_hash(data)


def plan_jobs(exp_path: Path, exp: dict, model: Model, toolkits: list[str], levels: list[str], members: list[str],
              out: Path) -> list[dict]:
    folder = Path(exp_path).resolve().parent
    by_id = {m["id"]: m for m in exp["members"]}
    unknown = [m for m in members if m not in by_id] + [t for t in toolkits if t not in model.toolkits]
    unknown += [lv for lv in levels if lv not in LEVEL_NUMBER]
    if unknown:
        raise SystemExit(f"unknown toolkit, member or level: {unknown}")
    jobs = []
    for name in toolkits:
        tk = model.toolkits[name]
        missing = [lv for lv in levels if lv not in tk["levels"]]
        if missing:
            raise SystemExit(f"{name} offers no level {missing}")
        for mid in members:
            m = by_id[mid]
            for lv in levels:
                jobs.append({"toolkit": name, "member": mid, "level": lv, "level_arg": tk["levels"][lv],
                             "parameter_file": (folder / m["parameter_file"]).resolve(),
                             "request_file": (folder / m["request_file"]).resolve(),
                             "parameter_file_sha256": m["parameter_file_sha256"],
                             "request_file_sha256": m["request_file_sha256"],
                             "dir": out / name / mid / f"level-{LEVEL_NUMBER[lv]}"})
    return jobs


def fingerprint(job: dict, tk: dict, model: Model) -> dict:
    """Everything a job's output depends on that the harness can name."""
    return {"toolkit": tk["name"], "member": job["member"], "level": job["level"], "level_arg": job["level_arg"],
            "parameter_file_sha256": job["parameter_file_sha256"], "request_file_sha256": job["request_file_sha256"],
            "environment": environment_identity(tk, model), "code_sha256": code_sha256(tk, model), "threads": tk["threads"]}


def adapter_arguments(job: dict, out_dir: str, in_container: bool, model: Model) -> list[str]:
    """The adapter contract's arguments: the parameter file, --out, --level and --request."""
    p = model.rel(job["parameter_file"]) if in_container else str(job["parameter_file"])
    r = model.rel(job["request_file"]) if in_container else str(job["request_file"])
    return [p, "--out", out_dir, "--level", str(job["level_arg"]), "--request", r]


def command(job: dict, tk: dict, model: Model) -> list[str]:
    args = [str(tk["adapter"])] + adapter_arguments(job, str(job["dir"]), False, model)
    if tk["environment"] is None:
        return [sys.executable] + args
    return ["uv", "run", "--quiet", "--project", str(tk["environment"]), "--frozen", "python"] + args


def container_name(job: dict, run_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "-", f"wg1-{run_id}-{job['toolkit']}-{job['member']}-{job['level']}")[:120]


def container_command(job: dict, tk: dict, ctx: dict) -> list[str]:
    """One job under the container contract: the repository read-only at /src, the job's folder at /out, no network,
    the thread cap, a scratch /tmp for what the toolkit caches, and the caps given."""
    caps, model = ctx["caps"], ctx["model"]
    cmd = ["docker", "run", "--init", "--name", container_name(job, ctx["run_id"]),
           "--user", f"{os.getuid()}:{os.getgid()}", "--network", "none", "--cpus", str(caps["cpus"])]
    if caps.get("memory"):
        cmd += ["--memory", caps["memory"]]
    for v in THREAD_VARIABLES:
        cmd += ["--env", f"{v}={tk['threads']}"]
    cmd += ["--tmpfs", "/tmp", "--env", "HOME=/tmp", "--env", "NUMBA_CACHE_DIR=/tmp/numba", "--env", "MPLCONFIGDIR=/tmp/mpl",
            "--mount", f"type=bind,source={model.root},target=/src,readonly",
            "--mount", f"type=bind,source={job['dir']},target=/out",
            "--workdir", "/src", tk["image_id"], "python", model.rel(tk["adapter"])]
    return cmd + adapter_arguments(job, "/out", True, model)


def docker(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    done = subprocess.run(["docker", *args], capture_output=True, text=True)
    if check and done.returncode:
        raise SystemExit(f"docker {' '.join(args[:2])}: {done.stderr.strip()[:400]}")
    return done


def build_image(tk: dict, out: Path, ctx: dict) -> str:
    """Builds a toolkit's image from its environment directory, writes the build record, and returns the image ID.
    The image is named for the environment's hash, so that an unchanged specification keeps its name."""
    model, env = ctx["model"], tk["environment"]
    if env is None or not (env / "Dockerfile").is_file():
        raise SystemExit(f"{tk['name']}: --runtime docker needs a Dockerfile in {model.rel(env) if env else 'an environment'}")
    environment = records.environment(model.root, ctx["repo"], model.rel(env), "dockerfile", ctx["where"]["runtime"])
    tag = f"{IMAGE_PREFIX}/{tk['name']}:{environment['sha256'][:12]}"
    folder = out / tk["name"]
    folder.mkdir(parents=True, exist_ok=True)
    started, clock = records.now(), time.perf_counter()
    with open(folder / "build.log", "w", encoding="utf-8") as log:
        code = subprocess.run(["docker", "build", "--file", str(env / "Dockerfile"), "--tag", tag, str(env)],
                              cwd=model.root, stdout=log, stderr=subprocess.STDOUT).returncode
    duration, ended = time.perf_counter() - clock, records.now()
    if code:
        raise SystemExit(f"{tk['name']}: the image build failed; see {model.rel(folder / 'build.log')}")
    image_id = docker("image", "inspect", "--format", "{{.Id}}", tag).stdout.strip()
    record = {"$schema": records.MODEL_SCHEMA_ID, "record_version": records.RECORD_VERSION, "kind": "build",
              "recorder": ctx["recorder"], "repository": ctx["repo"], "environment": environment,
              "image": {"name": tag, "id": image_id}, "where": ctx["where"], "conditions": {"network": True},
              "when": {"started": started, "ended": ended, "duration_seconds": round(duration, 3)},
              "outcome": {"exit_code": code, "termination": "exited", "log": "build.log"}}
    records.write(record, folder / "build.json")
    return image_id


def execution_record(job: dict, tk: dict, ctx: dict, cmd: list[str], when: dict, exit_code: int,
                     termination: str, signal: str | None) -> dict:
    model, d = ctx["model"], job["dir"]
    in_container = ctx["runtime"] == "docker"
    env_path = model.rel(tk["environment"]) if tk["environment"] is not None else model.rel(model.dir)
    environment = records.environment(model.root, ctx["repo"], env_path, "dockerfile" if in_container else "host-uv",
                                      ctx["where"]["runtime"] if in_container else ctx["uv_version"])
    conditions = {"thread_variables": {v: str(tk["threads"]) for v in THREAD_VARIABLES}}
    if in_container:
        conditions.update({"jit_cache": "cold", "cpus": ctx["caps"]["cpus"], "network": False})
        if ctx["caps"].get("memory_bytes"):
            conditions["memory_bytes"] = ctx["caps"]["memory_bytes"]
    if ctx["caps"].get("wall_seconds"):
        conditions["wall_seconds"] = ctx["caps"]["wall_seconds"]
    results = d / "results.json"
    toolkit_block = {}
    if results.is_file():
        try:
            toolkit_block = json.loads(results.read_text(encoding="utf-8")).get("toolkit", {}) or {}
        except ValueError:
            toolkit_block = {}
    outcome = {"exit_code": exit_code, "termination": termination, "output_dir": ".",
               "outputs": records.outputs(d, OUTPUTS), "log": "adapter.log"}
    if signal:
        outcome["signal"] = signal
    fields = {"experiment": ctx["experiment"], "toolkit": tk["name"],
              "adapter": {"path": model.rel(tk["adapter"]), "code_sha256": code_sha256(tk, model)},
              "member": {"id": job["member"], "hash": ctx["member_hashes"][job["member"]],
                         "parameter_file_sha256": job["parameter_file_sha256"]},
              "request": {"sha256": job["request_file_sha256"]}, "level": job["level"],
              "results_sha256": next((o["sha256"] for o in outcome["outputs"] if o["path"] == "results.json"), "0" * 64),
              "verification": {"verdict": "not run"}, "core_version": VERSION}
    for name, key in (("settings.yaml", "settings_sha256"), ("methods.yaml", "methods_sha256")):
        h = next((o["sha256"] for o in outcome["outputs"] if o["path"] == name), None)
        if h:
            fields[key] = h
    if toolkit_block.get("version"):
        fields["toolkit_version"] = " ".join(str(toolkit_block[k]) for k in ("name", "version", "commit") if toolkit_block.get(k))
    adapter = model.rel(tk["adapter"]) if in_container else str(tk["adapter"])
    record = {"$schema": records.MODEL_SCHEMA_ID, "record_version": records.RECORD_VERSION, "kind": "execution",
              "recorder": ctx["recorder"], "run": {"id": ctx["run_id"], "manifest": "../../../manifest.json"},
              "repository": ctx["repo"], "script": model.rel(tk["adapter"]), "arguments": cmd[cmd.index(adapter) + 1:],
              "environment": environment, "where": ctx["where"], "conditions": conditions, "when": when,
              "outcome": outcome, "extensions": {"sce-wg-1": fields}}
    if in_container:
        record["image"] = {"id": tk["image_id"], "build_record": "../../build.json"}
    return record


def run_job(job: dict, tk: dict, ctx: dict) -> dict:
    model, d = ctx["model"], job["dir"]
    fp = fingerprint(job, tk, model)
    record = d / "job.json"
    if record.is_file() and (d / "results.json").is_file():
        old = json.loads(record.read_text(encoding="utf-8"))
        if old.get("status") == "ok" and old.get("fingerprint") == fp:
            return {**old, "skipped": True}
    d.mkdir(parents=True, exist_ok=True)
    for stale in ("results.json", "job.json", "record.json"):
        (d / stale).unlink(missing_ok=True)
    env = os.environ.copy()
    env.update({v: str(tk["threads"]) for v in THREAD_VARIABLES})
    in_container = ctx["runtime"] == "docker"
    cmd = container_command(job, tk, ctx) if in_container else command(job, tk, model)
    termination, signal = "exited", None
    started, clock = records.now(), time.perf_counter()
    with open(d / "adapter.log", "w", encoding="utf-8") as log:
        try:
            code = subprocess.run(cmd, cwd=model.root, env=env, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=ctx["caps"].get("wall_seconds")).returncode
        except subprocess.TimeoutExpired:
            code, termination = 124, "timeout"
            if in_container:
                docker("kill", container_name(job, ctx["run_id"]), check=False)
    when = {"started": started, "ended": records.now(), "duration_seconds": round(time.perf_counter() - clock, 3)}
    if in_container:
        state = docker("inspect", "--format", "{{.State.ExitCode}} {{.State.OOMKilled}}",
                       container_name(job, ctx["run_id"]), check=False)
        if state.returncode == 0:
            exit_in, oom = state.stdout.split()
            if termination == "exited":
                code = int(exit_in)
                if oom == "true":
                    termination = "oom"
                elif code > 128:
                    termination, signal = "signal", f"signal {code - 128}"
        docker("rm", "--force", container_name(job, ctx["run_id"]), check=False)
    ok = code == 0 and (d / "results.json").is_file()
    shown = [model.rel(Path(c)) if c.startswith("/") else c for c in cmd]
    if tk["environment"] is None:
        shown[0] = "python"
    out = {"status": "ok" if ok else "failed", "exit_code": code, "command": shown, "fingerprint": fp}
    record.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    records.write(execution_record(job, tk, ctx, shown if in_container else cmd, when, code, termination, signal),
                  d / "record.json")
    return {**out, "skipped": False}


def model_commit(model: Model) -> dict:
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=model.root, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=model.root, capture_output=True, text=True).stdout.strip()
    return {"commit": head or None, "uncommitted_changes": "yes" if dirty else "no"}


def memory_bytes(spec: str | None) -> int | None:
    """Docker's memory spec, such as 8g or 512m, as bytes."""
    if not spec:
        return None
    m = re.fullmatch(r"(\d+)([kmgKMG]?)", spec.strip())
    if not m:
        raise SystemExit(f"--memory {spec}: give a number with k, m or g")
    return int(m.group(1)) * {"": 1, "k": 1024, "m": 1024 ** 2, "g": 1024 ** 3}[m.group(2).lower()]


def cmd_run(args) -> int:
    model = Model(Path(args.registry))
    exp_path = Path(args.experiment).resolve()
    exp, exp_hash = load_experiment(exp_path, model)
    toolkits = args.toolkits.split(",")
    levels = args.levels.split(",") if args.levels else list(exp["levels"])
    members = args.members.split(",") if args.members else [m["id"] for m in exp["members"]]
    out = Path(args.out).resolve() if args.out else model.dir / "runs" / exp["experiment"].replace("/", "-")
    jobs = plan_jobs(exp_path, exp, model, toolkits, levels, members, out)
    out.mkdir(parents=True, exist_ok=True)
    runtime = records.docker_runtime() if args.runtime == "docker" else None
    if args.runtime == "docker" and runtime is None:
        raise SystemExit("--runtime docker: the Docker daemon does not answer; run under a shell in the docker group")
    uv = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    ctx = {"model": model, "runtime": args.runtime, "run_id": out.name, "repo": records.repository(model.root),
           "where": records.machine(runtime or "none"), "uv_version": uv.stdout.strip() if uv.returncode == 0 else "uv",
           "recorder": {"name": "wg1core runner", "version": VERSION},
           "experiment": {"id": exp["experiment"], "sha256": exp_hash},
           "member_hashes": {m["id"]: canonical.model_hash(canonical.load_strict(
               (exp_path.parent / m["parameter_file"]).read_text(encoding="utf-8"))) for m in exp["members"]},
           "caps": {"cpus": args.cpus, "memory": args.memory, "memory_bytes": memory_bytes(args.memory),
                    "wall_seconds": args.wall_seconds}}
    for name in toolkits:
        tk, env = model.toolkits[name], model.toolkits[name]["environment"]
        if args.runtime == "docker":
            tk["image_id"] = build_image(tk, out, ctx)
            print(f"{name:6s} image {tk['image_id'][:19]}", flush=True)
        elif env is not None:
            sync = subprocess.run(["uv", "sync", "--quiet", "--project", str(env), "--frozen"], cwd=model.root)
            if sync.returncode:
                raise SystemExit(f"{name}: its environment could not be built from {model.rel(env)}/uv.lock")
    started = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
    # Each toolkit's first job runs before its others, so that what a toolkit compiles and caches on its first use is
    # written by one process.
    lead = list({j["toolkit"]: j for j in reversed(jobs)}.values())
    rest = [j for j in jobs if all(j is not k for k in lead)]
    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        for batch in (lead, rest):
            futures = {pool.submit(run_job, j, model.toolkits[j["toolkit"]], ctx): j for j in batch}
            for f in concurrent.futures.as_completed(futures):
                j, r = futures[f], f.result()
                outcomes.append((j, r))
                print(f"{j['toolkit']:6s} {j['member']:22s} {j['level']:7s} {'skipped' if r['skipped'] else r['status']}",
                      flush=True)
    order = {id(j): i for i, j in enumerate(jobs)}
    outcomes.sort(key=lambda p: order[id(p[0])])
    manifest = {
        "experiment": {"name": exp["experiment"], "file": model.rel(exp_path), "sha256": exp_hash},
        "members": [{k: m[k] for k in ("id", "parameter_file_sha256", "request_file_sha256")} for m in exp["members"]
                    if m["id"] in members],
        "levels": levels,
        "toolkits": {n: {"adapter": model.rel(model.toolkits[n]["adapter"]), "environment": environment_identity(model.toolkits[n], model),
                         "code_sha256": code_sha256(model.toolkits[n], model), "threads": model.toolkits[n]["threads"]} for n in toolkits},
        "model": model_commit(model),
        "core": {"name": "wg1core", "version": VERSION},
        "runtime": ctx["where"]["runtime"],
        "started": started,
        "jobs": [{"toolkit": j["toolkit"], "member": j["member"], "level": j["level"], "dir": model.rel(j["dir"]),
                  "status": r["status"], "skipped": "yes" if r["skipped"] else "no"} for j, r in outcomes],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    failed = [m for m in manifest["jobs"] if m["status"] != "ok"]
    print(f"{len(jobs)} jobs, {len(failed)} failed; the run is in {model.rel(out)}")
    return 1 if failed else 0


# Verification ---------------------------------------------------------------------------------------------------------

def carries(results: dict, quantity: str) -> bool:
    """Whether a results file holds a quantity, a path such as types[].kink, with a value in every item."""
    nodes = [results]
    for segment in quantity.split("."):
        key, every = (segment[:-2], True) if segment.endswith("[]") else (segment, False)
        nxt = []
        for node in nodes:
            if not isinstance(node, dict) or node.get(key) is None:
                return False
            value = node[key]
            if every:
                if not isinstance(value, list) or not value:
                    return False
                nxt += value
            else:
                nxt.append(value)
        nodes = nxt
    return True


def verify_job(job: dict, reports: list[str], model: Model) -> dict:
    """The model's verifier on one results file, or the results schema's validation when the model names none, and
    the experiment's reports."""
    results = job["dir"] / "results.json"
    if not results.is_file():
        return {"status": "no results file"}
    data = json.loads(results.read_text(encoding="utf-8"))
    if model.verifier:
        argv = [a.replace("{member}", str(job["parameter_file"])).replace("{results}", str(results)) for a in model.verifier]
        check = subprocess.run(argv, cwd=model.root, capture_output=True, text=True)
        lines = [ln for ln in (check.stdout + check.stderr).splitlines() if ln.strip()]
        code, last = check.returncode, (lines[-1].replace(str(model.root) + "/", "") if lines else "")
    elif model.results_schema is not None:
        errors = list(jsonschema.Draft202012Validator(model.results_schema).iter_errors(data))
        code, last = (1 if errors else 0), (f"{errors[0].json_path}: {errors[0].message}" if errors else "")
    else:
        code, last = 0, ""
    missing = [q for q in reports if not carries(data, q)]
    ok = code == 0 and not missing
    return {"status": "ok" if ok else "failed", "checker_exit_code": code, "checker": last, "missing_reports": missing}


def cmd_verify(args) -> int:
    model = Model(Path(args.registry))
    run = Path(args.run).resolve()
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    exp_path = model.root / manifest["experiment"]["file"]
    exp, exp_hash = load_experiment(exp_path, model)
    if exp_hash != manifest["experiment"]["sha256"]:
        raise SystemExit("the experiment file has changed since the run")
    jobs = plan_jobs(exp_path, exp, model, list(manifest["toolkits"]), manifest["levels"],
                     [m["id"] for m in manifest["members"]], run)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        verdicts = list(pool.map(lambda j: verify_job(j, exp["reports"], model), jobs))
    out = []
    for j, v in zip(jobs, verdicts):
        out.append({"toolkit": j["toolkit"], "member": j["member"], "level": j["level"], **v})
        print(f"{j['toolkit']:6s} {j['member']:22s} {j['level']:7s} {v['status']}"
              + (f"  missing: {', '.join(v['missing_reports'])}" if v.get("missing_reports") else "")
              + ("" if v["status"] == "ok" else f"  {v.get('checker', '')}"))
        record = j["dir"] / "record.json"
        if record.is_file():
            data = json.loads(record.read_text(encoding="utf-8"))
            verdict = {"verdict": "verified" if v["status"] == "ok" else "failed"}
            problems = [v["checker"]] if v.get("checker") and v["status"] != "ok" else []
            problems += [f"missing report {q}" for q in v.get("missing_reports", [])]
            if problems:
                verdict["problems"] = problems
            data["extensions"]["sce-wg-1"]["verification"] = verdict
            records.write(data, record)
    (run / "verification.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    failed = [v for v in out if v["status"] != "ok"]
    print(f"{len(out)} results files, {len(failed)} failed")
    return 1 if failed else 0


def cmd_register(args) -> int:
    """Copies a run's records into the registry: <registry>/<stamp>_<experiment>/<toolkit>_<member>_<level>.json
    for each job and <toolkit>_build.json for each build, each validated. A record's relative paths refer to the run
    folder it came from, named in its `run.id`."""
    model = Model(Path(args.registry))
    run = Path(args.run).resolve()
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    stamp = manifest["started"].replace(":", "-")[:16]
    name = manifest["experiment"]["name"].replace("/", "-")
    folder = (Path(args.registry_dir).resolve() if args.registry_dir else model.registry_dir) / f"{stamp}_{name}"
    folder.mkdir(parents=True, exist_ok=True)
    copied = 0
    for j in manifest["jobs"]:
        job_dir = Path(j["dir"]) if Path(j["dir"]).is_absolute() else model.root / j["dir"]
        record = job_dir / "record.json"
        if not record.is_file():
            print(f"{j['toolkit']:6s} {j['member']:22s} {j['level']:7s} no record")
            continue
        records.validate(json.loads(record.read_text(encoding="utf-8")))
        shutil.copyfile(record, folder / f"{j['toolkit']}_{j['member']}_{j['level']}.json")
        copied += 1
    for build in sorted(run.glob("*/build.json")):
        records.validate(json.loads(build.read_text(encoding="utf-8")))
        shutil.copyfile(build, folder / f"{build.parent.name}_build.json")
        copied += 1
    print(f"{copied} records registered in {model.rel(folder)}")
    return 0


def cmd_list(args) -> int:
    model = Model(Path(args.registry))
    print("experiments:")
    for p in sorted(model.experiments_dir.glob("**/experiment.yaml")):
        e = canonical.load_strict(p.read_text(encoding="utf-8"))
        print(f"  {e['experiment']:22s} {model.rel(p)}: {len(e['members'])} members, levels {', '.join(e['levels'])}")
    print("toolkits:")
    for name, tk in model.toolkits.items():
        env = environment_identity(tk, model)
        print(f"  {name:6s} {model.rel(tk['adapter'])}, levels {', '.join(tk['levels'])}"
              + (f", Python {env['python']} locked in {env['project']}" if env else ", the core's own Python"))
    return 0


def default_registry() -> str:
    for candidate in ("harness/toolkits.yaml", "toolkits.yaml"):
        if Path(candidate).is_file():
            return candidate
    return "harness/toolkits.yaml"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wg1core", description=__doc__.split("\n\n")[0])
    ap.add_argument("--registry", default=default_registry(),
                    help="the model repository's registry file (default: harness/toolkits.yaml under the current directory)")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    r = sub.add_parser("run")
    r.add_argument("experiment")
    r.add_argument("--toolkits", required=True)
    r.add_argument("--levels")
    r.add_argument("--members")
    r.add_argument("--jobs", type=int, default=4)
    r.add_argument("--out")
    r.add_argument("--runtime", choices=("uv", "docker"), default="uv",
                   help="uv: the adapter's project on this machine; docker: an image built from its Dockerfile")
    r.add_argument("--cpus", type=float, default=2.0, help="the CPU cap of each container (docker only)")
    r.add_argument("--memory", help="the memory cap of each container, such as 8g (docker only)")
    r.add_argument("--wall-seconds", type=float, help="the wall-time cap of each job; a job past it is a timeout")
    v = sub.add_parser("verify")
    v.add_argument("run")
    v.add_argument("--jobs", type=int, default=4)
    g = sub.add_parser("register")
    g.add_argument("run")
    g.add_argument("--registry-dir", help="where to register (default: the registry file's registry_dir, runs.registry beside it)")
    args = ap.parse_args(argv)
    return {"list": cmd_list, "run": cmd_run, "verify": cmd_verify, "register": cmd_register}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
