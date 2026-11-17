"""The status reader's tests, on the tiny model repository of test_core.py: a run is made, verified, compared and
registered, and the reader is asked what the repository holds, with and without a file of runs of record, with a
changed experiment, a newer run, records of an earlier draft and of one the core does not hold, a mode of solution,
and a file with problems.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import json
import shutil
from importlib import metadata
from pathlib import Path

import pytest
import yaml

from test_core import command, git, make_model, run
from wg1core import records, runner, status


@pytest.fixture
def registered(tmp_path: Path) -> dict:
    """The tiny model with one run registered: two members at one level, the first with a reference."""
    model = make_model(tmp_path)
    assert run(model, "--levels", "low") == 0
    assert command(model, "verify") == 0 and command(model, "compare") == 0 and command(model, "register") == 0
    model["registry_dir"] = model["root"] / "harness" / "runs.registry"
    (model["run"],) = [p.name for p in model["registry_dir"].iterdir()]
    return model


def name_runs(model: dict, *entries: dict) -> None:
    (model["registry_dir"] / status.OF_RECORD).write_text(yaml.safe_dump({"runs_of_record": list(entries)}))


def of_record(model: dict, **more) -> dict:
    return {"experiment": "tiny/1", "toolkit": "stub", "run": model["run"], **more}


def rewrite(model: dict, folder: str, change) -> None:
    """Every execution record of a registry folder, changed in place."""
    for path in (model["registry_dir"] / folder).glob("*.json"):
        record = json.loads(path.read_text())
        change(record)
        path.write_text(json.dumps(record, indent=1) + "\n")


def test_without_a_file_of_runs_of_record_the_reader_says_so(registered):
    found = status.read(registered["root"])
    assert found["summary"] == "1 toolkit on 1 experiment: no file of runs of record"
    (cell,) = found["data"]["cells"]
    assert (cell["experiment"], cell["toolkit"], cell["mode"], cell["run_of_record"]) == ("tiny/1", "stub", None, None)
    assert cell["notes"] == [f"no run of record; the registry's newest run is {registered['run']}"]
    assert found["data"]["runs_of_record_file"] is None and not found["data"]["problems"]
    assert "has no file of runs of record" in found["table"]


def test_a_run_of_record_is_read_from_its_records(registered):
    name_runs(registered, of_record(registered))
    found = status.read(registered["root"], entry=None)
    assert found["summary"] == "1 toolkit on 1 experiment: runs of record for 1 of 1; 2 of their 2 jobs verified"
    (cell,) = found["data"]["cells"]
    assert cell["run_of_record"] == registered["run"] and cell["notes"] == [] and not found["data"]["problems"]
    assert cell["commits"] == [git(registered["root"], "rev-parse", "HEAD")] and cell["uncommitted_changes"] is False
    assert cell["members"] == ["m1", "m2"] and cell["members_of_the_experiment"] == 2 and cell["levels"] == ["low"]
    assert cell["toolkit_versions"] == ["stub 0.0"] and cell["runtimes"] == ["none"]
    assert cell["verification"] == {"verified": 2} and cell["jobs_not_ended_cleanly"] == 0
    assert cell["schema"]["valid"] == 2 and cell["schema"]["drafts"] == [Path(records.MODEL_SCHEMA_ID).name.removesuffix(".json")]
    assert cell["experiment_changed"] is False
    # the comparison: computed for the member with a reference, with the reference's error beside the distance
    comparison = cell["comparison"]
    assert comparison["statuses"] == {"computed": 1, "not run": 1}
    low = comparison["largest_distance_by_level"]["low"]
    assert low["member"] == "m1" and low["distance"] >= 0 and low["reference_error"] in (0.001, 0.002)
    assert found["data"]["runs_of_record_file"] == "harness/runs.registry/runs-of-record.yaml"
    # the table: one row, no verdict on the distance, and nothing of a duration
    row = [line for line in found["table"].splitlines() if line.startswith("| tiny/1 ")]
    assert len(row) == 1 and "2 verified" in row[0] and "the host" in row[0] and "2 of 2" in row[0]
    assert f"2 valid ({cell['schema']['drafts'][0]})" in row[0] and f"| {cell['commits'][0][:10]} |" in row[0]
    assert f"low {low['distance']:.3g} ({low['reference_error']:.3g})" in row[0]
    assert "duration" not in found["table"] and "seconds" not in json.dumps(found["data"])
    json.dumps(found["data"])  # everything in the data is JSON's


def test_a_changed_experiment_and_a_newer_run_are_noted_and_are_no_problem(registered):
    name_runs(registered, of_record(registered))
    later = "2099-01-01T00-00_tiny-1"
    shutil.copytree(registered["registry_dir"] / registered["run"], registered["registry_dir"] / later)
    rewrite(registered, later, lambda r: r["when"].update(started="2099-01-01T00:00:00+00:00"))
    experiment = registered["experiment"]
    experiment.write_text(experiment.read_text().replace("A tiny experiment", "A tiny experiment, restated"))
    found = status.read(registered["root"])
    (cell,) = found["data"]["cells"]
    assert cell["experiment_changed"] is True and cell["newer_runs"] == [later]
    assert cell["notes"] == ["the experiment has changed since the run", f"a newer run is in the registry: {later}"]
    assert not found["data"]["problems"] and found["summary"].endswith("; notes on 1")
    assert runner.main(["--registry", str(registered["registry"]), "status"]) == 0


def test_a_record_of_a_draft_the_core_does_not_hold_is_unchecked_and_an_invalid_one_is_a_problem(registered):
    name_runs(registered, of_record(registered))
    unheld = "https://github.com/econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.3.json"
    rewrite(registered, registered["run"], lambda r: r.update({"$schema": unheld}))
    (cell,) = status.read(registered["root"])["data"]["cells"]
    assert cell["schema"]["unchecked"] == 2 and cell["schema"]["valid"] == cell["schema"]["invalid"] == 0
    assert cell["schema"]["drafts"] == ["0.1.0-draft.3"]
    rewrite(registered, registered["run"], lambda r: (r.update({"$schema": records.MODEL_SCHEMA_ID}),
                                                       r["extensions"]["sce-wg-1"]["verification"].update(verdict="perhaps")))
    found = status.read(registered["root"])
    assert found["data"]["cells"][0]["schema"]["invalid"] == 2
    assert len(found["data"]["problems"]) == 1 and "do not validate" in found["data"]["problems"][0]
    assert found["summary"].endswith("; 1 problem")


def test_a_record_of_an_earlier_draft_is_checked_against_that_draft(registered):
    """Draft 7 allowed only the core's three metrics by name, where draft 8 allows an experiment's own: a record that
    names draft 7 and a metric of an experiment's own is invalid under the draft it names, though the core's own
    draft would take it."""
    name_runs(registered, of_record(registered))
    seventh = "https://github.com/econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.7.json"
    rewrite(registered, registered["run"], lambda r: r.update({"$schema": seventh}))
    found = status.read(registered["root"])
    assert found["data"]["cells"][0]["schema"] | {"errors": []} == {"valid": 2, "invalid": 0, "unchecked": 0,
                                                                     "drafts": ["0.1.0-draft.7"], "errors": []}
    assert not found["data"]["problems"]

    def own_metric(record):
        largest = record["extensions"]["sce-wg-1"].get("comparison", {}).get("largest_distance")
        if largest:
            largest["metric"] = "mean_abs_difference"
    rewrite(registered, registered["run"], own_metric)
    found = status.read(registered["root"])
    assert (found["data"]["cells"][0]["schema"]["valid"], found["data"]["cells"][0]["schema"]["invalid"]) == (1, 1)
    assert len(found["data"]["problems"]) == 1
    rewrite(registered, registered["run"], lambda r: r.update({"$schema": records.MODEL_SCHEMA_ID}))
    assert status.read(registered["root"])["data"]["cells"][0]["schema"]["valid"] == 2


def test_the_earlier_drafts_are_held_under_their_own_identifiers():
    schemas = records.held()
    assert records.MODEL_SCHEMA_ID in schemas and len(schemas) == 2 + len(list(records.EARLIER.glob("*.json")))
    for path in records.EARLIER.glob("*.json"):
        identifier = json.loads(path.read_text(encoding="utf-8"))["$id"]
        assert path.name.removeprefix("fork-") == "-".join(identifier.removesuffix(".json").split("/")[-2:]) + ".json"
        assert ("llorracc/sce-wg-1-dev" in identifier) == path.name.startswith("fork-")
    with pytest.raises(ValueError, match="does not hold"):
        records.validate({}, "https://github.com/econ-ark/sce-wg-1/schemas/runs.registry/0.1.0-draft.3.json")


def test_a_mode_of_solution_is_a_cell_of_its_own(registered):
    rewrite(registered, registered["run"], lambda r: r["extensions"]["sce-wg-1"].update(mode="markov"))
    name_runs(registered, of_record(registered, mode="markov"))
    found = status.read(registered["root"])
    (cell,) = found["data"]["cells"]  # and no row for the toolkit without a mode
    assert cell["mode"] == "markov" and cell["verification"] == {"verified": 2} and not found["data"]["problems"]
    assert "| tiny/1 | stub | markov |" in found["table"]


def test_what_is_wrong_with_the_file_of_runs_of_record_is_a_problem(registered, capsys):
    name_runs(registered,
              of_record(registered),
              of_record(registered),                                                  # a second entry for the cell
              {"experiment": "tiny/1", "toolkit": "other", "run": registered["run"]},  # no such toolkit, and no record
              {"experiment": "tiny/1", "toolkit": "stub", "mode": "markov", "run": "2000-01-01T00-00_tiny-1"},  # no folder
              {"experiment": "tiny/1", "toolkit": "stub", "run": registered["run"], "score": "9"})              # not an entry
    found = status.read(registered["root"])
    problems = "\n".join(found["data"]["problems"])
    assert "more than one entry for stub on tiny/1" in problems
    assert "other on tiny/1 names a toolkit the registry file does not have" in problems
    assert "a folder the registry does not hold" in problems and "an entry is not an experiment" in problems
    assert "Problems:" in found["table"] and f"; {len(found['data']['problems'])} problems" in found["summary"]
    # the well-formed entry is still read, and the command's exit status is the problems'
    assert [c["toolkit"] for c in found["data"]["cells"] if c.get("verification")] == ["stub"]
    assert runner.main(["--registry", str(registered["registry"]), "status"]) == 1
    assert "Problems:" in capsys.readouterr().out
    (registered["registry_dir"] / status.OF_RECORD).write_text("runs_of_record: {a: 1, a: 2}\n")
    assert "not read" in status.read(registered["root"])["data"]["problems"][0]


def test_a_checkout_the_runner_would_refuse_is_an_exception_and_never_an_exit(registered, tmp_path):
    with pytest.raises(ValueError, match="no registry file"):
        status.read(tmp_path / "nowhere")
    text = registered["registry"].read_text()
    registered["registry"].write_text(text.replace("registry_dir:", "registry_folder:"))
    with pytest.raises(ValueError, match="unknown keys"):
        status.read(registered["root"])


def test_remark_finds_the_reader_by_the_kind(registered):
    found = [point for point in metadata.entry_points(group="remark.status") if point.name == status.KIND]
    assert len(found) == 1 and found[0].load() is status.read
