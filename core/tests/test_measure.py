"""The two steps of a job of an adapter on contract 2, on the tiny model repository of test_core.py: the adapter, given
the level's suggestions, writes the toolkit's solution, method and settings files; the model's bench, outside the
toolkit's environment, measures the solution and writes the results file. Each step has its record and is skipped
when its own fingerprint is unchanged; verification, comparison, registration and the status reader take a job's
results from its measure step.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

from test_core import RESULTS_SCHEMA, command, git, make_model, manifest, run
from wg1core import canonical, experiment, records, runner, status

# A stand-in toolkit on contract 2: it reads the level's suggestions, takes the tolerance where one is suggested and
# uses its own default otherwise, and writes a solution file, its methods and its settings with its answer to each
# suggestion. STUB_DROP names a key to leave out of the solution file.
STUB_SOLVER = textwrap.dedent('''
    import argparse, json, os
    from pathlib import Path
    import yaml
    from wg1core import canonical
    ap = argparse.ArgumentParser()
    ap.add_argument("member"); ap.add_argument("--out", required=True); ap.add_argument("--suggest", required=True)
    ap.add_argument("--request", required=True)
    a = ap.parse_args()
    member, request = canonical.load_strict(Path(a.member).read_text()), canonical.load_strict(Path(a.request).read_text())
    suggested = yaml.safe_load(Path(a.suggest).read_text())["suggested"]
    tolerance = suggested.get("tolerance", 0.01)
    out = Path(a.out)
    solution = {"toolkit": {"name": "stub", "version": "0.0"}, "parameter_file_sha256": canonical.model_hash(member),
                "request_file_sha256": canonical.model_hash(request),
                "types": [{"rule": {"kind": "linear", "m": [1.0, 2.0], "c": [0.5 * member["beta"], 0.75 * member["beta"]]},
                           "own": {"kink": 1.25 + tolerance + member["beta"] / 100}}]}
    solution.pop(os.environ.get("STUB_DROP", ""), None)
    (out / "solution.json").write_text(json.dumps(solution))
    (out / "methods.yaml").write_text("policy: time-iteration\\n")
    answers = {k: "taken" for k in suggested}
    (out / "settings.yaml").write_text(yaml.safe_dump({"settings": {"tolerance": tolerance}, "suggestions": answers}))
''')

# A stand-in bench: it reads the solution, the member, the request and its settings, and writes a results file that the
# tiny results schema accepts, its kink the solution's own moved by the settings' offset. STUB_BENCH_FAIL makes it fail.
STUB_BENCH = textwrap.dedent('''
    import argparse, json, os, sys
    from pathlib import Path
    import yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("member"); ap.add_argument("--request", required=True); ap.add_argument("--solution", required=True)
    ap.add_argument("--bench", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if os.environ.get("STUB_BENCH_FAIL"):
        sys.exit(3)
    solution = json.loads((Path(a.solution) / "solution.json").read_text())
    offset = yaml.safe_load(Path(a.bench).read_text())["settings"].get("offset", 0.0)
    types = [{"kink": t["own"]["kink"] + offset, "rule": {"c": t["rule"]["c"]}} for t in solution["types"]]
    (Path(a.out) / "results.json").write_text(json.dumps({**{k: solution[k] for k in ("toolkit", "parameter_file_sha256",
        "request_file_sha256")}, "types": types}))
''')

SOLUTION_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                   "required": ["toolkit", "types", "parameter_file_sha256", "request_file_sha256"]}
SUGGESTIONS_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
                      "additionalProperties": False,
                      "properties": {"tolerance": {"type": "number", "exclusiveMinimum": 0}}}


def make_measured(tmp_path: Path, bench: dict | None = None) -> dict:
    """The tiny model with its toolkit on contract 2 and a bench, the experiment declaring a level `out-of-box` that it
    gives no suggestions, and the bench's settings with an override at low."""
    model = make_model(tmp_path)
    root, harness = model["root"], model["root"] / "harness"
    (harness / "stub_solver.py").write_text(STUB_SOLVER)
    (harness / "stub_bench.py").write_text(STUB_BENCH)
    (harness / "bench_helper.py").write_text("# a file the bench's measurements depend on\n")
    (root / "schemas" / "solution.schema.json").write_text(json.dumps(SOLUTION_SCHEMA))
    (root / "schemas" / "suggestions.schema.json").write_text(json.dumps(SUGGESTIONS_SCHEMA))
    registry = yaml.safe_load(model["registry"].read_text())
    registry["model"].update({"solution_schema": "../schemas/solution.schema.json",
                              "suggestions_schema": "../schemas/suggestions.schema.json",
                              "bench": bench or {"script": "stub_bench.py", "code": ["bench_helper.py"]}})
    registry["toolkits"]["stub"] = {"adapter": "stub_solver.py", "code": ["stub_solver.py"], "contract": 2, "threads": 1}
    model["registry"].write_text(yaml.safe_dump(registry))
    exp = yaml.safe_load(model["experiment"].read_text())
    exp["levels"] = ["low", "out-of-box"]
    exp["suggestions"] = {"low": {"tolerance": 0.0001}}
    exp["bench"] = {"version": "1", "settings": {"offset": 0.5, "grid": {"points": 10, "top": 4.0}},
                    "levels": {"low": {"grid": {"points": 20}}}}
    model["experiment"].write_text(yaml.safe_dump(exp, sort_keys=False))
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "the stub on contract 2, with a bench")
    return model


@pytest.fixture
def measured(tmp_path: Path) -> dict:
    return make_measured(tmp_path)


def folder(model: dict, member: str = "m1", level: str = "low") -> Path:
    return model["out"] / "stub" / member / level


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def test_a_job_on_contract_two_is_solved_then_measured(measured):
    assert run(measured, "--levels", "low") == 0
    m = manifest(measured)
    assert [j["steps"] for j in m["jobs"]] == [{"solve": "ok", "measure": "ok"}] * 2
    assert m["toolkits"]["stub"]["contract"] == 2 and m["bench"]["script"] == "harness/stub_bench.py"
    d = folder(measured)
    suggestions = yaml.safe_load((d / "suggestions.yaml").read_text())
    assert suggestions == {"level": "low", "suggested": {"tolerance": 0.0001}}
    assert yaml.safe_load((d / "bench.yaml").read_text()) == {
        "level": "low", "settings": {"offset": 0.5, "grid": {"points": 20, "top": 4.0}}, "version": "1"}
    assert yaml.safe_load((d / "settings.yaml").read_text())["suggestions"] == {"tolerance": "taken"}
    assert read(d / "results.json")["types"][0]["kink"] == pytest.approx(1.25 + 0.0001 + 0.009 + 0.5)
    solve, measure = read(d / "record.json"), read(d / "measure.json")
    for r in (solve, measure):
        records.validate(r)
        assert r["$schema"].endswith("/0.1.0-draft.9.json") and r["kind"] == "execution"
    s, f = solve["extensions"]["sce-wg-1"], measure["extensions"]["sce-wg-1"]
    assert (s["step"], s["contract"], f["step"], f["contract"]) == ("solve", 2, "measure", 2)
    assert "results_sha256" not in s and "verification" not in s
    assert s["suggestions_sha256"] == f["suggestions_sha256"] == canonical.model_hash(suggestions)
    assert s["solution_sha256"] == f["solution_sha256"] == hashlib.sha256((d / "solution.json").read_bytes()).hexdigest()
    assert solve["script"] == "harness/stub_solver.py" and solve["arguments"][3:5] == ["--suggest", str(d / "suggestions.yaml")]
    assert {o["path"] for o in solve["outcome"]["outputs"]} == {"solution.json", "methods.yaml", "settings.yaml"}
    assert measure["script"] == "harness/stub_bench.py" and measure["outcome"]["log"] == "bench.log"
    assert measure["where"]["runtime"] == "none" and "image" not in measure
    assert [i["path"] for i in f["inputs"]] == ["solution.json", "methods.yaml", "settings.yaml", "bench.yaml"]
    assert f["bench"]["settings_sha256"] == canonical.model_hash(yaml.safe_load((d / "bench.yaml").read_text()))
    assert f["results_sha256"] == hashlib.sha256((d / "results.json").read_bytes()).hexdigest()
    assert f["verification"] == {"verdict": "not run"} and f["toolkit_version"] == "stub 0.0"
    job = read(d / "job.json")
    assert job["solve"]["status"] == job["measure"]["status"] == "ok" and "level_arg" not in job["fingerprint"]
    assert job["fingerprint"]["suggestions_sha256"] == s["suggestions_sha256"]


def test_a_level_without_suggestions_suggests_nothing(measured):
    assert run(measured, "--levels", "out-of-box") == 0
    d = folder(measured, level="out-of-box")
    assert yaml.safe_load((d / "suggestions.yaml").read_text()) == {"level": "out-of-box", "suggested": {}}
    assert yaml.safe_load((d / "settings.yaml").read_text()) == {"settings": {"tolerance": 0.01}, "suggestions": {}}


def test_each_step_runs_again_only_when_its_own_inputs_change(measured):
    assert run(measured, "--levels", "low") == 0
    started = read(folder(measured) / "record.json")["when"]["started"]
    assert run(measured, "--levels", "low") == 0
    assert {j["skipped"] for j in manifest(measured)["jobs"]} == {"yes"}
    # a change to the bench's code measures again without solving again
    helper = measured["root"] / "harness" / "bench_helper.py"
    helper.write_text(helper.read_text() + "# changed\n")
    assert run(measured, "--levels", "low") == 0
    assert [j["steps"] for j in manifest(measured)["jobs"]] == [{"solve": "skipped", "measure": "ok"}] * 2
    assert read(folder(measured) / "record.json")["when"]["started"] == started
    # so does a change to the bench's settings in the experiment
    exp = yaml.safe_load(measured["experiment"].read_text())
    exp["bench"]["settings"]["offset"] = 0.25
    measured["experiment"].write_text(yaml.safe_dump(exp, sort_keys=False))
    assert run(measured, "--levels", "low") == 0
    assert [j["steps"] for j in manifest(measured)["jobs"]] == [{"solve": "skipped", "measure": "ok"}] * 2
    assert read(folder(measured) / "results.json")["types"][0]["kink"] == pytest.approx(1.25 + 0.0001 + 0.009 + 0.25)
    # a change to the level's suggestions solves again, and so measures again
    exp["suggestions"]["low"]["tolerance"] = 0.001
    measured["experiment"].write_text(yaml.safe_dump(exp, sort_keys=False))
    assert run(measured, "--levels", "low") == 0
    assert [j["steps"] for j in manifest(measured)["jobs"]] == [{"solve": "ok", "measure": "ok"}] * 2
    assert read(folder(measured) / "results.json")["types"][0]["kink"] == pytest.approx(1.25 + 0.001 + 0.009 + 0.25)


def test_verification_comparison_registration_and_status_take_the_measure_step(measured):
    assert run(measured, "--levels", "low") == 0
    assert command(measured, "verify") == 0
    d = folder(measured)
    assert read(d / "measure.json")["extensions"]["sce-wg-1"]["verification"] == {"verdict": "verified"}
    assert "verification" not in read(d / "record.json")["extensions"]["sce-wg-1"]
    assert command(measured, "compare") == 0
    assert read(d / "measure.json")["extensions"]["sce-wg-1"]["comparison"]["status"] == "computed"
    assert "comparison" not in read(d / "record.json")["extensions"]["sce-wg-1"]
    assert command(measured, "register") == 0
    (registered,) = (measured["root"] / "harness" / "runs.registry").iterdir()
    assert sorted(p.name for p in registered.iterdir()) == [
        "stub_m1_low.json", "stub_m1_low_measure.json", "stub_m2_low.json", "stub_m2_low_measure.json"]
    (registry_dir := measured["root"] / "harness" / "runs.registry")
    (registry_dir / status.OF_RECORD).write_text(yaml.safe_dump({"runs_of_record": [
        {"experiment": "tiny/1", "toolkit": "stub", "run": registered.name}]}))
    found = status.read(measured["root"])
    (cell,) = found["data"]["cells"]
    assert not found["data"]["problems"] and cell["schema"]["invalid"] == 0
    assert cell["steps"] == {"solve": 2, "measure": 2} and cell["verification"] == {"verified": 2}
    assert cell["comparison"]["statuses"] == {"computed": 1, "not run": 1} and cell["members"] == ["m1", "m2"]


def test_a_solution_the_model_s_schema_refuses_fails_the_solve_and_is_not_measured(measured, monkeypatch):
    monkeypatch.setenv("STUB_DROP", "types")
    assert run(measured, "--levels", "low") == 1
    d = folder(measured)
    job = read(d / "job.json")
    assert job["status"] == "failed" and job["solve"]["status"] == "failed" and job["measure"] == {"status": "not run"}
    assert "'types' is a required property" in job["solve"]["problems"][0]
    assert not (d / "results.json").exists() and not (d / "measure.json").exists()
    records.validate(read(d / "record.json"))


def test_a_failing_bench_fails_the_measure_and_records_it(measured, monkeypatch):
    monkeypatch.setenv("STUB_BENCH_FAIL", "1")
    assert run(measured, "--levels", "low") == 1
    d = folder(measured)
    job = read(d / "job.json")
    assert job["solve"]["status"] == "ok" and job["measure"]["status"] == "failed" and job["measure"]["exit_code"] == 3
    r = read(d / "measure.json")
    records.validate(r)
    assert r["outcome"]["exit_code"] == 3 and r["outcome"]["outputs"] == []
    monkeypatch.delenv("STUB_BENCH_FAIL")
    assert run(measured, "--levels", "low") == 0
    assert [j["steps"] for j in manifest(measured)["jobs"]] == [{"solve": "skipped", "measure": "ok"}] * 2


def test_a_bench_started_by_its_stated_command(tmp_path):
    stated = [sys.executable, "{script}", "{member}", "--request", "{request}", "--solution", "{solution}",
              "--bench", "{bench}", "--out", "{out}"]
    model = make_measured(tmp_path, bench={"script": "stub_bench.py", "command": stated})
    assert run(model, "--levels", "low") == 0
    d = folder(model)
    assert read(d / "job.json")["measure"]["fingerprint"]["bench_command"] == stated
    r = read(d / "measure.json")
    assert r["script"] == "harness/stub_bench.py" and r["arguments"][1:3] == ["--request", str(d.parent.parent.parent.parent
        / "model" / "schemas" / "experiments" / "tiny" / "m1.request.yaml")]


def test_contract_two_needs_a_bench_and_states_no_levels(measured):
    registry = yaml.safe_load(measured["registry"].read_text())
    del registry["model"]["bench"]
    measured["registry"].write_text(yaml.safe_dump(registry))
    with pytest.raises(SystemExit, match="names no bench"):
        run(measured, "--levels", "low")
    for change, says in (({"levels": {"low": 1}}, "unknown keys"), ({"contract": 3}, "contract is 3")):
        entry = {"adapter": "stub_solver.py", "contract": 2, **change}
        registry["toolkits"]["stub"] = entry
        measured["registry"].write_text(yaml.safe_dump(registry))
        with pytest.raises(SystemExit, match=says):
            runner.Model(measured["registry"])
    registry["model"]["bench"] = {"script": "stub_bench.py", "command": ["python", "stub_bench.py"]}
    registry["toolkits"]["stub"] = {"adapter": "stub_solver.py", "contract": 2}
    measured["registry"].write_text(yaml.safe_dump(registry))
    with pytest.raises(SystemExit, match="bench: command is a list of words"):
        runner.Model(measured["registry"])


def test_the_experiment_s_suggestions_and_bench_settings_are_checked(measured):
    exp = experiment.load(measured["experiment"])
    where = measured["experiment"].parent
    assert experiment.problems(exp, where, RESULTS_SCHEMA, None, SUGGESTIONS_SCHEMA) == []
    exp["suggestions"] = {"low": {"tolerance": -1}, "high": {}}
    exp["bench"]["levels"]["medium"] = {}
    found = experiment.problems(exp, where, RESULTS_SCHEMA, None, SUGGESTIONS_SCHEMA)
    assert found == ["the suggestions at low: tolerance: -1 is less than or equal to the minimum of 0",
                     "suggestions for high, a level the experiment does not declare",
                     "bench settings for medium, a level the experiment does not declare"]
    exp = experiment.load(measured["experiment"])
    exp["levels"] = ["Low"]
    assert any("does not match" in p for p in experiment.problems(exp, where))


def test_the_container_command_gives_the_suggestions(measured):
    m = runner.Model(measured["registry"])
    tk = {**m.toolkits["stub"], "image_id": "sha256:" + "0" * 64}
    exp = experiment.load(measured["experiment"])
    (job,) = [j for j in runner.plan_jobs(measured["experiment"], exp, m, ["stub"], ["low"], ["m1"], measured["out"])]
    cmd = runner.container_command(job, tk, {"model": m, "run_id": "run", "caps": {"cpus": 2.0}})
    assert cmd[-4:-2] == ["--suggest", "/out/suggestions.yaml"] and "--level" not in cmd
    assert cmd[cmd.index(tk["image_id"]) + 1:cmd.index(tk["image_id"]) + 3] == ["python", "harness/stub_solver.py"]
