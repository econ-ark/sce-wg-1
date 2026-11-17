"""The tests of the metrics an experiment defines, on the two-entry model of test_reference.py: a pointwise distance
with an aggregate against values computed by hand, a function of the model's repository, the three the core names as
such pairs, what the checker of experiments refuses, and a run whose checks and records use a defined metric.

    uv run --project core --with pytest pytest -q core/tests
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import textwrap

import pytest

from test_core import RESULTS_SCHEMA, REFERENCE_M1, command
from test_reference import check, comparison, evaluate, recommit, results_of_the_entries, run_both, with_two_entries
from wg1core import comparator, experiment, metrics, records

A = [1.0, 2.0, 4.0, 8.0]            # an entry's numbers
R = [1.1, 2.4, 4.2, 7.7]            # the reference's
EACH = [0.1, 0.4, 0.2, 0.3]         # their absolute differences, to rounding

FUNCTIONS = textwrap.dedent('''
    """Metrics of the tests' own, as a model repository would write them."""
    def power_mean(entry, reference, power=1):
        each = [abs(x - y) ** power for x, y in zip(entry, reference)]
        return (sum(each) / len(each)) ** (1 / power), max(range(len(each)), key=each.__getitem__)

    def count_off(entry, reference, by=0.0):
        return sum(1 for x, y in zip(entry, reference) if abs(x - y) > by)

    def negative(entry, reference):
        return -1.0

    def fails(entry, reference):
        raise RuntimeError("no")
''')


def defined(**definitions) -> dict:
    return {name: {"definition": definition} for name, definition in definitions.items()}


def test_a_pointwise_distance_with_an_aggregate_against_values_by_hand():
    d = defined(mean_abs={"pointwise": "abs_difference", "aggregate": "mean"},
                rms_abs={"pointwise": "abs_difference", "aggregate": "rms"},
                median_abs={"pointwise": "abs_difference", "aggregate": "quantile", "q": 0.5},
                most_abs={"pointwise": "abs_difference", "aggregate": "quantile", "q": 0.75},
                all_abs={"pointwise": "abs_difference", "aggregate": "quantile", "q": 1},
                mean_to_reference={"pointwise": "relative_to_reference", "floor": 5.0, "aggregate": "mean"},
                rms_relative={"pointwise": "relative_difference", "aggregate": "rms"})
    assert comparator.distance_at(A, R, "mean_abs", defined=d) == (pytest.approx(0.25), 1)       # at: the largest term's index
    assert comparator.distance(A, R, "rms_abs", defined=d) == pytest.approx(math.sqrt(0.30 / 4))
    # a quantile with no interpolation: the smallest distance with at least q of them at or below it
    assert comparator.distance(A, R, "median_abs", defined=d) == pytest.approx(0.2)
    assert comparator.distance(A, R, "most_abs", defined=d) == pytest.approx(0.3)
    assert comparator.distance(A, R, "all_abs", defined=d) == pytest.approx(0.4)
    # relative to the reference above a floor of five: the first three are divided by the floor, the last by 7.7
    assert comparator.distance(A, R, "mean_to_reference", defined=d) == pytest.approx((0.1 / 5 + 0.4 / 5 + 0.2 / 5 + 0.3 / 7.7) / 4)
    assert comparator.distance(A, R, "rms_relative", defined=d) == pytest.approx(
        math.sqrt(((0.1 / 1) ** 2 + (0.4 / 2) ** 2 + (0.2 / 4) ** 2 + (0.3 / 8) ** 2) / 4))
    # nine tenths of ten numbers is nine of them, whatever the fraction's binary form
    ten = [float(i) for i in range(1, 11)]
    assert metrics.aggregate(ten, "quantile", 0.9) == 9.0 and metrics.aggregate(ten, "quantile", 0.91) == 10.0
    assert metrics.aggregate(ten, "quantile", 0.1) == 1.0 and metrics.aggregate(ten, "quantile", 0.05) == 1.0
    with pytest.raises(ValueError, match="unknown metric mean_abs"):
        comparator.distance(A, R, "mean_abs")


def test_the_cores_three_are_the_three_pointwise_distances_with_the_largest():
    pairs = defined(a={"pointwise": "abs_difference", "aggregate": "max"},
                    b={"pointwise": "relative_difference", "aggregate": "max"},
                    c={"pointwise": "relative_to_reference", "floor": 0.25, "aggregate": "max"})
    rng = random.Random(7)
    for _ in range(200):
        n = rng.randint(1, 12)
        a, r = [rng.uniform(-3, 3) for _ in range(n)], [rng.uniform(-3, 3) for _ in range(n)]
        assert comparator.distance_at(a, r, "max_abs_difference") == comparator.distance_at(a, r, "a", defined=pairs)
        assert comparator.distance_at(a, r, "max_relative_difference") == comparator.distance_at(a, r, "b", defined=pairs)
        assert comparator.distance_at(a, r, "max_relative_to_reference", 0.25) == comparator.distance_at(a, r, "c", defined=pairs)
    assert set(metrics.BUILT_IN) == {"max_abs_difference", "max_relative_difference", "max_relative_to_reference"}


def test_a_bare_error_is_never_shown_under_a_defined_metric():
    d = defined(mean_abs={"pointwise": "abs_difference", "aggregate": "mean"})
    quantities = [{"quantity": "types[].rule.c", "metric": "max_abs_difference"}, {"quantity": "types[].rule.c", "metric": "mean_abs"}]
    stub = results_of_the_entries()["stub"]["m1"]["low"]
    bare = comparator.reference_distances(stub, REFERENCE_M1, quantities, {"types[].rule.c": 0.002}, d)
    assert [row.get("reference_error") for row in bare] == [0.002, None]
    keyed = comparator.reference_distances(stub, REFERENCE_M1, quantities, {"types[].rule.c": {"mean_abs": 0.0005}}, d)
    assert [row.get("reference_error") for row in keyed] == [None, 0.0005]


def test_a_defined_metric_refuses_a_value_that_is_not_a_number_wherever_it_is_used():
    d = defined(mean_abs={"pointwise": "abs_difference", "aggregate": "mean"})
    with pytest.raises(ValueError, match="not a number, at 1"):
        comparator.distance([1.0, float("nan")], [1.0, 2.0], "mean_abs", defined=d)
    assert comparator.distance([1.0, float("nan")], [1.0, 2.0], "max_abs_difference") == 0.0  # the core's, as it always was


def with_metrics(tmp_path, definitions: dict, checks: list, errors: dict | None = None, quantities: list | None = None) -> dict:
    """The two-entry model with a file of functions beside the experiment file, the metrics defined, and the checks
    given; a function's definition is given its file's hash."""
    model = with_two_entries(tmp_path)
    (model["experiment"].parent / "tiny_metrics.py").write_text(FUNCTIONS)
    digest = hashlib.sha256(FUNCTIONS.encode()).hexdigest()
    definitions = {name: ({**d, "sha256": digest} if "function" in d else d) for name, d in definitions.items()}

    def change(exp):
        exp["metrics"] = definitions
        exp["checks"] = checks
        if errors is not None:
            exp["members"][0]["reference"]["errors"] = errors
        if quantities is not None:
            exp["reference_quantities"] = quantities
    recommit(model, change)
    return model


def test_a_run_whose_checks_and_records_use_the_metrics_the_experiment_defines(tmp_path):
    definitions = {"mean_abs": {"pointwise": "abs_difference", "aggregate": "mean", "description": "the average over the points"},
                   "power_mean": {"function": "tiny_metrics.py:power_mean", "parameters": {"power": 2}},
                   "count_off": {"function": "tiny_metrics.py:count_off", "parameters": {"by": 0.001}}}
    checks = [check("stub_rule_is_near_on_average", "reference", "types[].rule.c", {"at_most": 0.003}, metric="mean_abs", kind="numerical"),
              check("formula_is_the_reference_on_average", "reference", "types[].rule.c", "within_reference_error",
                    metric="mean_abs", kind="exact"),
              check("stub_rule_in_root_mean_square", "reference", "types[].rule.c", {"at_most": 0.004}, metric="power_mean", kind="numerical"),
              check("stub_kink_falls_on_average", "reference", "types[].kink", "falls_with_level", metric="mean_abs", kind="numerical"),
              check("how_many_points_are_off", "levels", "types[].rule.c", {"at_most": 0.5}, metric="count_off")]
    errors = {"types[].kink": 0.001, "types[].rule.c": {"max_abs_difference": 0.002, "mean_abs": 0.0005}}
    quantities = [{"quantity": "types[].rule.c", "metric": "mean_abs"}, {"quantity": "types[].rule.c", "metric": "count_off"}]
    model = with_metrics(tmp_path, definitions, checks, errors, quantities)
    assert experiment.problems(experiment.load(model["experiment"]), model["experiment"].parent, RESULTS_SCHEMA) == []
    assert run_both(model) == 0 and command(model, "verify") == 0 and command(model, "compare") == 0
    report = comparison(model)
    by_id = {c["id"]: c for c in report["checks"]}
    assert {c["verdict"] for c in report["checks"]} == {"pass"}
    # the stub's rule is 0.005 off at one of its two numbers: 0.0025 on average, 0.005/sqrt(2) in root mean square
    mean = by_id["stub_rule_is_near_on_average"]["values"][0]
    assert mean["values"]["low"] == pytest.approx(0.0025) and mean["at"]["low"] == 1 and mean["reference_error"] == 0.0005
    assert by_id["stub_rule_in_root_mean_square"]["values"][0]["values"]["high"] == pytest.approx(0.005 / math.sqrt(2))
    assert by_id["formula_is_the_reference_on_average"]["values"][0]["values"] == {"low": 0.0, "medium": 0.0, "high": 0.0}
    # a function that names no index leaves `at` out, in a check's values and in the table's rows
    job = next(j for j in report["reference"] if (j["toolkit"], j["member"], j["level"]) == ("stub", "m1", "low"))
    rows = {r["metric"]: r for r in job["distances"]}
    assert rows["mean_abs"]["distance"] == pytest.approx(0.0025) and rows["mean_abs"]["at"] == 1 and rows["mean_abs"]["reference_error"] == 0.0005
    assert rows["count_off"]["distance"] == 1.0 and "at" not in rows["count_off"] and "reference_error" not in rows["count_off"]
    # the report states what each defined metric is, a function's with its file's hash
    assert report["metrics"]["mean_abs"]["aggregate"] == "mean"
    assert report["metrics"]["power_mean"] == {"function": "tiny_metrics.py:power_mean", "parameters": {"power": 2},
                                               "sha256": hashlib.sha256(FUNCTIONS.encode()).hexdigest()}
    md = (model["out"] / "comparison.md").read_text()
    assert "## The metrics the experiment defines" in md and "| `mean_abs` | the mean over the quantity's numbers of the absolute difference |" in md
    assert "the function `tiny_metrics.py:power_mean` with {\"power\": 2}" in md
    # a record names its largest distance's metric, whatever its name
    record = json.loads((model["out"] / "stub" / "m1" / "low" / "record.json").read_text())
    assert record["extensions"]["sce-wg-1"]["comparison"]["largest_distance"]["metric"] == "count_off"
    assert record["$schema"].endswith("/0.1.0-draft.8.json")
    records.validate(record)


def test_a_function_that_breaks_its_contract_is_an_error_of_the_check(tmp_path):
    checks = [check("negative_distance", "reference", "types[].kink", {"at_most": 1.0}, metric="negative", kind="numerical"),
              check("failing_function", "levels", "types[].kink", {"at_most": 1.0}, metric="fails")]
    model = with_metrics(tmp_path, {"negative": {"function": "tiny_metrics.py:negative"},
                                    "fails": {"function": "tiny_metrics.py:fails"}}, checks)
    assert run_both(model, "--levels", "low,medium") == 0 and command(model, "compare") == 1
    by_id = {c["id"]: c for c in comparison(model)["checks"]}
    assert by_id["negative_distance"]["verdict"] == "error" and "returned -1.0, which is no distance" in by_id["negative_distance"]["errors"][0]
    assert by_id["failing_function"]["verdict"] == "error" and "its function failed (RuntimeError: no)" in by_id["failing_function"]["errors"][0]


def test_the_checker_of_experiments_refuses_a_metric_it_cannot_stand_behind(tmp_path):
    mean = {"pointwise": "abs_difference", "aggregate": "mean"}
    near = check("c", "reference", "types[].rule.c", {"at_most": 1.0}, metric="mean_abs", kind="numerical")
    model = with_metrics(tmp_path, {"mean_abs": mean, "power_mean": {"function": "tiny_metrics.py:power_mean"}}, [near])
    exp, folder = experiment.load(model["experiment"]), model["experiment"].parent
    assert experiment.problems(exp, folder, RESULTS_SCHEMA) == []

    def problems(change) -> str:
        broken = json.loads(json.dumps(exp))
        change(broken)
        return "\n".join(experiment.problems(broken, folder, RESULTS_SCHEMA))

    # a name that is neither the core's nor defined: in a check, a reference quantity, a reference's errors
    assert "c: no metric median_abs" in problems(lambda e: e["checks"][0].update(metric="median_abs"))
    assert "reference_quantities: no metric median_abs" in problems(
        lambda e: e.update(reference_quantities=[{"quantity": "types[].kink", "metric": "median_abs"}]))
    assert "m1: its reference states an error for types[].kink under median_abs, which is no metric" in problems(
        lambda e: e["members"][0]["reference"]["errors"].update({"types[].kink": {"median_abs": 0.1}}))
    # the definitions: a name of the core's cannot be defined again; each kind of definition has its own keys
    assert problems(lambda e: e["metrics"].update(max_abs_difference=mean)) != ""
    for definition in ({"pointwise": "abs_difference"}, {"pointwise": "abs_difference", "aggregate": "median"},
                       {"pointwise": "abs_difference", "aggregate": "quantile"},
                       {"pointwise": "abs_difference", "aggregate": "quantile", "q": 0},
                       {"pointwise": "abs_difference", "aggregate": "quantile", "q": 1.5},
                       {"pointwise": "abs_difference", "aggregate": "mean", "q": 0.5},
                       {"pointwise": "relative_to_reference", "aggregate": "mean"},
                       {"pointwise": "abs_difference", "aggregate": "mean", "floor": 1.0},
                       {"pointwise": "abs_difference", "aggregate": "mean", "weights": [1, 2]},
                       {"function": "tiny_metrics.py:power_mean"}, {"function": "/abs/metrics.py:f", "sha256": "0" * 64},
                       {"function": "tiny_metrics.py", "sha256": "0" * 64}):
        assert problems(lambda e: e["metrics"].update(other=definition)) != "", definition
    # a metric relative to the reference where a check compares with none; a floor on a check is the core's metric's alone
    relative = {"pointwise": "relative_to_reference", "floor": 0.5, "aggregate": "mean"}
    assert "is relative to the reference, and the check compares with none" in problems(
        lambda e: (e["metrics"].update(to_reference=relative),
                   e["checks"].append(check("d", "levels", "types[].kink", {"at_most": 1.0}, metric="to_reference"))))
    assert problems(lambda e: e["checks"][0].update(floor=0.5)) != ""
    # a function: its file there, hashing as stated, parsing, and defining the function; read and never run
    digest = exp["metrics"]["power_mean"]["sha256"]
    assert "the metric other: no file absent.py" in problems(
        lambda e: e["metrics"].update(other={"function": "absent.py:f", "sha256": digest}))
    assert "the metric power_mean: tiny_metrics.py's hash differs" in problems(lambda e: e["metrics"]["power_mean"].update(sha256="0" * 64))
    assert "the metric other: tiny_metrics.py defines no function median" in problems(
        lambda e: e["metrics"].update(other={"function": "tiny_metrics.py:median", "sha256": digest}))
    (folder / "broken.py").write_text("def f(:\n")
    assert "the metric other: broken.py does not parse" in problems(lambda e: e["metrics"].update(
        other={"function": "broken.py:f", "sha256": hashlib.sha256(b"def f(:\n").hexdigest()}))
    (folder / "raises.py").write_text("raise RuntimeError('at import')\ndef f(a, b):\n    return 0.0\n")
    raising = {"function": "raises.py:f", "sha256": hashlib.sha256((folder / "raises.py").read_bytes()).hexdigest()}
    assert problems(lambda e: e["metrics"].update(other=raising)) == ""  # the checker reads the file and does not run it
    with pytest.raises(ValueError, match="raises.py could not be imported"):
        metrics.load({"metrics": {"other": raising}}, model["experiment"])


def test_an_exact_entry_is_held_to_the_error_stated_under_a_defined_metric():
    d = defined(mean_abs={"pointwise": "abs_difference", "aggregate": "mean"})
    within = check("formula_conforms", "reference", "types[].rule.c", "within_reference_error", metric="mean_abs", kind="exact")
    stated = {"results_file": "m1.reference.json", "results_sha256": "0" * 64}
    for errors, verdict in (({"types[].rule.c": {"mean_abs": 0.001}}, "pass"), ({"types[].rule.c": 0.001}, "error")):
        references = {"m1": {"stated": {**stated, "errors": errors}, "results": REFERENCE_M1, "sha256": "0" * 64, "problem": None}}
        got = comparator.evaluate_check(within, results_of_the_entries(), ["m1"], ["low", "medium", "high"],
                                        {"stub": "numerical", "formula": "exact"}, references, defined=d)
        assert got["verdict"] == verdict, errors
    assert evaluate(check("kink_falls", "reference", "types[].kink", "falls_with_level", kind="numerical"))["verdict"] == "pass"
