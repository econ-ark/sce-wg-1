"""Metrics (../../schemas/experiments.md, "Metrics"): the distance between two files' numbers for one quantity.

No metric is the default: every check and every reference quantity names the one it uses, and which metrics there
are is the experiment's to say. The core has three by name, each a pointwise distance with its largest taken:

    max_abs_difference          the absolute difference
    max_relative_difference     the absolute difference over the larger of one and the first value's magnitude
    max_relative_to_reference   the absolute difference over the larger of the check's floor and the reference's
                                magnitude

An experiment defines others under `metrics`, each by a name its checks, its reference quantities and its references'
errors then use as they use the three. A definition is one of two things.

A pointwise distance with an aggregate over the quantity's numbers:

    metrics:
      mean_abs_difference: {pointwise: abs_difference, aggregate: mean}
      rms_relative_to_reference: {pointwise: relative_to_reference, floor: 1.0e-12, aggregate: rms}
      nine_tenths_abs_difference: {pointwise: abs_difference, aggregate: quantile, q: 0.9}

The aggregates are `max`, `mean`, `rms`, the root of the mean of the squares, and `quantile`, the smallest pointwise
distance with at least the fraction `q` of them at or below it, taken with no interpolation so that two programs
cannot differ on it. The three the core names are the three pointwise distances with `max`.

Or a function of the model's repository:

    metrics:
      weighted_abs_difference:
        function: metrics.py:weighted_abs_difference      # a file beside the experiment file, and a function in it
        sha256: ...                                       # of the file's bytes: a changed function, a changed experiment
        parameters: {power: 2}

The function is called with the two files' numbers as two lists, the entry's first and the reference's or the other
file's second, and the parameters by name. It returns the distance, a number not below zero, or the distance and the
index among the numbers where its largest pointwise distance sits. The comparator imports the file and runs the
function in its own process, so the function is the model repository's code run by the core, as its adapters and its
verifier are; the checker of experiments reads the file and never runs it. The function runs where the comparison
does, in the environment of the model repository's harness, so it may import the standard library, what the core
itself depends on, numpy and scipy among it, and whatever else that environment declares, and nothing besides.

Where the largest pointwise distance sits is reported with every distance, as `at`, whatever the aggregate. A metric
an experiment defines refuses a value that is not a number, in any comparison; the core's three refuse one where a
check against the reference rests on them, and otherwise pass over one that is not the first, as they always did.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import math
from fractions import Fraction
from pathlib import Path

BUILT_IN = {
    "max_abs_difference": {"pointwise": "abs_difference", "aggregate": "max"},
    "max_relative_difference": {"pointwise": "relative_difference", "aggregate": "max"},
    "max_relative_to_reference": {"pointwise": "relative_to_reference", "aggregate": "max"},  # its floor is the check's
}


# The pointwise distances and the aggregates ---------------------------------------------------------------------------

def pointwise(a: list[float], b: list[float], kind: str, floor: float | None = None) -> list[float]:
    """The distance at each number: `a` an entry's numbers, `b` the reference's or the other file's."""
    if kind == "abs_difference":
        return [abs(x - y) for x, y in zip(a, b)]
    if kind == "relative_difference":
        return [abs(x - y) / max(1.0, abs(x)) for x, y in zip(a, b)]
    if kind == "relative_to_reference":
        if floor is None or not floor > 0:
            raise ValueError("max_relative_to_reference needs a floor above zero")
        return [abs(x - y) / max(floor, abs(y)) for x, y in zip(a, b)]
    raise ValueError(f"unknown pointwise distance {kind}")


def aggregate(each: list[float], how: str, q: float | None = None) -> float:
    """One number from the pointwise distances. The sums are exact to rounding whatever the order of the terms."""
    if how == "max":
        return each[largest_at(each)]
    if how == "mean":
        return math.fsum(each) / len(each)
    if how == "rms":
        return math.sqrt(math.fsum(d * d for d in each) / len(each))
    if how == "quantile":
        if q is None or not 0 < q <= 1:
            raise ValueError("a quantile needs a fraction q above zero and at most one")
        # The least with the fraction q of them at or below it; q is read as the decimal it was written as, so that
        # nine tenths of ten numbers is nine of them and never, by the fraction's binary form, ten.
        return sorted(each)[max(1, math.ceil(Fraction(repr(float(q))) * len(each))) - 1]
    raise ValueError(f"unknown aggregate {how}")


def largest_at(each: list[float]) -> int:
    """The index of the first of the largest pointwise distances."""
    return max(range(len(each)), key=each.__getitem__)


# The metrics an experiment defines ------------------------------------------------------------------------------------

def _function_file(definition: dict, experiment_file: Path) -> tuple[Path, str, str]:
    path, name = definition["function"].rsplit(":", 1)
    return Path(experiment_file).resolve().parent / path, path, name


def load(experiment: dict, experiment_file: Path) -> dict:
    """The metrics an experiment defines, by name, each with its definition and, for a function, the function itself,
    imported from its file once the file hashes as the experiment says. Raises ValueError for a file that is missing,
    hashes otherwise, cannot be imported, or holds no such function."""
    out = {}
    for name, definition in (experiment.get("metrics") or {}).items():
        entry = {"definition": definition}
        if "function" in definition:
            file, path, function = _function_file(definition, experiment_file)
            try:
                data = file.read_bytes()
            except OSError:
                raise ValueError(f"the metric {name}: no file {path}") from None
            digest = hashlib.sha256(data).hexdigest()
            if digest != definition["sha256"]:
                raise ValueError(f"the metric {name}: {path} does not hash as the experiment says")
            try:
                spec = importlib.util.spec_from_file_location(f"wg1core_metric_{name}_{digest[:12]}", file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:  # the file is the model repository's code: its failure is a stated problem
                raise ValueError(f"the metric {name}: {path} could not be imported ({type(e).__name__}: {e})") from None
            entry["call"] = getattr(module, function, None)
            if not callable(entry["call"]):
                raise ValueError(f"the metric {name}: {path} has no function {function}")
        out[name] = entry
    return out


def static_problems(experiment: dict, folder: Path) -> list[str]:
    """What is wrong with an experiment's metrics, found by reading and running nothing: a check, a reference
    quantity or a reference's error naming a metric that is neither the core's nor defined; a metric relative to the
    reference used where there is no reference to divide by; and a function whose file is missing, hashes otherwise
    than stated, does not parse, or defines no function of that name."""
    out = []
    defined = experiment.get("metrics") or {}
    known = set(BUILT_IN) | set(defined)
    for c in experiment["checks"]:
        if c["metric"] not in known:
            out.append(f"{c['id']}: no metric {c['metric']}")
        elif c["compare"] != "reference" and defined.get(c["metric"], {}).get("pointwise") == "relative_to_reference":
            out.append(f"{c['id']}: the metric {c['metric']} is relative to the reference, and the check compares "
                       "with none")
    out += [f"reference_quantities: no metric {q['metric']}" for q in experiment.get("reference_quantities", [])
            if q["metric"] not in known]
    for m in experiment["members"]:
        for quantity, stated in ((m.get("reference") or {}).get("errors") or {}).items():
            if isinstance(stated, dict):
                out += [f"{m['id']}: its reference states an error for {quantity} under {metric}, which is no metric"
                        for metric in stated if metric not in known]
    for name, definition in defined.items():
        if "function" not in definition:
            continue
        file, path, function = _function_file(definition, Path(folder) / "experiment.yaml")
        if not file.is_file():
            out.append(f"the metric {name}: no file {path}")
            continue
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() != definition["sha256"]:
            out.append(f"the metric {name}: {path}'s hash differs")
        try:
            tree = ast.parse(data.decode("utf-8"))
        except (SyntaxError, ValueError) as e:
            out.append(f"the metric {name}: {path} does not parse ({type(e).__name__})")
            continue
        if not any(isinstance(node, ast.FunctionDef) and node.name == function for node in tree.body):
            out.append(f"the metric {name}: {path} defines no function {function}")
    return out


def describe(experiment: dict) -> dict:
    """The metrics an experiment defines, as its report states them: each definition as written, a function's with
    the hash of its file."""
    return {name: dict(definition) for name, definition in (experiment.get("metrics") or {}).items()}


# The distance ----------------------------------------------------------------------------------------------------------

def _not_a_number(a: list[float], b: list[float]) -> None:
    unread = next((i for i, (x, y) in enumerate(zip(a, b)) if math.isnan(x) or math.isnan(y)), None)
    if unread is not None:
        raise ValueError(f"a value that is not a number, at {unread}")


def _called(name: str, entry: dict, a: list[float], b: list[float]) -> tuple[float, int | None]:
    """A function metric's distance, and the index it names if it names one; what it returns is held to the contract."""
    try:
        got = entry["call"](list(a), list(b), **entry["definition"].get("parameters", {}))
    except Exception as e:  # the function is the model repository's code: its failure is a stated problem
        raise ValueError(f"the metric {name}: its function failed ({type(e).__name__}: {e})") from None
    value, at = got if isinstance(got, tuple) and len(got) == 2 else (got, None)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"the metric {name}: its function returned {value!r}, which is no distance")
    if at is not None and (isinstance(at, bool) or not isinstance(at, int) or not 0 <= at < len(a)):
        raise ValueError(f"the metric {name}: its function returned the index {at!r}, which the numbers do not have")
    return float(value), at


def distance_at(a: list[float], b: list[float], metric: str, floor: float | None = None, strict: bool = False,
                defined: dict | None = None) -> tuple[float, int | None]:
    """The distance between two files' numbers under a metric, and where the largest pointwise distance sits: the
    index, among the quantity's numbers in their fixed order, of the first number that attains it; None when a
    function metric names no index. `metric` is one of the core's three names or a name in `defined`, the
    experiment's metrics as `load` returns them. `floor` is the check's, for max_relative_to_reference alone. With
    `strict`, and always for a metric the experiment defines, a value that is not a number is refused."""
    if len(a) != len(b):
        raise ValueError(f"the two files hold {len(a)} and {len(b)} numbers")
    if not a:
        raise ValueError("no numbers to compare")
    definition = BUILT_IN.get(metric)
    if definition is None:
        entry = (defined or {}).get(metric)
        if entry is None:
            raise ValueError(f"unknown metric {metric}")
        definition = entry.get("definition", entry)
        _not_a_number(a, b)
        if "function" in definition:
            return _called(metric, entry, a, b)
        floor = definition.get("floor")
    elif strict:
        _not_a_number(a, b)
    each = pointwise(a, b, definition["pointwise"], floor)
    return aggregate(each, definition["aggregate"], definition.get("q")), largest_at(each)
