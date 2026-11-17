"""The tests of a reference solution as its own kind of object, on the tiny model repository of test_core.py with a
second entry: `stub`, numerical, whose kink approaches the reference's with the level while its rule stays a fixed
distance from it, and `formula`, exact, which writes the reference's own numbers for the member that pins one.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
import textwrap
from pathlib import Path

import pytest
import yaml

from test_core import RESULTS_SCHEMA, REFERENCE_M1, command, git, make_model, run
from wg1core import comparator, experiment, records, runner

FORMULA_ADAPTER = textwrap.dedent('''
    """A stand-in exact entry: at every level it writes the numbers of the reference pinned for the first member,
    solving nothing and reading no setting."""
    import argparse, json
    from pathlib import Path
    from wg1core import canonical
    ap = argparse.ArgumentParser()
    ap.add_argument("member"); ap.add_argument("--out", required=True); ap.add_argument("--level", required=True)
    ap.add_argument("--request", required=True)
    a = ap.parse_args()
    member, request = canonical.load_strict(Path(a.member).read_text()), canonical.load_strict(Path(a.request).read_text())
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps({"toolkit": {"name": "formula", "version": "0.0"},
        "types": [{"kink": 1.30, "rule": {"c": [0.45, 0.68]}}],
        "parameter_file_sha256": canonical.model_hash(member), "request_file_sha256": canonical.model_hash(request)}))
    (out / "methods.yaml").write_text("policy: closed-form\\n")
    (out / "settings.yaml").write_text("{}\\n")
''')


def check(id: str, compare: str, quantity: str, expect, metric: str = "max_abs_difference", **more) -> dict:
    return {"id": id, "statement": "A check of the tests.", "compare": compare, "quantity": quantity, "metric": metric,
            "expect": expect, **more}


CHECKS = [
    check("stub_approaches_the_reference", "reference", "types[].kink", "falls_with_level", kind="numerical"),
    check("stub_rule_is_near_the_reference", "reference", "types[].rule.c", {"at_most": 0.01}, kind="numerical"),
    check("formula_is_the_reference", "reference", "types[].kink", "within_reference_error", kind="exact"),
    check("formula_rule_is_the_reference", "reference", "types[].rule.c", "within_reference_error",
          metric="max_relative_to_reference", floor=0.5, kind="exact"),
    check("toolkits_agree", "toolkits", "types[].kink", "falls_with_level"),
    check("levels_converge", "levels", "types[].kink", {"at_most": 1.0}),
    check("kinks_agree", "members", "types[].kink", {"at_most": 1.0}, pairs=[["m1", "m2"]]),
]
REFERENCE = {"kind": "exact", "produced_by": "the tests' own formula",
             "errors": {"types[].kink": 0.001,
                        "types[].rule.c": {"max_abs_difference": 0.002, "max_relative_to_reference": 0.004}}}


def with_two_entries(tmp_path: Path, checks: list | None = None, reference: dict | None = None) -> dict:
    """The tiny model with an exact entry beside the numerical one, three levels, and the first member's reference
    given a kind, a producer and errors by metric; committed."""
    model = make_model(tmp_path)
    harness = model["root"] / "harness"
    (harness / "formula_adapter.py").write_text(FORMULA_ADAPTER)
    registry = yaml.safe_load(model["registry"].read_text())
    registry["toolkits"]["formula"] = {"adapter": "formula_adapter.py", "code": ["formula_adapter.py"], "kind": "exact",
                                       "levels": {"low": 1, "medium": 2, "high": 3}, "threads": 1}
    model["registry"].write_text(yaml.safe_dump(registry))
    exp = yaml.safe_load(model["experiment"].read_text())
    exp["levels"] = ["low", "medium", "high"]
    exp["members"][0]["reference"].update(copy.deepcopy(REFERENCE if reference is None else reference))
    exp["checks"] = copy.deepcopy(CHECKS if checks is None else checks)
    exp["reference_quantities"] = [{"quantity": "types[].kink", "metric": "max_abs_difference"},
                                   {"quantity": "types[].rule.c", "metric": "max_relative_to_reference", "floor": 0.5}]
    model["experiment"].write_text(yaml.safe_dump(exp, sort_keys=False))
    git(model["root"], "add", "-A")
    git(model["root"], "commit", "-q", "-m", "an exact entry beside the numerical one")
    return model


def run_both(model: dict, *extra: str) -> int:
    return runner.main(["--registry", str(model["registry"]), "run", str(model["experiment"]), "--toolkits", "stub,formula",
                        "--out", str(model["out"]), *extra])


def comparison(model: dict) -> dict:
    return json.loads((model["out"] / "comparison.json").read_text())


# What the tests' entries hold, for the checks evaluated without a run: results[toolkit][member][level].
def results_of_the_entries() -> dict:
    stub = {level: {"types": [{"kink": 1.25 + 0.01 * n + 0.009, "rule": {"c": [0.45, 0.675]}}]}
            for n, level in enumerate(("low", "medium", "high"), start=1)}
    formula = {level: {"types": [copy.deepcopy(REFERENCE_M1["types"][0])]} for level in ("low", "medium", "high")}
    return {"stub": {"m1": stub}, "formula": {"m1": formula}}


def evaluate(c: dict, errors: dict | None = None, results: dict | None = None) -> dict:
    stated = {"results_file": "m1.reference.json", "results_sha256": "0" * 64, "errors": errors if errors is not None else REFERENCE["errors"]}
    references = {"m1": {"stated": stated, "results": copy.deepcopy(REFERENCE_M1), "sha256": "0" * 64, "problem": None}}
    return comparator.evaluate_check(c, results or results_of_the_entries(), ["m1", "m2"], ["low", "medium", "high"],
                                     {"stub": "numerical", "formula": "exact"}, references)


def recommit(model: dict, change, reference: bytes | None = None) -> None:
    """The experiment file changed, the first member's reference file replaced and pinned again if given, committed."""
    exp = yaml.safe_load(model["experiment"].read_text())
    if reference is not None:
        (model["experiment"].parent / "m1.reference.json").write_bytes(reference)
        exp["members"][0]["reference"]["results_sha256"] = hashlib.sha256(reference).hexdigest()
    change(exp)
    model["experiment"].write_text(yaml.safe_dump(exp, sort_keys=False))
    git(model["root"], "add", "-A")
    git(model["root"], "commit", "-q", "-m", "the experiment changed")


def test_an_entry_has_a_kind_and_the_run_carries_it(tmp_path):
    model = with_two_entries(tmp_path)
    m = runner.Model(model["registry"])
    assert m.toolkits["stub"]["kind"] == "numerical" and m.toolkits["formula"]["kind"] == "exact"
    assert run_both(model, "--levels", "low") == 0
    manifest = json.loads((model["out"] / "manifest.json").read_text())
    assert manifest["toolkits"]["stub"]["kind"] == "numerical" and manifest["toolkits"]["formula"]["kind"] == "exact"
    for toolkit, kind in (("stub", "numerical"), ("formula", "exact")):
        folder = model["out"] / toolkit / "m1" / "low"
        record = json.loads((folder / "record.json").read_text())
        assert record["extensions"]["sce-wg-1"]["entry_kind"] == kind
        assert record["$schema"] == records.MODEL_SCHEMA_ID
        records.validate(record)
        # a numerical entry's fingerprint is what it was before entries had kinds; an exact entry's names its kind
        assert json.loads((folder / "job.json").read_text())["fingerprint"].get("kind") == (None if kind == "numerical" else "exact")
    registry = yaml.safe_load(model["registry"].read_text())
    registry["toolkits"]["formula"]["kind"] = "analytic"
    model["registry"].write_text(yaml.safe_dump(registry))
    with pytest.raises(SystemExit, match="kind is 'analytic'"):
        runner.Model(model["registry"])


def test_a_check_against_the_reference_holds_each_kind_of_entry(tmp_path):
    model = with_two_entries(tmp_path)
    assert run_both(model) == 0 and command(model, "verify") == 0 and command(model, "compare") == 0
    report = comparison(model)
    checks = {c["id"]: c for c in report["checks"]}
    # the numerical entry: its kink's distance from the reference falls with the level
    falls = checks["stub_approaches_the_reference"]
    (value,) = falls["values"]
    assert falls["verdict"] == "pass" and falls["kind"] == "numerical"
    assert (value["toolkit"], value["kind"], value["member"]) == ("stub", "numerical", "m1")
    assert list(value["values"]) == ["low", "medium", "high"]
    assert [value["values"][lv] for lv in ("low", "medium", "high")] == pytest.approx([0.031, 0.021, 0.011])
    assert value["at"] == {"low": 0, "medium": 0, "high": 0} and value["reference_error"] == 0.001
    near = checks["stub_rule_is_near_the_reference"]
    assert near["verdict"] == "pass" and near["values"][0]["at"]["high"] == 1  # the rule's second number is the one off
    # the exact entry: within the reference's error, under each check's own metric
    for name, error in (("formula_is_the_reference", 0.001), ("formula_rule_is_the_reference", 0.004)):
        (value,) = checks[name]["values"]
        assert checks[name]["verdict"] == "pass" and value["toolkit"] == "formula" and value["kind"] == "exact"
        assert set(value["values"].values()) == {0.0} and value["reference_error"] == error
    assert checks["formula_rule_is_the_reference"]["floor"] == 0.5
    # the checks between toolkits and between levels leave the exact entry out
    assert checks["toolkits_agree"]["verdict"] == "not applicable" and checks["toolkits_agree"]["values"] == []
    assert {v["toolkit"] for v in checks["levels_converge"]["values"]} == {"stub"}
    # the check between members is every entry's, as before
    assert {v["toolkit"] for v in checks["kinks_agree"]["values"]} == {"stub", "formula"}
    assert report["failed"] is False


def test_the_report_states_the_reference_and_the_kinds(tmp_path):
    reference = {**REFERENCE, "kind": "numerical", "produced_by": {"toolkit": "formula", "commit": "0123abc"},
                 "certified_by": ["a second solve", {"toolkit": "another", "settings": "its finest rung"}]}
    model = with_two_entries(tmp_path, reference=reference)
    assert run_both(model, "--levels", "low") == 0 and command(model, "compare") == 0
    report = comparison(model)
    assert report["entries"] == {"stub": "numerical", "formula": "exact"}
    (ref,) = report["member_references"]
    assert ref["member"] == "m1" and ref["kind"] == "numerical" and ref["status"] == "loaded"
    assert ref["produced_by"] == {"toolkit": "formula", "commit": "0123abc"} and len(ref["certified_by"]) == 2
    assert ref["errors"] == REFERENCE["errors"] and ref["producers_among_the_entries"] == ["formula"]
    # the distances from the reference keep their part and carry no verdict; each says where its largest sits
    by_job = {(j["toolkit"], j["member"]): j for j in report["reference"]}
    stub, formula = by_job[("stub", "m1")], by_job[("formula", "m1")]
    assert stub["kind"] == "numerical" and formula["kind"] == "exact" and "verdict" not in stub
    rows = {r["quantity"]: r for r in stub["distances"]}
    assert rows["types[].kink"]["at"] == 0 and rows["types[].kink"]["reference_error"] == 0.001
    rule = rows["types[].rule.c"]
    assert rule["metric"] == "max_relative_to_reference" and rule["floor"] == 0.5 and rule["at"] == 1
    assert rule["distance"] == pytest.approx(0.005 / 0.68) and rule["reference_error"] == 0.004  # the error under that metric
    assert by_job[("stub", "m2")]["status"] == "not run"
    # each job's record still validates, the relative distance among what its block may hold
    record = json.loads((model["out"] / "stub" / "m1" / "low" / "record.json").read_text())
    records.validate(record)
    assert "at" not in record["extensions"]["sce-wg-1"]["comparison"]["largest_distance"]
    md = (model["out"] / "comparison.md").read_text()
    assert "## The reference" in md and "| m1 | numerical | formula, commit 0123abc |" in md
    assert "formula, is also an entry of this run" in md and "The entries: stub, numerical, formula, exact." in md
    assert "| toolkit | kind | member | level |" in md and "max_relative_to_reference, floor 0.5" in md


def test_a_fall_that_has_reached_the_references_error_counts_and_only_against_a_reference():
    falls = check("rule_falls", "reference", "types[].rule.c", "falls_with_level", kind="numerical")
    # the stub's rule stays 0.005 from the reference at every level: no fall, and above the stated error
    stays = evaluate(falls)
    assert stays["verdict"] == "fail" and list(stays["values"][0]["values"].values()) == pytest.approx([0.005] * 3)
    # with the reference's own error at 0.01 the entry is as close as the reference resolves, at every level
    assert evaluate(falls, {"types[].rule.c": 0.01})["verdict"] == "pass"
    # an error stated for another metric is no error under this one
    assert evaluate(falls, {"types[].rule.c": {"max_relative_to_reference": 0.01}})["verdict"] == "fail"
    assert "reference_error" not in evaluate(falls, {})["values"][0]
    # between levels the fall stays strict: the rule does not move, and that is no fall
    strict = evaluate(check("rule_converges", "levels", "types[].rule.c", "falls_with_level"))
    assert strict["verdict"] == "fail" and [v["toolkit"] for v in strict["values"]] == ["stub"]


def test_an_exact_entry_is_held_to_the_error_stated_under_the_checks_metric():
    within = check("formula_conforms", "reference", "types[].rule.c", "within_reference_error",
                   metric="max_relative_to_reference", floor=0.5, kind="exact")
    assert evaluate(within)["verdict"] == "pass"
    unstated = evaluate(within, {"types[].rule.c": 0.002})  # a bare number is the error under the absolute metric alone
    assert unstated["verdict"] == "error" and "states no error for types[].rule.c under max_relative_to_reference" in unstated["errors"][0]
    # held to the numerical entry's numbers, the same check fails: 0.005/0.68 is above 0.004
    results = results_of_the_entries()
    results["formula"] = results["stub"]
    stated = {"results_file": "m1.reference.json", "results_sha256": "0" * 64, "errors": REFERENCE["errors"]}
    references = {"m1": {"stated": stated, "results": copy.deepcopy(REFERENCE_M1), "sha256": "0" * 64, "problem": None}}
    failed = comparator.evaluate_check(within, results, ["m1"], ["low", "medium", "high"], {"formula": "exact"}, references)
    assert failed["verdict"] == "fail" and failed["values"][0]["at"]["low"] == 1
    # a reference that did not load, or that answers another question, is an error and never a failure
    references["m1"].update(results=None, problem="no reference file m1.reference.json")
    assert comparator.evaluate_check(within, results, ["m1"], ["low"], {"formula": "exact"}, references)["verdict"] == "error"
    references["m1"].update(results={**copy.deepcopy(REFERENCE_M1), "request_file_sha256": "f" * 64}, problem=None)
    other = comparator.evaluate_check(within, results, ["m1"], ["low"], {"formula": "exact"}, references, ["request_file_sha256"])
    assert other["verdict"] == "error" and "does not answer the same question" in other["errors"][0]


@pytest.mark.parametrize("content, problem", [(b"null", "holds no results"), (b"not json", "is not JSON")])
def test_a_reference_that_cannot_be_read_is_an_error_and_never_a_crash(tmp_path, content, problem):
    model = with_two_entries(tmp_path)
    recommit(model, lambda exp: None, reference=content)
    assert run_both(model, "--levels", "low") == 0 and command(model, "compare") == 1
    report = comparison(model)
    (ref,) = report["member_references"]
    assert ref["status"] == "error" and problem in ref["problem"]
    assert {c["verdict"] for c in report["checks"] if c["compare"] == "reference"} == {"error"}
    assert {j["status"] for j in report["reference"] if j["member"] == "m1"} == {"error"}
    assert problem in (model["out"] / "comparison.md").read_text()
    # the reference of a member the run does not hold is not read, and stops nothing
    shutil.rmtree(model["out"])
    assert run_both(model, "--levels", "low", "--members", "m2") == 0 and command(model, "compare") == 0
    assert comparison(model)["member_references"] == []


def test_a_value_that_is_not_a_number_makes_a_check_against_the_reference_an_error():
    results = results_of_the_entries()
    for at_level in results["formula"]["m1"].values():
        at_level["types"][0]["rule"]["c"][1] = float("nan")
    within = check("formula_conforms", "reference", "types[].rule.c", "within_reference_error", kind="exact")
    unread = evaluate(within, results=results)
    assert unread["verdict"] == "error" and "not a number, at 1" in unread["errors"][0]
    # a largest distance alone passes over such a value when it is not the first, which is why the check refuses it
    passed_over = ([1.0, float("nan"), 3.0], [1.0, 2.0, 3.0], "max_abs_difference")
    assert comparator.distance(*passed_over) == 0.0
    with pytest.raises(ValueError, match="not a number, at 1"):
        comparator.distance_at(*passed_over, strict=True)


def test_a_bare_error_is_shown_under_the_metrics_of_before_and_never_relative_to_the_reference():
    stub = results_of_the_entries()["stub"]["m1"]["low"]
    quantities = [{"quantity": "types[].rule.c", "metric": "max_abs_difference"},
                  {"quantity": "types[].rule.c", "metric": "max_relative_difference"},
                  {"quantity": "types[].rule.c", "metric": "max_relative_to_reference", "floor": 0.5}]
    bare = comparator.reference_distances(stub, REFERENCE_M1, quantities, {"types[].rule.c": 0.002})
    assert [row.get("reference_error") for row in bare] == [0.002, 0.002, None]
    keyed = comparator.reference_distances(stub, REFERENCE_M1, quantities, {"types[].rule.c": {"max_relative_to_reference": 0.004}})
    assert [row.get("reference_error") for row in keyed] == [None, None, 0.004]
    assert [row["at"] for row in keyed] == [1, 1, 1] and keyed[2]["floor"] == 0.5


def test_a_record_names_the_floor_its_largest_distance_was_taken_with(tmp_path):
    model = with_two_entries(tmp_path)
    relative = {"quantity": "types[].rule.c", "metric": "max_relative_to_reference", "floor": 0.5}
    recommit(model, lambda exp: exp.update(reference_quantities=[relative]))
    assert run_both(model, "--levels", "low") == 0 and command(model, "compare") == 0
    record = json.loads((model["out"] / "stub" / "m1" / "low" / "record.json").read_text())
    largest = record["extensions"]["sce-wg-1"]["comparison"]["largest_distance"]
    assert largest == {"quantity": "types[].rule.c", "metric": "max_relative_to_reference", "floor": 0.5,
                       "distance": pytest.approx(0.005 / 0.68), "reference_error": 0.004}
    records.validate(record)


def test_a_check_names_its_levels_in_the_order_its_expectation_reads_them():
    falls = check("kink_falls", "reference", "types[].kink", "falls_with_level", kind="numerical")
    two = evaluate({**falls, "levels": ["low", "high"]})
    assert two["verdict"] == "pass" and list(two["values"][0]["values"]) == ["low", "high"] and two["levels"] == ["low", "high"]
    backwards = evaluate({**falls, "levels": ["high", "low"]})
    assert backwards["verdict"] == "fail" and list(backwards["values"][0]["values"]) == ["high", "low"]
    assert evaluate({**falls, "levels": ["high"]})["verdict"] == "not applicable"  # one level is no fall
    between = evaluate(check("kink_moves", "levels", "types[].kink", {"at_most": 1.0}, levels=["low", "high"]))
    assert list(between["values"][0]["values"]) == ["low-high"]


def test_the_metric_relative_to_the_reference_divides_by_the_references_magnitude_above_a_floor():
    a = {"types": [{"kink": 0.0, "rule": {"c": [1.0e-6, 2.0]}}]}
    r = {"types": [{"kink": 0.0, "rule": {"c": [2.0e-6, 1.0]}}]}
    assert comparator.compare(a, r, "types[].rule.c", "max_relative_to_reference", 1.0e-9) == 1.0  # 1 over 1, at the second
    assert comparator.compare_at(a, r, "types[].rule.c", "max_relative_to_reference", 1.0e-9) == (1.0, 1)
    assert comparator.compare_at(a, r, "types[].rule.c", "max_relative_to_reference", 1.0e-7)[0] == 1.0
    assert comparator.compare_at(a, r, "types[].rule.c", "max_abs_difference") == (1.0, 1)
    # the first number is half the reference's away, where the metric of before calls it a millionth
    assert comparator.distance([1.0e-6], [2.0e-6], "max_relative_to_reference", 1.0e-9) == pytest.approx(0.5)
    assert comparator.distance([1.0e-6], [2.0e-6], "max_relative_difference") == pytest.approx(1.0e-6)
    assert comparator.distance([0.5], [0.0], "max_relative_to_reference", 0.25) == 2.0  # a reference of zero, divided by the floor
    with pytest.raises(ValueError, match="floor"):
        comparator.distance([1.0], [1.0], "max_relative_to_reference")


def test_the_experiment_checker_refuses_what_the_design_forbids(tmp_path):
    model = with_two_entries(tmp_path)
    exp, folder = experiment.load(model["experiment"]), model["experiment"].parent
    assert experiment.problems(exp, folder, RESULTS_SCHEMA) == []

    def problems(c: dict, change=None) -> str:
        broken = json.loads(json.dumps(exp))
        broken["checks"] = [c]
        if change:
            change(broken)
        return "\n".join(experiment.problems(broken, folder, RESULTS_SCHEMA))

    reference = check("c", "reference", "types[].kink", {"at_most": 1.0}, kind="numerical")
    assert problems(reference) == ""
    assert "'kind' is a required property" in problems({k: v for k, v in reference.items() if k != "kind"})
    # a check that lacks a key is told of that key, and not of the rules that hang on it
    lacking = problems({k: v for k, v in reference.items() if k != "metric"})
    assert "'metric' is a required property" in lacking and "floor" not in lacking and "'reference' was expected" not in lacking
    assert problems(check("c", "toolkits", "types[].kink", {"at_most": 1.0}, kind="numerical")) != ""  # a kind only against the reference
    assert problems({**reference, "expect": "within_reference_error"}) != ""                           # only an exact entry
    assert problems({**reference, "expect": "falls_with_level", "kind": "exact"}) != ""                # no ladder to fall along
    assert problems(check("c", "levels", "types[].kink", "within_reference_error")) != ""
    relative = {**reference, "metric": "max_relative_to_reference"}
    assert "'floor' is a required property" in problems(relative) and problems({**relative, "floor": 1.0e-9}) == ""
    assert problems({**reference, "floor": 1.0e-9}) != ""                                              # a floor only with that metric
    assert problems(check("c", "toolkits", "types[].kink", {"at_most": 1.0}, metric="max_relative_to_reference", floor=1.0)) != ""
    assert "c: the experiment has no level high" in problems({**reference, "levels": ["low", "high"]},
                                                              lambda e: e.update(levels=["low"]))
    assert "c: m2 pins no reference" in problems({**reference, "members": ["m2"]})
    assert "no member pins one" in problems(reference, lambda e: e["members"][0].pop("reference"))
    conforms = check("c", "reference", "types[].rule.c", "within_reference_error", kind="exact")
    assert problems(conforms) == ""
    assert "c: m1's reference states no error for types[].rule.c under max_relative_to_reference" in problems(
        {**conforms, "metric": "max_relative_to_reference", "floor": 0.5},
        lambda e: e["members"][0]["reference"]["errors"].update({"types[].rule.c": 0.002}))
    # the reference's own statements: a kind of the two, a producer as words or as a toolkit, errors by a metric there is
    for key, value in (("kind", "analytic"), ("produced_by", {"commit": "0123abc"}), ("certified_by", []),
                       ("errors", {"types[].kink": {"max_distance": 0.1}})):
        assert problems(reference, lambda e: e["members"][0]["reference"].update({key: value})) != "", key
    assert experiment.stated_error({"errors": {"q": 0.1}}, "q", "max_abs_difference") == 0.1
    assert experiment.stated_error({"errors": {"q": 0.1}}, "q", "max_relative_difference") is None
    assert experiment.stated_error({"errors": {"q": {"max_relative_difference": 0.2}}}, "q", "max_relative_difference") == 0.2
    assert experiment.stated_error({}, "q", "max_abs_difference") is None


def test_an_experiment_of_the_earlier_form_compares_as_before(tmp_path):
    """One entry with no kind, a reference with bare errors and no kind, the checks of before: the verdicts, the
    distances and the keys a reader of the earlier report used are what they were."""
    model = make_model(tmp_path)
    assert run(model, "--levels", "low") == 0 and command(model, "verify") == 0 and command(model, "compare") == 0
    manifest = json.loads((model["out"] / "manifest.json").read_text())
    assert manifest["toolkits"]["stub"]["kind"] == "numerical"
    assert "kind" not in json.loads((model["out"] / "stub" / "m1" / "low" / "job.json").read_text())["fingerprint"]
    report = comparison(model)
    assert {c["id"]: c["verdict"] for c in report["checks"]} == {"kinks_agree": "pass", "rules_converge": "not applicable"}
    assert set(report["checks"][0]) == {"id", "statement", "compare", "quantity", "metric", "expect", "verdict", "values", "errors"}
    m1 = next(j for j in report["reference"] if j["member"] == "m1")
    assert m1["status"] == "computed" and m1["kind"] == "numerical"
    rows = {r["quantity"]: r for r in m1["distances"]}
    assert rows["types[].kink"]["distance"] == pytest.approx(abs(1.25 + 0.01 + 0.009 - 1.30))
    # a bare error stays beside the quantity's distance under the metric of before, as it was shown
    assert rows["types[].rule.c"]["metric"] == "max_relative_difference" and rows["types[].rule.c"]["reference_error"] == 0.002
    assert report["member_references"][0]["member"] == "m1" and "kind" not in report["member_references"][0]
    # a manifest written before entries had kinds states none, and the comparison reads every entry as numerical
    del manifest["toolkits"]["stub"]["kind"]
    (model["out"] / "manifest.json").write_text(json.dumps(manifest))
    assert command(model, "compare") == 0 and comparison(model)["entries"] == {"stub": "numerical"}
    assert hashlib.sha256(model["experiment"].read_bytes()).hexdigest()  # the experiment file itself is untouched
