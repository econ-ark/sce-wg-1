"""The core's tests, on a model repository of its own making: a tiny results schema, two members with their request
files, one experiment, a registry file with a stand-in toolkit, all committed in a temporary git repository with a
remote named and no network. The runner runs, the records validate, verification fills the verdicts, the registry is
written, the container command follows the contract, and the experiment checker catches what the validator cannot.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

import pytest
import yaml

from wg1core import canonical, experiment, records, runner

RESULTS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "required": ["toolkit", "types"],
    "properties": {
        "toolkit": {"type": "object", "required": ["name", "version"],
                    "properties": {"name": {"type": "string"}, "version": {"type": "string"}}},
        "types": {"type": "array", "minItems": 1, "items": {"$ref": "#/$defs/Type"}},
    },
    "$defs": {"Type": {"type": "object", "required": ["kink", "rule"],
                       "properties": {"kink": {"type": "number"},
                                      "rule": {"type": "object", "properties": {"c": {"type": "array", "items": {"type": "number"}}}}}}},
}

STUB_ADAPTER = textwrap.dedent('''
    """A stand-in toolkit: it takes the adapter contract's command line and writes a results file that the tiny
    results schema accepts, solving nothing. STUB_DROP names a key to leave out of every type."""
    import argparse, json, os
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("member"); ap.add_argument("--out", required=True); ap.add_argument("--level", required=True)
    ap.add_argument("--request", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    t = {"kink": 1.25 + 0.01 * int(a.level), "rule": {"c": [0.5, 0.75]}}
    t.pop(os.environ.get("STUB_DROP", ""), None)
    (out / "results.json").write_text(json.dumps({"toolkit": {"name": "stub", "version": "0.0"}, "types": [t]}))
    (out / "methods.yaml").write_text("policy: time-iteration\\n")
    (out / "settings.yaml").write_text(f"level: {a.level}\\n")
''')


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def model(tmp_path: Path) -> dict:
    """A tiny model repository, committed, with one experiment of two members and a stand-in toolkit."""
    root = tmp_path / "model"
    exp_dir, harness = root / "schemas" / "experiments" / "tiny", root / "harness"
    exp_dir.mkdir(parents=True)
    harness.mkdir()
    (root / "schemas" / "results.schema.json").write_text(json.dumps(RESULTS_SCHEMA, indent=1))
    members = []
    for mid, beta in (("m1", 0.9), ("m2", 0.95)):
        member = {"family": "tiny/1", "beta": beta}
        mh = canonical.model_hash(member)
        request = {"family": "tiny/1", "parameter_file_sha256": mh, "points": [1.0, 2.0]}
        (exp_dir / f"{mid}.yaml").write_text(yaml.safe_dump(member))
        (exp_dir / f"{mid}.request.yaml").write_text(yaml.safe_dump(request))
        members.append({"id": mid, "parameter_file": f"{mid}.yaml", "parameter_file_sha256": mh,
                        "request_file": f"{mid}.request.yaml", "request_file_sha256": canonical.model_hash(request)})
    exp = {"experiment": "tiny/1", "title": "A tiny experiment", "statement": "Two members at one level.",
           "members": members, "levels": ["low"], "reports": ["types[].kink", "types[].rule.c"],
           "checks": [{"id": "kinks_agree", "statement": "The kinks agree.", "compare": "members",
                       "quantity": "types[].kink", "metric": "max_abs_difference", "pairs": [["m1", "m2"]],
                       "expect": {"at_most": 1.0}}]}
    (exp_dir / "experiment.yaml").write_text(yaml.safe_dump(exp, sort_keys=False))
    (harness / "stub_adapter.py").write_text(STUB_ADAPTER)
    (harness / "toolkits.yaml").write_text(yaml.safe_dump({
        "model": {"results_schema": "../schemas/results.schema.json", "experiments": "../schemas/experiments",
                  "registry_dir": "runs.registry"},
        "toolkits": {"stub": {"adapter": "stub_adapter.py", "code": ["stub_adapter.py"],
                              "levels": {"low": 1, "medium": 2, "high": 3}, "threads": 1}}}))
    git(root, "init", "-q")
    git(root, "config", "user.email", "tests@example.invalid")
    git(root, "config", "user.name", "tests")
    git(root, "remote", "add", "origin", "git@github.com:example/model.git")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the tiny model")
    return {"root": root, "registry": harness / "toolkits.yaml", "experiment": exp_dir / "experiment.yaml",
            "out": tmp_path / "run"}


def run(model: dict, *extra: str) -> int:
    return runner.main(["--registry", str(model["registry"]), "run", str(model["experiment"]), "--toolkits", "stub",
                        "--out", str(model["out"]), *extra])


def manifest(model: dict) -> dict:
    return json.loads((model["out"] / "manifest.json").read_text())


def test_a_run_writes_its_jobs_and_records(model):
    assert run(model, "--levels", "low") == 0
    m = manifest(model)
    assert m["experiment"]["name"] == "tiny/1" and m["runtime"] == "none" and m["core"]["name"] == "wg1core"
    assert [j["status"] for j in m["jobs"]] == ["ok", "ok"] and m["model"]["uncommitted_changes"] == "no"
    for j in m["jobs"]:
        d = model["out"] / "stub" / j["member"] / "level-1"
        assert (d / "results.json").is_file() and (d / "adapter.log").is_file()
        assert json.loads((d / "job.json").read_text())["fingerprint"]["parameter_file_sha256"]
        r = json.loads((d / "record.json").read_text())
        records.validate(r)
        assert r["kind"] == "execution" and r["record_version"] == records.RECORD_VERSION
        assert r["repository"]["remote"] == "https://github.com/example/model" and r["repository"]["dirty"] is False
        assert r["environment"] == {**r["environment"], "path": "harness", "kind": "host-uv"}
        assert r["when"]["duration_seconds"] >= 0 and r["where"]["cores"] >= 1 and "image" not in r
        assert r["conditions"]["thread_variables"]["OMP_NUM_THREADS"] == "1"
        assert {o["path"] for o in r["outcome"]["outputs"]} == {"results.json", "methods.yaml", "settings.yaml"}
        fields = r["extensions"]["sce-wg-1"]
        assert fields["member"]["id"] == j["member"] and fields["level"] == "low"
        assert fields["verification"] == {"verdict": "not run"} and fields["toolkit_version"] == "stub 0.0"


def test_a_rerun_skips_what_is_done_and_redoes_what_changed(model):
    assert run(model, "--levels", "low") == 0
    assert run(model, "--levels", "low") == 0
    assert {j["skipped"] for j in manifest(model)["jobs"]} == {"yes"}
    stub = model["root"] / "harness" / "stub_adapter.py"
    stub.write_text(stub.read_text() + "\n# changed\n")
    assert run(model, "--levels", "low") == 0
    assert {j["skipped"] for j in manifest(model)["jobs"]} == {"no"}
    r = json.loads((model["out"] / "stub" / "m1" / "level-1" / "record.json").read_text())
    assert r["repository"]["dirty"] is True and len(r["repository"]["worktree_tree"]) in (40, 64)


def test_verification_fills_the_verdicts_and_catches_a_missing_quantity(model, monkeypatch):
    assert run(model, "--levels", "low") == 0
    assert runner.main(["--registry", str(model["registry"]), "verify", str(model["out"])]) == 0
    verdicts = json.loads((model["out"] / "verification.json").read_text())
    assert {v["status"] for v in verdicts} == {"ok"}
    r = json.loads((model["out"] / "stub" / "m1" / "level-1" / "record.json").read_text())
    assert r["extensions"]["sce-wg-1"]["verification"] == {"verdict": "verified"}
    monkeypatch.setenv("STUB_DROP", "kink")
    stub = model["root"] / "harness" / "stub_adapter.py"
    stub.write_text(stub.read_text() + "\n# dropped\n")
    assert run(model, "--levels", "low") == 0
    assert runner.main(["--registry", str(model["registry"]), "verify", str(model["out"])]) == 1
    verdicts = json.loads((model["out"] / "verification.json").read_text())
    assert {v["status"] for v in verdicts} == {"failed"} and all("types[].kink" in v["missing_reports"] for v in verdicts)
    r = json.loads((model["out"] / "stub" / "m1" / "level-1" / "record.json").read_text())
    assert r["extensions"]["sce-wg-1"]["verification"]["verdict"] == "failed"


def test_register_copies_the_records(model):
    assert run(model, "--levels", "low") == 0
    assert runner.main(["--registry", str(model["registry"]), "verify", str(model["out"])]) == 0
    assert runner.main(["--registry", str(model["registry"]), "register", str(model["out"])]) == 0
    folders = list((model["root"] / "harness" / "runs.registry").iterdir())
    assert len(folders) == 1 and folders[0].name.endswith("_tiny-1")
    assert sorted(p.name for p in folders[0].iterdir()) == ["stub_m1_low.json", "stub_m2_low.json"]
    for p in folders[0].iterdir():
        records.validate(json.loads(p.read_text()))


def test_list_names_the_experiment_and_the_toolkit(model, capsys):
    assert runner.main(["--registry", str(model["registry"]), "list"]) == 0
    out = capsys.readouterr().out
    assert "tiny/1" in out and "stub" in out


def test_the_container_command_follows_the_contract(model):
    m = runner.Model(model["registry"])
    tk = {**m.toolkits["stub"], "image_id": "sha256:" + "0" * 64}
    job = {"toolkit": "stub", "member": "m1", "level": "low", "level_arg": 1,
           "parameter_file": model["experiment"].parent / "m1.yaml",
           "request_file": model["experiment"].parent / "m1.request.yaml",
           "dir": model["out"] / "stub" / "m1" / "level-1"}
    cmd = runner.container_command(job, tk, {"model": m, "run_id": "run", "caps": {"cpus": 2.0, "memory": "8g"}})
    assert cmd[:2] == ["docker", "run"] and cmd[cmd.index("--network") + 1] == "none"
    assert cmd[cmd.index("--cpus") + 1] == "2.0" and cmd[cmd.index("--memory") + 1] == "8g"
    assert "--tmpfs" in cmd and "NUMBA_CACHE_DIR=/tmp/numba" in cmd and "HOME=/tmp" in cmd
    assert f"type=bind,source={m.root},target=/src,readonly" in cmd and cmd[cmd.index("--workdir") + 1] == "/src"
    assert cmd[cmd.index(tk["image_id"]) + 1] == "python" and cmd[-6:-4] == ["--out", "/out"]
    assert cmd[-7] == "schemas/experiments/tiny/m1.yaml" and cmd[-1] == "schemas/experiments/tiny/m1.request.yaml"


def test_the_experiment_checker_catches_what_the_validator_cannot(model):
    exp = experiment.load(model["experiment"])
    folder = model["experiment"].parent
    assert experiment.problems(exp, folder, RESULTS_SCHEMA) == []
    broken = json.loads(json.dumps(exp))
    broken["members"][0]["parameter_file_sha256"] = "0" * 64
    assert any("hash differs" in p for p in experiment.problems(broken, folder, RESULTS_SCHEMA))
    broken = json.loads(json.dumps(exp))
    broken["reports"].append("types[].target")
    assert "the results schema has no types[].target" in experiment.problems(broken, folder, RESULTS_SCHEMA)
    broken = json.loads(json.dumps(exp))
    broken["checks"][0]["pairs"] = [["m1", "m9"]]
    assert "kinks_agree: no member m9" in experiment.problems(broken, folder, RESULTS_SCHEMA)
    assert experiment.resolves("types[].rule.c", RESULTS_SCHEMA) and not experiment.resolves("types[].slope", RESULTS_SCHEMA)


def test_remotes_are_normalized_to_https():
    assert records.https_remote("git@github.com:owner/repo.git") == "https://github.com/owner/repo"
    assert records.https_remote("ssh://git@github.com/owner/repo.git") == "https://github.com/owner/repo"
    assert records.https_remote("https://github.com/owner/repo") == "https://github.com/owner/repo"


def test_the_environment_hash_sees_only_what_git_records(model):
    m = runner.Model(model["registry"])
    repo = records.repository(m.root)
    clean, tree = records.environment_hash(m.root, repo["commit"], "harness")
    (m.root / "harness" / ".venv").mkdir()
    (m.root / "harness" / ".venv" / "junk").write_text("x")
    (m.root / ".gitignore").write_text(".venv/\n")
    git(m.root, "add", ".gitignore")
    git(m.root, "commit", "-q", "-m", "ignore")
    again, _ = records.environment_hash(m.root, records.repository(m.root)["commit"], "harness")
    assert again == clean and tree and len(tree) in (40, 64)
