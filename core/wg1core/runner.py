"""The runner: every toolkit on an experiment's members and levels, the verification of every results file, and the
registry's records. The `wg1core` command.

    wg1core list
    wg1core run <experiment.yaml> --toolkits hark,dolo [--levels low,medium] [--members <id>,...] [--jobs 8] \\
        [--out <run folder>] [--runtime uv|docker] [--cpus 2] [--memory 8g] [--wall-seconds 3600]
    wg1core verify <run folder>
    wg1core compare <run folder>
    wg1core register <run folder>
    wg1core status

Every command reads a model repository's registry file, `--registry`, `harness/toolkits.yaml` under the current
directory by default. The file names the toolkits, each with its adapter, the command that starts it where that is
not `python <adapter>` (a list of words in which `{adapter}` stands once for the adapter's path, so that an adapter
may be written in any language), the files its runs depend on, its
environment, its stone, its levels, its thread cap and its kind, exact for an entry that evaluates a closed form and
numerical, the default, for one that approximates by a method, and under `model` what the core needs of the
repository: its
results schema, its source page's anchors, its experiments folder, its verifier, its registry folder and the
identity keys a results file and its reference must agree on (README.md).
The repository's root is the git top level of the registry file's folder.

`run` checks the experiment and refuses one with problems. It then runs one job for each toolkit, member and level,
in parallel, each through the toolkit's adapter: with `--runtime uv`, the default, in the adapter's uv project on this
machine; with `--runtime docker`, in an image built from the adapter's environment directory and run under the
container contract (the repository mounted read-only at /src, the job's folder at /out, no network, the thread cap, a
scratch /tmp, and the caps given). Each toolkit's first job runs alone before its others, so that one process writes
what the toolkit compiles and caches. A job writes into <run folder>/<toolkit>/<member>/<level>/, the folder named
for the level and never for its position, and leaves there
the adapter's log, `job.json`, its status and a fingerprint of everything its output depends on, and `record.json`,
its execution record for the registry. A job whose fingerprint is unchanged and whose results file exists is skipped.
A job of an adapter on contract 2 has two steps (`run_steps`): the solve, the adapter given the level's suggestions
and writing the toolkit's solution, method and settings files, in its environment or container; then the measure,
the model's bench on this machine, in the harness's environment, writing the results file from them, with its own
record, `measure.json`. Each step is skipped when its own fingerprint is unchanged.
With `--runtime docker` each toolkit's image is built first and its build record written as
<run folder>/<toolkit>/build.json. `manifest.json` in the run folder names every hash.

`verify` runs the model's verifier on every results file, or validates it against the results schema when the model
names none, checks that each carries the quantities the experiment's `reports` names, and writes `verification.json`
and each record's verdict. `compare` evaluates the experiment's checks on the run's results and every job's distances
from its member's reference, with the reference's error beside each, every entry's kind being the run's own as its
manifest states it, writing `comparison.json` and `comparison.md` in
the run folder, a report in each job's folder and each record's comparison block; its exit status is the checks' and
the comparison errors', never a distance's. `register` copies a run's records into the registry folder, one file per job and one per build, validating
each. `status` prints what the repository holds, running nothing: its runs of record with what their records say
(status.py), the table REMARK's catalog shows for a canonical model; its exit status is nonzero when the file of runs
of record or a record it names has a problem.
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
import signal as signals
import subprocess
import sys
import time
from pathlib import Path

import jsonschema
import yaml

from . import VERSION, canonical, identity, records
from . import experiment as experiments

THREAD_VARIABLES = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
OUTPUTS = ("results.json", "methods.yaml", "settings.yaml")       # what an adapter on contract 1 writes
SOLVE_OUTPUTS = ("solution.json", "methods.yaml", "settings.yaml")  # what an adapter on contract 2 writes
MEASURE_OUTPUTS = ("results.json",)                                 # what the model's bench writes from them
SUGGESTIONS = "suggestions.yaml"  # the level's suggestions, which a contract-2 adapter is given
BENCH_FILE = "bench.yaml"         # the bench's settings at the level, which the bench is given
IMAGE_PREFIX = "sce-wg-1"
TOOLKIT_KEYS = {"adapter", "command", "contract", "code", "environment", "stone", "levels", "threads", "kind"}
# An adapter's contract: 1, it writes the results file itself; 2, it writes the toolkit's solution, which the model's
# bench measures in the harness's environment, outside the toolkit's container, writing the results file.
CONTRACTS = (1, 2)
KINDS = ("exact", "numerical")  # how an entry obtains its solution; numerical when the registry file states none
# An adapter's command: the words that start it, `{adapter}` standing once, as a word of its own, for the adapter's path.
# A command whose first word is `python` runs in the adapter's environment; any other runs as it is given.
ADAPTER = "{adapter}"
DEFAULT_COMMAND = ("python", ADAPTER)
MODEL_KEYS = {"results_schema", "anchors", "experiments", "verifier", "registry_dir", "identity", "solution_schema",
              "suggestions_schema", "bench"}
BENCH_KEYS = {"script", "code", "environment", "command"}
SCRIPT = "{script}"  # the bench's script, in a stated command of the bench
REGISTRY_FILES = ("harness/toolkits.yaml", "toolkits.yaml")
# Linux's signal numbers, by which a container's exit code of 128 and a number names a signal, whatever the host's are:
# on macOS, 10 is SIGBUS and 30 SIGUSR1.
LINUX_SIGNALS = dict(enumerate(
    "SIGHUP SIGINT SIGQUIT SIGILL SIGTRAP SIGABRT SIGBUS SIGFPE SIGKILL SIGUSR1 SIGSEGV SIGUSR2 SIGPIPE SIGALRM "
    "SIGTERM SIGSTKFLT SIGCHLD SIGCONT SIGSTOP SIGTSTP SIGTTIN SIGTTOU SIGURG SIGXCPU SIGXFSZ SIGVTALRM SIGPROF "
    "SIGWINCH SIGIO SIGPWR SIGSYS".split(), start=1))


def signal_name(number: int, linux: bool) -> str:
    """A signal's name, `SIGKILL`, by Linux's numbering for a container and the host's for a process the core started;
    `signal <number>` for one without a name, as every signal was recorded before, which a reader still accepts."""
    if linux:
        name = LINUX_SIGNALS.get(number)
    else:
        try:
            name = signals.Signals(number).name
        except ValueError:
            name = None
    return name or f"signal {number}"


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
        self.anchors = self._anchors(m.get("anchors"))
        self.experiments_dir = (self.dir / m["experiments"]).resolve() if m.get("experiments") else self.root
        self.verifier = [str(a) for a in m["verifier"]] if m.get("verifier") else None
        self.registry_dir = (self.dir / m.get("registry_dir", "runs.registry")).resolve()
        self.identity = [str(k) for k in m.get("identity", [])]
        self.solution_schema = self._json(m.get("solution_schema"))
        self.suggestions_schema = self._json(m.get("suggestions_schema"))
        self.bench = self._bench(m.get("bench"))
        self.toolkits = self._toolkits(raw.get("toolkits") or {})

    def _json(self, rel) -> dict | None:
        return json.loads((self.dir / str(rel)).resolve().read_text(encoding="utf-8")) if rel else None

    def _files(self, patterns: list[str]) -> list[Path]:
        """The files some patterns name, relative to the registry file's folder; files named test_* are left out."""
        files = set()
        for pattern in patterns:
            for f in glob.glob(str(self.dir / pattern)):
                if not Path(f).name.startswith("test_"):
                    files.add(Path(f).resolve())
        return sorted(files)

    def _bench(self, raw) -> dict | None:
        """The model's bench, which measures the solutions of adapters on contract 2: its script, the files its
        measurements depend on besides it, its environment, and its command where that is not the default."""
        if raw is None:
            return None
        if not isinstance(raw, dict) or set(raw) - BENCH_KEYS or "script" not in raw:
            raise SystemExit(f"{self.file.name}: model: bench: a script, with code, environment and command at most")
        stated = raw.get("command")
        if stated is not None and not (isinstance(stated, list) and stated and all(isinstance(w, str) and w for w in stated)
                                       and stated.count(SCRIPT) == 1):
            raise SystemExit(f"{self.file.name}: model: bench: command is a list of words, {SCRIPT} standing once as a "
                             f"word of its own for the bench's script")
        return {"script": (self.dir / raw["script"]).resolve(), "command": list(stated) if stated is not None else None,
                "environment": (self.dir / raw["environment"]).resolve() if raw.get("environment") else None,
                "code": self._files(list(raw.get("code", [])) + [raw["script"]])}

    def _anchors(self, raw) -> dict[str, set[str]] | None:
        """Each source's anchors by its key in an experiment's `sources`. The registry file names one file, BST's, or a
        file per source key; a file that is not there leaves its source unchecked, as before."""
        if not raw:
            return None
        files = raw if isinstance(raw, dict) else {"bst": raw}
        out = {}
        for key, rel in files.items():
            path = (self.dir / str(rel)).resolve()
            if path.is_file():
                out[str(key)] = experiments.read_anchors(path)
        return out or None

    def _toolkits(self, raw: dict) -> dict:
        out = {}
        for name, entry in raw.items():
            unknown = set(entry) - TOOLKIT_KEYS
            contract = entry.get("contract", 1)
            if contract not in CONTRACTS:
                raise SystemExit(f"{self.file.name}: {name}: contract is {contract!r}; it is 1 or 2")
            if unknown or "adapter" not in entry or ("levels" in entry) != (contract == 1):
                raise SystemExit(f"{self.file.name}: {name}: unknown keys {sorted(unknown)} or no adapter or levels "
                                 f"(an adapter on contract 1 states its levels; on contract 2 the experiment names them)")
            if entry.get("kind", "numerical") not in KINDS:
                raise SystemExit(f"{self.file.name}: {name}: kind is {entry['kind']!r}; it is one of {', '.join(KINDS)}")
            stated = entry.get("command")
            if stated is not None and not (isinstance(stated, list) and stated and all(isinstance(w, str) and w for w in stated)
                                           and stated.count(ADAPTER) == 1):
                raise SystemExit(f"{self.file.name}: {name}: command is a list of words, {ADAPTER} standing once as a "
                                 f"word of its own for the adapter's path")
            tk = {"name": name, "adapter": (self.dir / entry["adapter"]).resolve(), "kind": entry.get("kind", "numerical"),
                  "levels": dict(entry.get("levels") or {}), "threads": int(entry.get("threads", 2)),
                  "command": list(stated) if stated is not None else None, "contract": contract}
            tk["environment"] = (self.dir / entry["environment"]).resolve() if entry.get("environment") else None
            tk["stone"] = (self.dir / entry["stone"]).resolve() if entry.get("stone") else None
            tk["code"] = self._files(list(entry.get("code", [])) + [entry["adapter"]])
            out[name] = tk
        return out

    def rel(self, path: Path) -> str:
        """A path relative to the repository's root, for the records; absolute if it lies outside."""
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return str(Path(path).resolve())


def project_identity(env: Path | None, model: Model) -> dict | None:
    """What identifies a uv project: its lock file and interpreter."""
    if env is None:
        return None
    version = env / ".python-version"
    return {"project": model.rel(env), "lock_sha256": sha256_file(env / "uv.lock") if (env / "uv.lock").is_file() else None,
            "python": version.read_text(encoding="utf-8").strip() if version.is_file() else None}


def environment_identity(tk: dict, model: Model) -> dict | None:
    """What identifies a toolkit's environment: its lock file and interpreter, its Dockerfile when it has one, and
    the image it was built into when the run is in containers."""
    env = tk["environment"]
    out = project_identity(env, model)
    if out is None:
        return None
    if (env / "Dockerfile").is_file():
        out["dockerfile_sha256"] = sha256_file(env / "Dockerfile")
    if tk.get("image_id"):
        out["image_id"] = tk["image_id"]
    return out


def files_sha256(files: list[Path], model: Model) -> str:
    h = hashlib.sha256()
    for f in files:
        h.update(model.rel(f).encode() + b"\0" + Path(f).read_bytes() + b"\0")
    return h.hexdigest()


def code_sha256(tk: dict, model: Model) -> str:
    return files_sha256(tk["code"], model)


# The experiment and the jobs ------------------------------------------------------------------------------------------

def load_experiment(path: Path, model: Model) -> tuple[dict, str]:
    """The experiment and its hash; refuses one with problems."""
    path = Path(path).resolve()
    data = canonical.load_strict(path.read_text(encoding="utf-8"))
    problems = experiments.problems(data, path.parent, model.results_schema, model.anchors, model.suggestions_schema)
    if problems:
        raise SystemExit("the experiment has problems:\n  " + "\n  ".join(problems))
    return data, canonical.model_hash(data)


def plan_jobs(exp_path: Path, exp: dict, model: Model, toolkits: list[str], levels: list[str], members: list[str],
              out: Path) -> list[dict]:
    folder = Path(exp_path).resolve().parent
    by_id = {m["id"]: m for m in exp["members"]}
    unknown = [m for m in members if m not in by_id] + [t for t in toolkits if t not in model.toolkits]
    unknown += [lv for lv in levels if lv not in exp["levels"]]
    if unknown:
        raise SystemExit(f"unknown toolkit, member or level: {unknown}")
    jobs = []
    for name in toolkits:
        tk = model.toolkits[name]
        missing = [lv for lv in levels if lv not in tk["levels"]] if tk["contract"] == 1 else []
        if missing:
            raise SystemExit(f"{name} offers no level {missing}")
        if tk["contract"] == 2 and model.bench is None:
            raise SystemExit(f"{name} is on contract 2, and the registry file's model block names no bench to measure "
                             f"its solutions")
        for mid in members:
            m = by_id[mid]
            for lv in levels:
                job = {"toolkit": name, "kind": tk["kind"], "member": mid, "level": lv, "contract": tk["contract"],
                       "level_arg": tk["levels"].get(lv),
                       "parameter_file": (folder / m["parameter_file"]).resolve(),
                       "request_file": (folder / m["request_file"]).resolve(),
                       "parameter_file_sha256": m["parameter_file_sha256"],
                       "request_file_sha256": m["request_file_sha256"],
                       "dir": out / name / mid / lv}
                if tk["contract"] == 2:
                    job["suggestions"] = {"level": lv, "suggested": (exp.get("suggestions") or {}).get(lv, {})}
                    job["bench_settings"] = bench_settings(exp, lv)
                jobs.append(job)
    return jobs


def merged(base: dict, over: dict) -> dict:
    """`over` laid on `base`, key by key, mappings merged and anything else replaced."""
    out = dict(base)
    for k, v in over.items():
        out[k] = merged(out[k], v) if isinstance(out.get(k), dict) and isinstance(v, dict) else v
    return out


def bench_settings(exp: dict, level: str) -> dict:
    """The bench's settings at a level, as the bench is given them: the experiment's `settings` with the level's
    overrides, the level's name, and the bench's version where the experiment states one."""
    b = exp.get("bench") or {}
    out = {"level": level, "settings": merged(b.get("settings") or {}, (b.get("levels") or {}).get(level, {}))}
    if b.get("version"):
        out["version"] = b["version"]
    return out


def fingerprint(job: dict, tk: dict, model: Model) -> dict:
    """Everything a job's output depends on that the harness can name. An entry's kind is named only when it is not
    the default, so that a numerical entry's fingerprint is what it was before entries had kinds, and an entry newly
    stated to be exact is run again, its record then saying so."""
    out = {"toolkit": tk["name"], "member": job["member"], "level": job["level"], "level_arg": job["level_arg"],
           "parameter_file_sha256": job["parameter_file_sha256"], "request_file_sha256": job["request_file_sha256"],
           "environment": environment_identity(tk, model), "code_sha256": code_sha256(tk, model), "threads": tk["threads"]}
    if tk["kind"] != "numerical":
        out["kind"] = tk["kind"]
    if tk["command"] is not None:
        out["command"] = tk["command"]
    if job.get("contract") == 2:
        out.pop("level_arg")
        out.update({"contract": 2, "suggestions_sha256": canonical.model_hash(job["suggestions"])})
    return out


def measure_fingerprint(job: dict, model: Model) -> dict:
    """Everything a measure step's output depends on that the harness can name: the solve's files, the bench's code,
    command and environment, the settings the experiment gives it at the level, and the member and request. A change
    to the bench re-measures a job without solving it again."""
    b = model.bench
    out = {"solution": records.outputs(job["dir"], SOLVE_OUTPUTS), "bench_script": model.rel(b["script"]),
           "bench_code_sha256": files_sha256(b["code"], model),
           "bench_settings_sha256": canonical.model_hash(job["bench_settings"]),
           "bench_environment": project_identity(b["environment"], model),
           "parameter_file_sha256": job["parameter_file_sha256"], "request_file_sha256": job["request_file_sha256"]}
    if b["command"] is not None:
        out["bench_command"] = b["command"]
    return out


def adapter_arguments(job: dict, out_dir: str, in_container: bool, model: Model) -> list[str]:
    """The adapter contract's arguments: the parameter file, --out, --level and --request; on contract 2,
    --suggest and the suggestions file in the job's folder in place of --level."""
    p = model.rel(job["parameter_file"]) if in_container else str(job["parameter_file"])
    r = model.rel(job["request_file"]) if in_container else str(job["request_file"])
    if job.get("contract") == 2:
        return [p, "--out", out_dir, "--suggest", f"{out_dir}/{SUGGESTIONS}", "--request", r]
    return [p, "--out", out_dir, "--level", str(job["level_arg"]), "--request", r]


def adapter_words(tk: dict, adapter: str) -> list[str]:
    """The adapter's command with its path put in: the registry's `command`, or `python <adapter>`."""
    return [adapter if w == ADAPTER else w for w in (tk["command"] or DEFAULT_COMMAND)]


def command(job: dict, tk: dict, model: Model) -> list[str]:
    """The job on this machine: a command that starts with `python` in the adapter's uv project, or in the core's own
    Python where the adapter states no environment; any other command as the registry file gives it."""
    words = adapter_words(tk, str(tk["adapter"])) + adapter_arguments(job, str(job["dir"]), False, model)
    if words[0] != "python":
        return words
    if tk["environment"] is None:
        return [sys.executable] + words[1:]
    return ["uv", "run", "--quiet", "--project", str(tk["environment"]), "--frozen"] + words


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
            "--workdir", "/src", tk["image_id"]]
    return cmd + adapter_words(tk, model.rel(tk["adapter"])) + adapter_arguments(job, "/out", True, model)


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


def toolkit_of(path: Path) -> dict:
    """The toolkit block a results or solution file reports, or nothing."""
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8")).get("toolkit", {}) or {}
        except (ValueError, AttributeError):
            return {}
    return {}


def job_fields(job: dict, tk: dict, ctx: dict) -> dict:
    """The model repository's fields every record of a job carries."""
    model = ctx["model"]
    return {"experiment": ctx["experiment"], "toolkit": tk["name"], "entry_kind": tk["kind"],
            "adapter": {"path": model.rel(tk["adapter"]), "code_sha256": code_sha256(tk, model)},
            "member": {"id": job["member"], "hash": ctx["member_hashes"][job["member"]],
                       "parameter_file_sha256": job["parameter_file_sha256"]},
            "request": {"sha256": job["request_file_sha256"]}, "level": job["level"]}


def execution_record(job: dict, tk: dict, ctx: dict, cmd: list[str], when: dict, exit_code: int,
                     termination: str, signal: str | None, step: str = "job") -> dict:
    """The record of a job of an adapter on contract 1, `step` job, or of the solve of one on contract 2, `step`
    solve: the adapter in the toolkit's environment or container."""
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
    solving = step == "solve"
    outcome = {"exit_code": exit_code, "termination": termination, "output_dir": ".",
               "outputs": records.outputs(d, SOLVE_OUTPUTS if solving else OUTPUTS), "log": "adapter.log"}
    if signal:
        outcome["signal"] = signal
    fields = job_fields(job, tk, ctx)
    hashes = {o["path"]: o["sha256"] for o in outcome["outputs"]}
    if solving:
        fields.update({"step": "solve", "contract": 2, "suggestions_sha256": canonical.model_hash(job["suggestions"])})
        if hashes.get("solution.json"):
            fields["solution_sha256"] = hashes["solution.json"]
    else:
        fields["results_sha256"] = hashes.get("results.json", "0" * 64)
        fields["verification"] = {"verdict": "not run"}
    for name, key in (("settings.yaml", "settings_sha256"), ("methods.yaml", "methods_sha256")):
        if hashes.get(name):
            fields[key] = hashes[name]
    toolkit_block = toolkit_of(d / ("solution.json" if solving else "results.json"))
    if toolkit_block.get("version"):
        fields["toolkit_version"] = " ".join(str(toolkit_block[k]) for k in ("name", "version", "commit") if toolkit_block.get(k))
    fields["core_version"] = VERSION
    adapter = model.rel(tk["adapter"]) if in_container else str(tk["adapter"])
    record = {"$schema": records.MODEL_SCHEMA_ID, "record_version": records.RECORD_VERSION, "kind": "execution",
              "recorder": ctx["recorder"], "run": {"id": ctx["run_id"], "manifest": "../../../manifest.json"},
              "repository": ctx["repo"], "script": model.rel(tk["adapter"]), "arguments": cmd[cmd.index(adapter) + 1:],
              "environment": environment, "where": ctx["where"], "conditions": conditions, "when": when,
              "outcome": outcome, "extensions": {"sce-wg-1": fields}}
    if in_container:
        record["image"] = {"id": tk["image_id"], "build_record": "../../build.json"}
    return record


def measure_record(job: dict, tk: dict, ctx: dict, cmd: list[str], when: dict, exit_code: int,
                   termination: str, signal: str | None) -> dict:
    """The record of a job's measure step: the model's bench, run on this machine in the harness's environment and
    outside any container, its inputs the solve's files and the bench's settings, its output the results file."""
    model, d, b = ctx["model"], job["dir"], ctx["model"].bench
    env_path = model.rel(b["environment"]) if b["environment"] is not None else model.rel(model.dir)
    environment = records.environment(model.root, ctx["repo"], env_path, "host-uv", ctx["uv_version"])
    conditions = {"thread_variables": {v: str(tk["threads"]) for v in THREAD_VARIABLES}}
    if ctx["caps"].get("wall_seconds"):
        conditions["wall_seconds"] = ctx["caps"]["wall_seconds"]
    outcome = {"exit_code": exit_code, "termination": termination, "output_dir": ".",
               "outputs": records.outputs(d, MEASURE_OUTPUTS), "log": "bench.log"}
    if signal:
        outcome["signal"] = signal
    inputs = records.outputs(d, SOLVE_OUTPUTS + (BENCH_FILE,))
    held = {i["path"]: i["sha256"] for i in inputs}
    fields = job_fields(job, tk, ctx)
    fields.update({"step": "measure", "contract": 2, "suggestions_sha256": canonical.model_hash(job["suggestions"]),
                   "inputs": inputs,
                   "bench": {"script": model.rel(b["script"]), "code_sha256": files_sha256(b["code"], model),
                             "settings_sha256": canonical.model_hash(job["bench_settings"])},
                   "results_sha256": next((o["sha256"] for o in outcome["outputs"] if o["path"] == "results.json"), "0" * 64),
                   "verification": {"verdict": "not run"}})
    for name, key in (("solution.json", "solution_sha256"), ("settings.yaml", "settings_sha256"),
                      ("methods.yaml", "methods_sha256")):
        if held.get(name):
            fields[key] = held[name]
    toolkit_block = toolkit_of(d / "results.json")
    if toolkit_block.get("version"):
        fields["toolkit_version"] = " ".join(str(toolkit_block[k]) for k in ("name", "version", "commit") if toolkit_block.get(k))
    fields["core_version"] = VERSION
    script = str(b["script"])
    return {"$schema": records.MODEL_SCHEMA_ID, "record_version": records.RECORD_VERSION, "kind": "execution",
            "recorder": ctx["recorder"], "run": {"id": ctx["run_id"], "manifest": "../../../manifest.json"},
            "repository": ctx["repo"], "script": model.rel(b["script"]), "arguments": cmd[cmd.index(script) + 1:],
            "environment": environment, "where": {**ctx["where"], "runtime": "none"}, "conditions": conditions,
            "when": when, "outcome": outcome, "extensions": {"sce-wg-1": fields}}


def execute(cmd: list[str], threads: int, ctx: dict, log_path: Path, name: str | None = None):
    """One process of a job, run from the repository's root under the thread cap and the wall-time cap, its output
    in `log_path`: (the exit code, how it ended, its signal or None, when). `name` is the container's, for a process
    run in one, which is then inspected for how it ended and removed."""
    in_container = name is not None
    env = os.environ.copy()
    env.update({v: str(threads) for v in THREAD_VARIABLES})
    termination, signal = "exited", None
    started, clock = records.now(), time.perf_counter()
    with open(log_path, "w", encoding="utf-8") as log:
        try:
            code = subprocess.run(cmd, cwd=ctx["model"].root, env=env, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=ctx["caps"].get("wall_seconds")).returncode
        except subprocess.TimeoutExpired:
            code, termination = 124, "timeout"
            if in_container:
                docker("kill", name, check=False)
    if not in_container and termination == "exited" and code < 0:
        termination, signal = "signal", signal_name(-code, linux=False)  # a process the core started, ended by a signal
    when = {"started": started, "ended": records.now(), "duration_seconds": round(time.perf_counter() - clock, 3)}
    if in_container:
        state = docker("inspect", "--format", "{{.State.ExitCode}} {{.State.OOMKilled}}", name, check=False)
        if state.returncode == 0:
            exit_in, oom = state.stdout.split()
            if termination == "exited":
                code = int(exit_in)
                if oom == "true":
                    termination = "oom"
                elif code > 128:
                    termination, signal = "signal", signal_name(code - 128, linux=True)
        docker("rm", "--force", name, check=False)
    return code, termination, signal, when


def shown_command(cmd: list[str], in_container: bool, model: Model) -> list[str]:
    """A command as job.json shows it: paths in the repository relative to its root, the core's own Python as python."""
    shown = [model.rel(Path(c)) if c.startswith("/") else c for c in cmd]
    if not in_container and cmd[0] == sys.executable:
        shown[0] = "python"
    return shown


def run_job(job: dict, tk: dict, ctx: dict) -> dict:
    if job.get("contract") == 2:
        return run_steps(job, tk, ctx)
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
    in_container = ctx["runtime"] == "docker"
    cmd = container_command(job, tk, ctx) if in_container else command(job, tk, model)
    code, termination, signal, when = execute(cmd, tk["threads"], ctx, d / "adapter.log",
                                              container_name(job, ctx["run_id"]) if in_container else None)
    ok = code == 0 and (d / "results.json").is_file()
    shown = shown_command(cmd, in_container, model)
    out = {"status": "ok" if ok else "failed", "exit_code": code, "command": shown, "fingerprint": fp}
    record.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    records.write(execution_record(job, tk, ctx, shown if in_container else cmd, when, code, termination, signal),
                  d / "record.json")
    return {**out, "skipped": False}


def solution_problems(d: Path, model: Model) -> list[str]:
    """What the model's solution schema says of a job's solution file: nothing where the model names no schema."""
    path = d / "solution.json"
    if model.solution_schema is None or not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        return [f"solution.json is not JSON: {e}"]
    errors = jsonschema.Draft202012Validator(model.solution_schema).iter_errors(data)
    return [f"solution.json: {e.json_path}: {e.message}" for e in errors][:5]


def bench_command(job: dict, model: Model) -> list[str]:
    """A measure step's command: the bench's stated command with its places filled, or by default its script in its
    environment's uv project, the core's own Python where it names none, given the parameter file, --request,
    --solution (the job's folder, where the solve's files are), --bench (its settings at the level) and --out."""
    b, d = model.bench, job["dir"]
    places = {SCRIPT: str(b["script"]), "{member}": str(job["parameter_file"]), "{request}": str(job["request_file"]),
              "{solution}": str(d), "{bench}": str(d / BENCH_FILE), "{out}": str(d)}
    if b["command"] is not None:
        return [places.get(w, w) for w in b["command"]]
    words = [places[SCRIPT], places["{member}"], "--request", places["{request}"], "--solution", places["{solution}"],
             "--bench", places["{bench}"], "--out", places["{out}"]]
    if b["environment"] is None:
        return [sys.executable] + words
    return ["uv", "run", "--quiet", "--project", str(b["environment"]), "--frozen", "python"] + words


def run_steps(job: dict, tk: dict, ctx: dict) -> dict:
    """A job of an adapter on contract 2, in two steps, each skipped when its own fingerprint is unchanged. The solve:
    the adapter, in the toolkit's environment or container, given the level's suggestions, writes the solution,
    method and settings files, and the solution is checked against the model's solution schema; its record is
    `record.json`. The measure: the model's bench, on this machine in the harness's environment, outside the
    container, writes the results file from them; its record is `measure.json`. A changed bench re-measures without
    solving again; changed suggestions solve again."""
    model, d = ctx["model"], job["dir"]
    fp = fingerprint(job, tk, model)
    jobfile = d / "job.json"
    old = json.loads(jobfile.read_text(encoding="utf-8")) if jobfile.is_file() else {}
    solve = old.get("solve") or {}
    solve_skipped = (solve.get("status") == "ok" and old.get("fingerprint") == fp
                     and (d / "solution.json").is_file() and (d / "record.json").is_file())
    d.mkdir(parents=True, exist_ok=True)
    if not solve_skipped:
        for stale in SOLVE_OUTPUTS + MEASURE_OUTPUTS + ("job.json", "record.json", "measure.json", SUGGESTIONS, BENCH_FILE):
            (d / stale).unlink(missing_ok=True)
        (d / SUGGESTIONS).write_text(yaml.safe_dump(job["suggestions"], sort_keys=False, allow_unicode=True),
                                     encoding="utf-8")
        in_container = ctx["runtime"] == "docker"
        cmd = container_command(job, tk, ctx) if in_container else command(job, tk, model)
        code, termination, signal, when = execute(cmd, tk["threads"], ctx, d / "adapter.log",
                                                  container_name(job, ctx["run_id"]) if in_container else None)
        problems = solution_problems(d, model) if code == 0 else []
        ok = code == 0 and (d / "solution.json").is_file() and not problems
        shown = shown_command(cmd, in_container, model)
        solve = {"status": "ok" if ok else "failed", "exit_code": code, "command": shown}
        if problems:
            solve["problems"] = problems
        records.write(execution_record(job, tk, ctx, shown if in_container else cmd, when, code, termination, signal,
                                       step="solve"), d / "record.json")
    measure, measure_skipped = {"status": "not run"}, False
    if solve["status"] == "ok":
        (d / BENCH_FILE).write_text(yaml.safe_dump(job["bench_settings"], sort_keys=False, allow_unicode=True),
                                    encoding="utf-8")
        mfp = measure_fingerprint(job, model)
        held = old.get("measure") or {}
        measure_skipped = (held.get("status") == "ok" and held.get("fingerprint") == mfp
                           and (d / "results.json").is_file() and (d / "measure.json").is_file())
        if measure_skipped:
            measure = held
        else:
            for stale in MEASURE_OUTPUTS + ("measure.json",):
                (d / stale).unlink(missing_ok=True)
            cmd = bench_command(job, model)
            code, termination, signal, when = execute(cmd, tk["threads"], ctx, d / "bench.log")
            ok = code == 0 and (d / "results.json").is_file()
            measure = {"status": "ok" if ok else "failed", "exit_code": code,
                       "command": shown_command(cmd, False, model), "fingerprint": mfp}
            records.write(measure_record(job, tk, ctx, cmd, when, code, termination, signal), d / "measure.json")
    out = {"status": "ok" if solve["status"] == "ok" and measure["status"] == "ok" else "failed",
           "exit_code": solve["exit_code"], "command": solve["command"], "fingerprint": fp, "solve": solve,
           "measure": measure}
    jobfile.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    return {**out, "skipped": solve_skipped and measure_skipped,
            "steps": {"solve": "skipped" if solve_skipped else solve["status"],
                      "measure": "skipped" if measure_skipped else measure["status"]}}


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
    repo = records.repository(model.root)
    if not records.remote_is_named(repo["remote"]):
        raise SystemExit(f"origin is {repo['remote']!r}, which a record cannot name; set it to the repository's https or "
                         "ssh address before running, since every record names the repository by its remote")
    out.mkdir(parents=True, exist_ok=True)
    runtime = records.docker_runtime() if args.runtime == "docker" else None
    if args.runtime == "docker" and runtime is None:
        raise SystemExit("--runtime docker: the Docker daemon does not answer; run under a shell in the docker group")
    uv = subprocess.run(["uv", "--version"], capture_output=True, text=True)
    ctx = {"model": model, "runtime": args.runtime, "run_id": out.name, "repo": repo,
           "where": records.machine(runtime or "none"), "uv_version": uv.stdout.strip() if uv.returncode == 0 else "uv",
           "recorder": {**identity(), "name": "wg1core runner"},
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
    measured = [n for n in toolkits if model.toolkits[n]["contract"] == 2]
    bench_env = model.bench["environment"] if measured else None
    if bench_env is not None and (bench_env / "uv.lock").is_file():
        sync = subprocess.run(["uv", "sync", "--quiet", "--project", str(bench_env), "--frozen"], cwd=model.root)
        if sync.returncode:
            raise SystemExit(f"the bench's environment could not be built from {model.rel(bench_env)}/uv.lock")
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
                said = "skipped" if r["skipped"] else r["status"]
                if r.get("steps") and not r["skipped"]:
                    said += f" (solve {r['steps']['solve']}, measure {r['steps']['measure']})"
                print(f"{j['toolkit']:6s} {j['member']:22s} {j['level']:7s} {said}", flush=True)
    order = {id(j): i for i, j in enumerate(jobs)}
    outcomes.sort(key=lambda p: order[id(p[0])])
    manifest = {
        "experiment": {"name": exp["experiment"], "file": model.rel(exp_path), "sha256": exp_hash},
        "members": [{k: m[k] for k in ("id", "parameter_file_sha256", "request_file_sha256")} for m in exp["members"]
                    if m["id"] in members],
        "levels": levels,
        "toolkits": {n: {"adapter": model.rel(model.toolkits[n]["adapter"]), "kind": model.toolkits[n]["kind"],
                         **({"command": model.toolkits[n]["command"]} if model.toolkits[n]["command"] else {}),
                         **({"contract": 2} if model.toolkits[n]["contract"] == 2 else {}),
                         "environment": environment_identity(model.toolkits[n], model),
                         "code_sha256": code_sha256(model.toolkits[n], model), "threads": model.toolkits[n]["threads"]} for n in toolkits},
        "model": model_commit(model),
        "core": identity(),
        "runtime": ctx["where"]["runtime"],
        "started": started,
        "jobs": [{"toolkit": j["toolkit"], "member": j["member"], "level": j["level"], "dir": model.rel(j["dir"]),
                  "status": r["status"], "skipped": "yes" if r["skipped"] else "no",
                  **({"steps": r["steps"]} if r.get("steps") else {})} for j, r in outcomes],
    }
    if measured:
        b = model.bench
        manifest["bench"] = {"script": model.rel(b["script"]), "code_sha256": files_sha256(b["code"], model),
                             "environment": project_identity(b["environment"], model),
                             **({"command": b["command"]} if b["command"] is not None else {})}
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
        record = records.results_record(j["dir"])
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
    for each job, or for its solve under contract 2 with <toolkit>_<member>_<level>_measure.json for its measure, and
    <toolkit>_build.json for each build, each validated. A record's relative paths refer to the run folder it came
    from, named in its `run.id`."""
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
        measure = job_dir / "measure.json"
        if measure.is_file():
            records.validate(json.loads(measure.read_text(encoding="utf-8")))
            shutil.copyfile(measure, folder / f"{j['toolkit']}_{j['member']}_{j['level']}_measure.json")
            copied += 1
    for build in sorted(run.glob("*/build.json")):
        records.validate(json.loads(build.read_text(encoding="utf-8")))
        shutil.copyfile(build, folder / f"{build.parent.name}_build.json")
        copied += 1
    print(f"{copied} records registered in {model.rel(folder)}")
    return 0


def cmd_compare(args) -> int:
    """The experiment's checks on a run's results, and every job's distances from its member's reference; the exit
    status is the checks' alone. An entry's kind is the run's own, as its manifest states it, numerical where a
    manifest written before entries had kinds states none."""
    from . import comparator

    model = Model(Path(args.registry))
    run = Path(args.run).resolve()
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    exp_path = model.root / manifest["experiment"]["file"]
    exp, exp_hash = load_experiment(exp_path, model)
    if exp_hash != manifest["experiment"]["sha256"]:
        raise SystemExit("the experiment file has changed since the run")
    jobs = plan_jobs(exp_path, exp, model, list(manifest["toolkits"]), manifest["levels"],
                     [m["id"] for m in manifest["members"]], run)
    for j in jobs:
        j["kind"] = manifest["toolkits"][j["toolkit"]].get("kind", "numerical")
    try:
        report = comparator.run_comparison(exp, exp_path, jobs, run, model.identity)
    except ValueError as e:  # a metric's function that cannot be imported: a refusal, as an experiment with problems is
        raise SystemExit(str(e))
    comparator.write_outputs(report, jobs, run)
    for c in report["checks"]:
        print(f"{c['id']:32s} {c['verdict']}" + (f"  {c['errors'][0]}" if c["errors"] else ""))
    computed = [j for j in report["reference"] if j["status"] == "computed"]
    in_error = [j for j in report["reference"] if j["status"] == "error"]
    for j in in_error:
        print(f"{j['toolkit']:6s} {j['member']:22s} {j['level']:7s} comparison error: {j['reason']}")
    print(f"{len(report['checks'])} checks; distances from the reference computed for {len(computed)} of {len(report['reference'])} jobs,"
          f" {len(in_error)} in error; the report is in {model.rel(run / 'comparison.md')}")
    return 1 if report["failed"] else 0


def cmd_list(args) -> int:
    model = Model(Path(args.registry))
    print("experiments:")
    for p in sorted(model.experiments_dir.glob("**/experiment.yaml")):
        e = canonical.load_strict(p.read_text(encoding="utf-8"))
        print(f"  {e['experiment']:22s} {model.rel(p)}: {len(e['members'])} members, levels {', '.join(e['levels'])}")
    print("toolkits:")
    for name, tk in model.toolkits.items():
        env = environment_identity(tk, model)
        levels = (f"levels {', '.join(tk['levels'])}" if tk["contract"] == 1
                  else "contract 2, at the experiment's levels, measured by the model's bench")
        print(f"  {name:6s} {model.rel(tk['adapter'])}, {levels}"
              + (f", Python {env['python']} locked in {env['project']}" if env else ", the core's own Python"))
    return 0


def cmd_status(args) -> int:
    """What the repository holds, as REMARK's status table shows it; nothing is run."""
    from . import status

    try:
        found = status.report(Path(args.registry))
    except ValueError as e:
        raise SystemExit(str(e))
    print(found["summary"], "", found["table"], sep="\n", end="")
    return 1 if found["data"]["problems"] else 0


def default_registry() -> str:
    for candidate in REGISTRY_FILES:
        if Path(candidate).is_file():
            return candidate
    return REGISTRY_FILES[0]


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
    c = sub.add_parser("compare")
    c.add_argument("run")
    g = sub.add_parser("register")
    g.add_argument("run")
    g.add_argument("--registry-dir", help="where to register (default: the registry file's registry_dir, runs.registry beside it)")
    sub.add_parser("status")
    args = ap.parse_args(argv)
    return {"list": cmd_list, "run": cmd_run, "verify": cmd_verify, "compare": cmd_compare, "register": cmd_register,
            "status": cmd_status}[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
