"""The core's tests, on a model repository of its own making: a tiny results schema, two members with their request
files, one experiment with a pinned reference for one member, a registry file with a stand-in toolkit, all committed
in a temporary git repository with a remote named and no network. The runner runs, the records validate, verification
fills the verdicts, the comparator evaluates the checks and reports the distances from the reference, the registry is
written, the container command follows the contract, and the experiment checker catches what the validator cannot.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from wg1core import canonical, comparator, experiment, records, runner

RESULTS_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object", "required": ["toolkit", "types", "parameter_file_sha256", "request_file_sha256"],
    "properties": {
        "parameter_file_sha256": {"type": "string"}, "request_file_sha256": {"type": "string"},
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
    results schema accepts, solving nothing; the kink depends on the member's beta and the level. STUB_DROP names a
    key to leave out of every type."""
    import argparse, json, os
    from pathlib import Path
    import yaml
    from wg1core import canonical
    ap = argparse.ArgumentParser()
    ap.add_argument("member"); ap.add_argument("--out", required=True); ap.add_argument("--level", required=True)
    ap.add_argument("--request", required=True)
    a = ap.parse_args()
    member, request = canonical.load_strict(Path(a.member).read_text()), canonical.load_strict(Path(a.request).read_text())
    beta = member["beta"]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    t = {"kink": 1.25 + 0.01 * int(a.level) + beta / 100, "rule": {"c": [0.5 * beta, 0.75 * beta]}}
    t.pop(os.environ.get("STUB_DROP", ""), None)
    (out / "results.json").write_text(json.dumps({"toolkit": {"name": "stub", "version": "0.0"}, "types": [t],
        "parameter_file_sha256": canonical.model_hash(member), "request_file_sha256": canonical.model_hash(request)}))
    (out / "methods.yaml").write_text("policy: time-iteration\\n")
    (out / "settings.yaml").write_text(f"level: {a.level}\\n")
''')

REFERENCE_M1 = {"toolkit": {"name": "bench-continuous", "version": "0.0"},
                "types": [{"kink": 1.30, "rule": {"c": [0.45, 0.68]}}]}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def make_model(tmp_path: Path, at_most: float = 1.0, reference: dict | None = None, same_question: bool = True) -> dict:
    """A tiny model repository, committed: one experiment of two members, a reference pinned for the first, and a
    stand-in toolkit; `at_most` is the tolerance of the experiment's one check on the kinks; `reference` replaces the
    reference's content; with `same_question` false the reference carries another request's hash."""
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
    m1_member = {"family": "tiny/1", "beta": 0.9}
    m1_request = {"family": "tiny/1", "parameter_file_sha256": canonical.model_hash(m1_member), "points": [1.0, 2.0]}
    ref = dict(reference or REFERENCE_M1)
    ref["parameter_file_sha256"] = canonical.model_hash(m1_member)
    ref["request_file_sha256"] = canonical.model_hash(m1_request) if same_question else "f" * 64
    ref_bytes = json.dumps(ref, indent=1).encode()
    (exp_dir / "m1.reference.json").write_bytes(ref_bytes)
    members[0]["reference"] = {"results_file": "m1.reference.json", "results_sha256": hashlib.sha256(ref_bytes).hexdigest(),
                               "errors": {"types[].kink": 0.001, "types[].rule.c": 0.002}}
    exp = {"experiment": "tiny/1", "title": "A tiny experiment", "statement": "Two members at one level.",
           "members": members, "levels": ["low"], "reports": ["types[].kink", "types[].rule.c"],
           "reference_quantities": [{"quantity": "types[].kink", "metric": "max_abs_difference"},
                                    {"quantity": "types[].rule.c", "metric": "max_relative_difference"}],
           "checks": [{"id": "kinks_agree", "statement": "The two members' kinks are close.", "compare": "members",
                       "quantity": "types[].kink", "metric": "max_abs_difference", "pairs": [["m1", "m2"]],
                       "expect": {"at_most": at_most}},
                      {"id": "rules_converge", "statement": "The rules move less at each finer level.", "compare": "levels",
                       "quantity": "types[].rule.c", "metric": "max_abs_difference", "expect": "falls_with_level"}]}
    (exp_dir / "experiment.yaml").write_text(yaml.safe_dump(exp, sort_keys=False))
    (harness / "stub_adapter.py").write_text(STUB_ADAPTER)
    (harness / "toolkits.yaml").write_text(yaml.safe_dump({
        "model": {"results_schema": "../schemas/results.schema.json", "experiments": "../schemas/experiments",
                  "registry_dir": "runs.registry", "identity": ["parameter_file_sha256", "request_file_sha256"]},
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


@pytest.fixture
def model(tmp_path: Path) -> dict:
    return make_model(tmp_path)


def run(model: dict, *extra: str) -> int:
    return runner.main(["--registry", str(model["registry"]), "run", str(model["experiment"]), "--toolkits", "stub",
                        "--out", str(model["out"]), *extra])


def command(model: dict, name: str, *extra: str) -> int:
    return runner.main(["--registry", str(model["registry"]), name, str(model["out"]), *extra])


def manifest(model: dict) -> dict:
    return json.loads((model["out"] / "manifest.json").read_text())


def record(model: dict, member: str) -> dict:
    return json.loads((model["out"] / "stub" / member / "low" / "record.json").read_text())


def test_a_run_writes_its_jobs_and_records(model):
    assert run(model, "--levels", "low") == 0
    m = manifest(model)
    assert m["experiment"]["name"] == "tiny/1" and m["runtime"] == "none" and m["core"]["name"] == "wg1core"
    assert [j["status"] for j in m["jobs"]] == ["ok", "ok"] and m["model"]["uncommitted_changes"] == "no"
    for j in m["jobs"]:
        d = model["out"] / "stub" / j["member"] / "low"
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
    r = record(model, "m1")
    assert r["repository"]["dirty"] is True and len(r["repository"]["worktree_tree"]) in (40, 64)


def test_verification_fills_the_verdicts_and_catches_a_missing_quantity(model, monkeypatch):
    assert run(model, "--levels", "low") == 0
    assert command(model, "verify") == 0
    verdicts = json.loads((model["out"] / "verification.json").read_text())
    assert {v["status"] for v in verdicts} == {"ok"}
    assert record(model, "m1")["extensions"]["sce-wg-1"]["verification"] == {"verdict": "verified"}
    monkeypatch.setenv("STUB_DROP", "kink")
    stub = model["root"] / "harness" / "stub_adapter.py"
    stub.write_text(stub.read_text() + "\n# dropped\n")
    assert run(model, "--levels", "low") == 0
    assert command(model, "verify") == 1
    verdicts = json.loads((model["out"] / "verification.json").read_text())
    assert {v["status"] for v in verdicts} == {"failed"} and all("types[].kink" in v["missing_reports"] for v in verdicts)
    assert record(model, "m1")["extensions"]["sce-wg-1"]["verification"]["verdict"] == "failed"


def test_the_comparator_evaluates_the_checks_and_reports_the_distances(model):
    assert run(model, "--levels", "low") == 0
    assert command(model, "verify") == 0
    assert command(model, "compare") == 0
    report = json.loads((model["out"] / "comparison.json").read_text())
    checks = {c["id"]: c for c in report["checks"]}
    # the kinks differ by the betas' difference over a hundred, well within the tolerance of one
    assert checks["kinks_agree"]["verdict"] == "pass"
    assert checks["kinks_agree"]["values"][0]["values"][0] == pytest.approx(0.0005)
    # one level only: a check on successive levels cannot apply, and is not a failure
    assert checks["rules_converge"]["verdict"] == "not applicable"
    by_member = {j["member"]: j for j in report["reference"]}
    m1, m2 = by_member["m1"], by_member["m2"]
    assert m1["status"] == "computed" and m2["status"] == "not run" and "no reference" in m2["reason"]
    d = {r["quantity"]: r for r in m1["distances"]}
    assert d["types[].kink"]["distance"] == pytest.approx(abs(1.25 + 0.01 + 0.009 - 1.30))
    assert d["types[].kink"]["reference_error"] == 0.001 and d["types[].rule.c"]["metric"] == "max_relative_difference"
    assert m1["largest_distance"]["quantity"] in ("types[].kink", "types[].rule.c")
    # each job's own report, and the record's block: a status and the reference, never a verdict
    job_report = json.loads((model["out"] / "stub" / "m1" / "low" / "comparison.json").read_text())
    assert job_report["status"] == "computed" and job_report["reference"] == m1["reference"]
    block = record(model, "m1")["extensions"]["sce-wg-1"]["comparison"]
    assert block["status"] == "computed" and block["reference"] == m1["reference"] and "verdict" not in block
    assert block["report"] == "comparison.json" and block["largest_distance"]["distance"] >= 0
    records.validate(record(model, "m1"))
    assert record(model, "m2")["extensions"]["sce-wg-1"]["comparison"] == {"status": "not run", "report": "comparison.json",
                                                                          "reason": "the member pins no reference"}
    md = (model["out"] / "comparison.md").read_text()
    assert "| `kinks_agree` |" in md and "**pass**" in md and "Distances from the reference" in md


def test_a_failed_check_fails_the_comparison_but_a_distance_never_does(tmp_path):
    model = make_model(tmp_path, at_most=1e-6)
    assert run(model, "--levels", "low") == 0
    assert command(model, "compare") == 1
    report = json.loads((model["out"] / "comparison.json").read_text())
    assert {c["id"]: c["verdict"] for c in report["checks"]} == {"kinks_agree": "fail", "rules_converge": "not applicable"}
    # the reference distances are large relative to the reference's error, and still carry no verdict
    m1 = next(j for j in report["reference"] if j["member"] == "m1")
    assert m1["status"] == "computed" and all("verdict" not in r for r in m1["distances"])


def test_an_uncomputable_comparison_is_an_error_that_fails_the_command(tmp_path):
    # the reference lacks the rule, so one of the two named distances cannot be computed
    model = make_model(tmp_path, reference={"toolkit": {"name": "bench-continuous", "version": "0.0"}, "types": [{"kink": 1.30}]})
    assert run(model, "--levels", "low") == 0
    assert command(model, "compare") == 1
    report = json.loads((model["out"] / "comparison.json").read_text())
    m1 = next(j for j in report["reference"] if j["member"] == "m1")
    assert m1["status"] == "error" and "could not be computed" in m1["reason"] and report["failed"]
    assert {c["verdict"] for c in report["checks"]} == {"pass", "not applicable"}  # the checks themselves pass
    block = record(model, "m1")["extensions"]["sce-wg-1"]["comparison"]
    assert block["status"] == "error" and "reason" in block and "largest_distance" not in block
    records.validate(record(model, "m1"))


def test_a_reference_to_another_question_is_an_error(tmp_path):
    model = make_model(tmp_path, same_question=False)
    assert run(model, "--levels", "low") == 0
    assert command(model, "compare") == 1
    report = json.loads((model["out"] / "comparison.json").read_text())
    m1 = next(j for j in report["reference"] if j["member"] == "m1")
    assert m1["status"] == "error" and "request_file_sha256 differs" in m1["reason"]


def test_levels_are_ordered_as_the_experiment_lists_them():
    assert comparator._levels_in_order({"high", "low", "medium"}, ["low", "medium", "high"]) == ["low", "medium", "high"]
    assert comparator._levels_in_order({"fine", "coarse"}, ["coarse", "default", "fine"]) == ["coarse", "fine"]
    assert comparator._levels_in_order({"odd", "low"}, ["low", "medium", "high"]) == ["low", "odd"]


def test_a_reference_that_does_not_hash_is_refused_before_anything_runs(model):
    ref = model["experiment"].parent / "m1.reference.json"
    ref.write_text(ref.read_text() + "\n")
    with pytest.raises(SystemExit, match="reference file's hash differs"):
        run(model, "--levels", "low")


def test_register_copies_the_records(model):
    assert run(model, "--levels", "low") == 0
    assert command(model, "verify") == 0
    assert command(model, "register") == 0
    folders = list((model["root"] / "harness" / "runs.registry").iterdir())
    assert len(folders) == 1 and folders[0].name.endswith("_tiny-1")
    assert sorted(p.name for p in folders[0].iterdir()) == ["stub_m1_low.json", "stub_m2_low.json"]
    for p in folders[0].iterdir():
        records.validate(json.loads(p.read_text()))


def test_list_names_the_experiment_and_the_toolkit(model, capsys):
    assert runner.main(["--registry", str(model["registry"]), "list"]) == 0
    out = capsys.readouterr().out
    assert "tiny/1" in out and "stub" in out


def test_the_core_names_itself(model):
    from wg1core import identity
    i = identity()
    assert i["name"] == "wg1core" and i["version"] and set(i) <= {"name", "version", "commit"}
    assert run(model, "--levels", "low") == 0
    m = manifest(model)
    assert m["core"]["name"] == "wg1core" and m["core"]["version"] == i["version"]
    r = record(model, "m1")
    assert r["recorder"]["name"] == "wg1core runner" and r["recorder"]["version"] == i["version"]


def test_the_container_command_follows_the_contract(model):
    m = runner.Model(model["registry"])
    tk = {**m.toolkits["stub"], "image_id": "sha256:" + "0" * 64}
    job = {"toolkit": "stub", "member": "m1", "level": "low", "level_arg": 1,
           "parameter_file": model["experiment"].parent / "m1.yaml",
           "request_file": model["experiment"].parent / "m1.request.yaml",
           "dir": model["out"] / "stub" / "m1" / "low"}
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
    broken = json.loads(json.dumps(exp))
    broken["members"][0]["reference"]["errors"]["types[].slope"] = 0.1
    assert "the results schema has no types[].slope" in experiment.problems(broken, folder, RESULTS_SCHEMA)
    assert experiment.resolves("types[].rule.c", RESULTS_SCHEMA) and not experiment.resolves("types[].slope", RESULTS_SCHEMA)


def test_quantities_and_metrics():
    a = {"types": [{"kink": 1.0, "rule": {"c": [0.5, 0.75]}}, {"kink": 2.0, "rule": {"c": [0.6, 0.8]}}]}
    b = {"types": [{"kink": 1.5, "rule": {"c": [0.5, 0.70]}}, {"kink": 2.0, "rule": {"c": [0.9, 0.8]}}]}
    assert comparator.numbers(a, "types[].kink") == [1.0, 2.0]
    assert comparator.numbers(a, "types[].rule.c") == [0.5, 0.75, 0.6, 0.8]
    assert comparator.numbers(a, "types[]") == [1.0, 0.5, 0.75, 2.0, 0.6, 0.8]  # a mapping's numbers by sorted key
    assert comparator.compare(a, b, "types[].kink", "max_abs_difference") == 0.5
    assert comparator.compare(a, b, "types[].rule.c", "max_abs_difference") == pytest.approx(0.3)
    assert comparator.compare(a, b, "types[].kink", "max_relative_difference") == 0.5  # divided by max(1, 1.0)
    with pytest.raises(ValueError, match="numbers"):
        comparator.compare(a, {"types": [{"kink": 1.0, "rule": {"c": [0.5]}}]}, "types[].rule.c", "max_abs_difference")
    with pytest.raises(KeyError):
        comparator.numbers(a, "types[].target")


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


def test_the_verifier_runs_from_the_root_with_absolute_paths(model):
    """The verifier's command runs from the repository's root, its own paths written from there, and `{member}` and
    `{results}` are replaced by absolute paths."""
    root = model["root"]
    (root / "tools").mkdir()
    (root / "tools" / "verify.py").write_text(textwrap.dedent("""\
        import json, os, sys
        member, results = sys.argv[1], sys.argv[3]
        data = json.load(open(results))
        with open(os.path.join(os.path.dirname(results), "verifier.json"), "w") as f:
            json.dump({"cwd": os.getcwd(), "member": member, "results": results}, f)
        sys.exit(0 if data.get("types") else 1)
        """))
    registry = yaml.safe_load(model["registry"].read_text())
    registry["model"]["verifier"] = [sys.executable, "tools/verify.py", "{member}", "--verify-results", "{results}"]
    model["registry"].write_text(yaml.safe_dump(registry))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "a verifier at the root")
    assert run(model, "--levels", "low") == 0
    assert runner.main(["--registry", str(model["registry"]), "verify", str(model["out"])]) == 0
    seen = [json.loads(p.read_text()) for p in sorted((model["out"] / "stub").rglob("verifier.json"))]
    assert len(seen) == 2
    for s in seen:
        assert Path(s["cwd"]).resolve() == root.resolve()
        assert Path(s["member"]).is_absolute() and Path(s["member"]).is_file()
        assert Path(s["results"]).is_absolute() and Path(s["results"]).name == "results.json"


def test_the_record_names_the_continuous_integration_run(model, monkeypatch):
    """Under GitHub Actions the `where` block carries the run, the provider, the identifier and the attempt's address,
    from the service's own variables; on a workstation it carries no `ci` at all."""
    for k in ("GITHUB_ACTIONS", "GITHUB_RUN_ID", "GITHUB_RUN_ATTEMPT", "GITHUB_REPOSITORY", "GITHUB_SERVER_URL"):
        monkeypatch.delenv(k, raising=False)
    assert "ci" not in records.machine("none")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_ID", "123456")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    monkeypatch.setenv("GITHUB_REPOSITORY", "example/model")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    assert run(model, "--levels", "low") == 0
    r = json.loads(next((model["out"] / "stub" / "m1").rglob("record.json")).read_text())
    assert r["where"]["ci"] == {"provider": "github-actions", "run_id": "123456",
                                "url": "https://github.com/example/model/actions/runs/123456/attempts/2"}
    records.validate(r)


def test_a_clone_whose_origin_is_a_local_path_is_refused_before_anything_runs(model):
    git(model["root"], "remote", "set-url", "origin", str(model["root"].parent / "elsewhere"))
    with pytest.raises(SystemExit, match="origin is"):
        run(model, "--levels", "low")
    assert not model["out"].exists()


def test_the_environment_hash_takes_each_name_as_it_is_whatever_core_quotepath_says(model):
    """Without `-z`, git quotes a name outside ASCII when `core.quotePath` is true, its default, and the hash then
    held the quoted name with its directory; with it, the hash is the schema's on the name itself."""
    m = runner.Model(model["registry"])
    (m.root / "harness" / "données.txt").write_text("é\n", encoding="utf-8")
    git(m.root, "add", "-A")
    git(m.root, "commit", "-q", "-m", "a name outside ASCII")
    commit = records.repository(m.root)["commit"]
    hashes = set()
    for quote in ("true", "false"):
        git(m.root, "config", "core.quotePath", quote)
        hashes.add(records.environment_hash(m.root, commit, "harness")[0])
    lines = []
    for line in git(m.root, "-c", "core.quotePath=false", "ls-tree", "-r", commit, "--", "harness").splitlines():
        meta, _, name = line.partition("\t")
        mode, _, obj = meta.split()
        blob = subprocess.run(["git", "cat-file", "blob", obj], cwd=m.root, capture_output=True, check=True).stdout
        rel = name.removeprefix("harness/").encode("utf-8")
        lines.append((rel, f"blob {mode} {hashlib.sha256(blob).hexdigest()} ".encode() + rel + b"\n"))
    assert hashes == {hashlib.sha256(b"".join(text for _, text in sorted(lines))).hexdigest()}


def test_each_source_is_checked_against_its_own_anchors(model):
    exp = experiment.load(model["experiment"])
    folder = model["experiment"].parent
    exp["sources"] = {"bst": ["a-limit"], "other": ["a-section", "no-such-section"]}
    # A set alone is BST's anchors, as before; the other source has none, so it is not checked.
    assert experiment.problems(exp, folder, RESULTS_SCHEMA, {"a-limit"}) == []
    assert experiment.problems(exp, folder, RESULTS_SCHEMA, {"bst": {"a-limit"}, "other": {"a-section"}}) == [
        "the source page of other has no anchor no-such-section"]
    assert experiment.problems(exp, folder, RESULTS_SCHEMA, {"bst": set()}) == [
        "the source page of bst has no anchor a-limit"]


def test_the_registry_file_names_one_anchors_file_or_one_per_source(model):
    harness = model["registry"].parent
    (harness / "bst-anchors.txt").write_text("# BST's\na-limit\n")
    (harness / "other-anchors.txt").write_text("a-section\n")
    registry = yaml.safe_load(model["registry"].read_text())
    registry["model"]["anchors"] = "bst-anchors.txt"
    model["registry"].write_text(yaml.safe_dump(registry))
    assert runner.Model(model["registry"]).anchors == {"bst": {"a-limit"}}
    registry["model"]["anchors"] = {"bst": "bst-anchors.txt", "other": "other-anchors.txt", "third": "missing.txt"}
    model["registry"].write_text(yaml.safe_dump(registry))
    assert runner.Model(model["registry"]).anchors == {"bst": {"a-limit"}, "other": {"a-section"}}


def test_a_signal_is_recorded_by_its_name():
    assert runner.signal_name(9, linux=True) == "SIGKILL"
    assert runner.signal_name(10, linux=True) == "SIGUSR1"  # SIGBUS by macOS's numbering, which a container never has
    assert runner.signal_name(9, linux=False) == "SIGKILL"
    assert runner.signal_name(64, linux=True) == "signal 64"


def test_a_job_its_process_killed_by_a_signal_is_recorded_so(model):
    killed = "import os, signal\nos.kill(os.getpid(), signal.SIGKILL)\n"
    (model["registry"].parent / "stub_adapter.py").write_text(killed)
    git(model["root"], "commit", "-q", "-am", "an adapter that is killed")
    assert run(model, "--levels", "low") != 0
    outcome = record(model, "m1")["outcome"]
    assert (outcome["termination"], outcome["signal"], outcome["exit_code"]) == ("signal", "SIGKILL", -9)


def test_an_adapter_is_started_by_its_stated_command(model):
    """A registry entry's `command` is used as it is given: here the interpreter named by its own path, which is not
    the word `python`, so that nothing is put before it. The record names the adapter as its script and its arguments
    as the contract's; the fingerprint holds the command, so that a changed command reruns the jobs."""
    registry = yaml.safe_load(model["registry"].read_text())
    registry["toolkits"]["stub"]["command"] = [sys.executable, "-X", "utf8", "{adapter}"]
    model["registry"].write_text(yaml.safe_dump(registry))
    git(model["root"], "commit", "-q", "-am", "the stub started by a stated command")
    assert run(model, "--levels", "low") == 0
    r = record(model, "m1")
    records.validate(r)
    assert r["script"] == "harness/stub_adapter.py" and r["arguments"][1] == "--out"
    job = json.loads((model["out"] / "stub" / "m1" / "low" / "job.json").read_text())
    assert job["command"][:4] == ["python", "-X", "utf8", "harness/stub_adapter.py"]  # the interpreter shown as python
    assert job["fingerprint"]["command"] == [sys.executable, "-X", "utf8", "{adapter}"]
    assert manifest(model)["toolkits"]["stub"]["command"] == [sys.executable, "-X", "utf8", "{adapter}"]
    m = runner.Model(model["registry"])
    tk = {**m.toolkits["stub"], "image_id": "sha256:" + "0" * 64}
    job = {"toolkit": "stub", "member": "m1", "level": "low", "level_arg": 1,
           "parameter_file": model["experiment"].parent / "m1.yaml",
           "request_file": model["experiment"].parent / "m1.request.yaml", "dir": model["out"] / "stub" / "m1" / "low"}
    cmd = runner.container_command(job, tk, {"model": m, "run_id": "run", "caps": {"cpus": 2.0}})
    at = cmd.index(tk["image_id"])
    assert cmd[at + 1:at + 5] == [sys.executable, "-X", "utf8", "harness/stub_adapter.py"]


def test_a_default_command_is_not_in_the_fingerprint(model):
    """An entry that states no command keeps the fingerprint it had before commands could be stated, so that no run
    of record looks stale for it."""
    assert run(model, "--levels", "low") == 0
    job = json.loads((model["out"] / "stub" / "m1" / "low" / "job.json").read_text())
    assert "command" not in job["fingerprint"] and "command" not in manifest(model)["toolkits"]["stub"]


@pytest.mark.parametrize("stated", [[], ["python"], ["python", "{adapter}", "{adapter}"], "python {adapter}",
                                    ["python", "--file={adapter}"]])
def test_a_command_without_the_adapter_as_a_word_is_refused(model, stated):
    registry = yaml.safe_load(model["registry"].read_text())
    registry["toolkits"]["stub"]["command"] = stated
    model["registry"].write_text(yaml.safe_dump(registry))
    with pytest.raises(SystemExit, match="command is a list of words"):
        runner.Model(model["registry"])
