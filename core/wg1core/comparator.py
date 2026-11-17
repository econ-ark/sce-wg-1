"""The comparator (../../schemas/experiments.md): the experiment's checks evaluated as written on a run's results
files, and every job's distance from its member's reference with the reference's own error beside it.

A solution has a kind and a role. Its kind is how it is obtained: exact, evaluated from a closed form, or numerical,
approximated by a method with settings at a level. Its role is what it is for in an experiment: the reference, which
a member pins with its stated errors, or an entry, a registered toolkit's solution. An entry's kind is the registry
file's; a reference's is the experiment's.

A check compares one quantity, a path into the results file, under a metric and an expectation: between members of
one toolkit at one level; between numerical entries for one member at one level; between successive levels of one
numerical entry for one member; or, for each entry of the kind the check names, between its file and its member's
reference. The levels are ordered as the experiment lists them, or as the check lists the ones it applies to. An exact
entry has no method to compare and no ladder to converge along, so the checks between toolkits and between levels
leave it out; what holds it is a check against the reference. A check's verdict is pass, fail, not applicable when the
run holds too little to apply it, or error when the files cannot be compared.

Against a reference, a numerical entry's distance is to fall with the level; a level whose distance is no larger than
the reference's stated error under the check's metric has come as close as the reference resolves, and counts as
fallen. An exact entry is to lie within the reference's stated error, which is a test that it encodes the solution and
not a measurement of a method.

A check names its metric, one of the core's three or one the experiment defines (metrics.py); no metric is the
default.

Beside the checks, the distance of every job from its member's reference is reported for every quantity the
experiment names, with the reference's error beside it and where in the quantity's numbers the largest distance sits.
That distance gets no verdict. A comparison that cannot be computed for a member that pins a reference, the reference
not loading, not answering the same question by the identity keys the model names, or a quantity not comparable, is
an error. The comparator's exit status is the checks' and the errors', never a reported distance's.

It writes `comparison.json` and `comparison.md` in the run folder, `comparison.json` in each job's folder, and the
comparison block of each job's record.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from . import metrics as metric_definitions
from . import records
from .experiment import stated_error

NUMERICAL = "numerical"


# Quantities and metrics ------------------------------------------------------------------------------------------------

def numbers(value: dict, quantity: str) -> list[float]:
    """Every number a quantity holds, in a fixed order: along a path such as types[].rule.c, lists in order and
    mappings by sorted key, so that two files are compared element by element."""
    nodes = [value]
    for segment in quantity.split("."):
        key, every = (segment[:-2], True) if segment.endswith("[]") else (segment, False)
        nxt = []
        for node in nodes:
            if not isinstance(node, dict) or key not in node:
                raise KeyError(f"no {quantity}")
            item = node[key]
            if every:
                if not isinstance(item, list):
                    raise KeyError(f"{quantity}: not a list at {key}")
                nxt += item
            else:
                nxt.append(item)
        nodes = nxt
    out: list[float] = []

    def flatten(v):
        if isinstance(v, bool) or v is None or isinstance(v, str):
            return
        if isinstance(v, (int, float)):
            out.append(float(v))
        elif isinstance(v, list):
            for x in v:
                flatten(x)
        elif isinstance(v, dict):
            for k in sorted(v):
                flatten(v[k])

    for n in nodes:
        flatten(n)
    return out


def distance_at(a: list[float], b: list[float], metric: str, floor: float | None = None, strict: bool = False,
                defined: dict | None = None) -> tuple[float, int | None]:
    """The distance between two files' numbers under a metric, and where the largest pointwise distance sits: the
    index, among the quantity's numbers in their fixed order, of the first number that attains it (metrics.py). The
    metric is one of the core's three or one of `defined`, the experiment's own. With `strict`, a value that is not a
    number is refused: a largest distance passes over one that is not the first, so a verdict that an entry lies
    within an error must not rest on it."""
    return metric_definitions.distance_at(a, b, metric, floor, strict, defined)


def distance(a: list[float], b: list[float], metric: str, floor: float | None = None, defined: dict | None = None) -> float:
    return distance_at(a, b, metric, floor, defined=defined)[0]


def compare_at(a: dict, b: dict, quantity: str, metric: str, floor: float | None = None, strict: bool = False,
               defined: dict | None = None) -> tuple[float, int | None]:
    return distance_at(numbers(a, quantity), numbers(b, quantity), metric, floor, strict, defined)


def compare(a: dict, b: dict, quantity: str, metric: str, floor: float | None = None, defined: dict | None = None) -> float:
    return compare_at(a, b, quantity, metric, floor, defined=defined)[0]


# The checks -------------------------------------------------------------------------------------------------------------

def _levels_in_order(levels, order: list[str]) -> list[str]:
    """Levels as the experiment lists them, coarse to fine; a level the experiment does not list comes last."""
    return sorted(levels, key=lambda lv: (order.index(lv) if lv in order else len(order), lv))


def value_at(data: dict, path: str):
    """One value along a path with no [] in it, such as parameter_file_sha256; None when absent."""
    node = data
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _verdict(outcomes: list[bool], errors: list[str]) -> str:
    if errors:
        return "error"
    if not outcomes:
        return "not applicable"
    return "pass" if all(outcomes) else "fail"


def evaluate_check(check: dict, results: dict, members: list[str], order: list[str], kinds: dict | None = None,
                   references: dict | None = None, identity: list[str] = (), defined: dict | None = None) -> dict:
    """One check on a run's results, `results[toolkit][member][level]`, the levels ordered as the experiment lists
    them, or as the check lists the ones it applies to. `kinds` gives each entry's kind, numerical where it gives
    none; `references` gives, for each member that pins one, the reference as `load_references` returns it;
    `identity` names the keys an entry's file and the reference must agree on; `defined` holds the metrics the
    experiment defines. Returns the verdict and the numbers behind it. A comparison the run holds too little for is
    not applicable, never a failure."""
    quantity, metric, expect, floor = check["quantity"], check["metric"], check["expect"], check.get("floor")
    at_most = expect.get("at_most") if isinstance(expect, dict) else None
    kinds, references = kinds or {}, references or {}
    values, outcomes, errors = [], [], []
    if check.get("levels"):
        order = list(check["levels"])

    def ordered(levels) -> list[str]:
        """The levels the check applies to, of those given, in the order the expectation reads them."""
        return [lv for lv in _levels_in_order(levels, order) if not check.get("levels") or lv in order]

    def dist(x: dict, y: dict, label: str, strict: bool = False) -> tuple[float, int] | None:
        try:
            return compare_at(x, y, quantity, metric, floor, strict, defined)
        except (KeyError, ValueError) as e:
            errors.append(f"{label}: {e}")
            return None

    # An exact entry has no method to compare and no ladder to converge along: only numerical entries are set
    # beside one another or along their levels.
    numerical = {t: r for t, r in results.items() if kinds.get(t, NUMERICAL) == NUMERICAL}

    if check["compare"] == "members":
        for toolkit, by_member in results.items():
            levels = set().union(*(set(v) for v in by_member.values())) if by_member else set()
            for level in ordered(levels):
                series = []
                for a, b in check["pairs"]:
                    ra, rb = by_member.get(a, {}).get(level), by_member.get(b, {}).get(level)
                    if ra is None or rb is None:
                        series = None
                        break
                    d = dist(ra, rb, f"{toolkit} {a} against {b} at {level}")
                    series.append(d[0] if d else None)
                if series is None or any(d is None for d in series):
                    continue
                values.append({"toolkit": toolkit, "level": level, "pairs": [[a, b] for a, b in check["pairs"]], "values": series})
                if expect == "decreasing":
                    outcomes.append(all(later < earlier for earlier, later in zip(series, series[1:])))
                elif at_most is not None:
                    outcomes.append(all(d <= at_most for d in series))
    elif check["compare"] == "toolkits":
        chosen = check.get("members") or members
        for t1, t2 in itertools.combinations(sorted(numerical), 2):
            for member in chosen:
                levels = ordered(set(numerical[t1].get(member, {})) & set(numerical[t2].get(member, {})))
                series = []
                for level in levels:
                    d = dist(numerical[t1][member][level], numerical[t2][member][level], f"{t1} against {t2}, {member} at {level}")
                    if d is None:
                        series = None
                        break
                    series.append((level, d[0]))
                if not series:
                    continue
                values.append({"toolkits": [t1, t2], "member": member, "values": {lv: d for lv, d in series}})
                if expect == "falls_with_level":
                    if len(series) >= 2:
                        outcomes.append(all(later < earlier for (_, earlier), (_, later) in zip(series, series[1:])))
                elif at_most is not None:
                    outcomes.append(all(d <= at_most for _, d in series))
    elif check["compare"] == "levels":
        chosen = check.get("members") or members
        for toolkit, by_member in numerical.items():
            for member in chosen:
                levels = ordered(by_member.get(member, {}))
                steps = []
                for lo, hi in zip(levels, levels[1:]):
                    d = dist(by_member[member][lo], by_member[member][hi], f"{toolkit} {member}, {lo} to {hi}")
                    if d is None:
                        steps = None
                        break
                    steps.append((f"{lo}-{hi}", d[0]))
                if not steps:
                    continue
                values.append({"toolkit": toolkit, "member": member, "values": {k: d for k, d in steps}})
                if expect == "falls_with_level":
                    if len(steps) >= 2:
                        outcomes.append(all(later < earlier for (_, earlier), (_, later) in zip(steps, steps[1:])))
                elif at_most is not None:
                    outcomes.append(all(d <= at_most for _, d in steps))
    elif check["compare"] == "reference":
        chosen = check.get("members") or [m for m in members if m in references]
        for toolkit, by_member in results.items():
            if kinds.get(toolkit, NUMERICAL) != check["kind"]:
                continue
            for member in chosen:
                levels = ordered(by_member.get(member, {}))
                if not levels:
                    continue
                reference = references.get(member)
                if reference is None or reference["results"] is None:
                    errors.append(f"{member}: {reference['problem'] if reference else 'the member pins no reference'}")
                    continue
                series = []
                for level in levels:
                    mismatched = [k for k in identity if value_at(by_member[member][level], k) != value_at(reference["results"], k)]
                    if mismatched:
                        errors.append(f"{toolkit} {member} at {level}: the reference does not answer the same question: "
                                      + ", ".join(f"{k} differs" for k in mismatched))
                        series = None
                        break
                    d = dist(by_member[member][level], reference["results"],
                             f"{toolkit} against the reference, {member} at {level}", strict=True)
                    if d is None:
                        series = None
                        break
                    series.append((level, d))
                if not series:
                    continue
                error = stated_error(reference["stated"], quantity, metric)
                entry = {"toolkit": toolkit, "kind": check["kind"], "member": member,
                         "values": {lv: d for lv, (d, _) in series},
                         "at": {lv: at for lv, (_, at) in series if at is not None}}
                if error is not None:
                    entry["reference_error"] = error
                values.append(entry)
                reached = (lambda d: d <= error) if error is not None else (lambda d: False)
                if expect == "falls_with_level":
                    # A distance no larger than the reference's error is as close as the reference resolves: the
                    # step to it counts as a fall, whatever the distance before it.
                    if len(series) >= 2:
                        outcomes.append(all(later < earlier or reached(later)
                                            for (_, (earlier, _)), (_, (later, _)) in zip(series, series[1:])))
                elif expect == "within_reference_error":
                    if error is None:
                        errors.append(f"{member}: the reference states no error for {quantity} under {metric}")
                    else:
                        outcomes.append(all(reached(d) for _, (d, _) in series))
                elif at_most is not None:
                    outcomes.append(all(d <= at_most for _, (d, _) in series))
    out = {"id": check["id"], "statement": check["statement"], "compare": check["compare"], "quantity": quantity,
           "metric": metric, "expect": expect, "verdict": _verdict(outcomes, errors), "values": values,
           "errors": errors}
    out.update({k: check[k] for k in ("kind", "floor", "levels") if k in check})
    return out


# The reference ----------------------------------------------------------------------------------------------------------

def reference_quantities(experiment: dict) -> list[dict]:
    """The quantities compared with the reference: the experiment's own list, or its reports under the absolute
    metric when it names none."""
    return experiment.get("reference_quantities") or [{"quantity": q, "metric": "max_abs_difference"}
                                                       for q in experiment["reports"]]


def load_reference(experiment_file: Path, member: dict) -> tuple[dict | None, str | None, str | None]:
    """A member's reference results file, its hash checked: (results, hash, problem). A file that hashes as stated
    and is not JSON, or holds no object, is a problem like a missing one."""
    ref = member.get("reference")
    if not ref:
        return None, None, None
    path = Path(experiment_file).resolve().parent / ref["results_file"]
    if not path.is_file():
        return None, None, f"no reference file {ref['results_file']}"
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ref["results_sha256"]:
        return None, digest, f"the reference file {ref['results_file']} does not hash as the experiment says"
    try:
        results = json.loads(data.decode("utf-8"))
    except ValueError:
        return None, digest, f"the reference file {ref['results_file']} is not JSON"
    if not isinstance(results, dict):
        return None, digest, f"the reference file {ref['results_file']} holds no results"
    return results, digest, None


def load_references(experiment: dict, experiment_file: Path, members=None) -> dict:
    """The pinned reference of every member, or of the members named, by the member's id: what the experiment states
    of it, its results when the file loads and hashes as stated, the hash of the file found, and the problem when it
    does not load."""
    out = {}
    for member in experiment["members"]:
        if member.get("reference") and (members is None or member["id"] in members):
            results, digest, problem = load_reference(experiment_file, member)
            out[member["id"]] = {"stated": member["reference"], "results": results, "sha256": digest, "problem": problem}
    return out


def _producers(stated: dict) -> list[str]:
    """The names of what produced or certified a reference: a producer written as a string, or its toolkit."""
    listed = ([stated["produced_by"]] if stated.get("produced_by") else []) + list(stated.get("certified_by", []))
    return [p if isinstance(p, str) else p["toolkit"] for p in listed]


def describe_references(references: dict, entries: list[str]) -> list[dict]:
    """The report's part on the reference: for each member that pins one, its kind, what produced and certified it,
    its file and hash, its stated errors, whether it loaded, and which of the run's entries a producer names: a
    producer written as that entry's name, or as a toolkit of that name."""
    out = []
    for member, reference in references.items():
        stated = reference["stated"]
        row = {"member": member, "results_file": stated["results_file"], "results_sha256": stated["results_sha256"]}
        row.update({k: stated[k] for k in ("kind", "produced_by", "certified_by", "record") if k in stated})
        row["errors"] = stated.get("errors", {})
        row["status"] = "loaded" if reference["results"] is not None else "error"
        if reference["problem"]:
            row["problem"] = reference["problem"]
        among = sorted(set(_producers(stated)) & set(entries))
        if among:
            row["producers_among_the_entries"] = among
        out.append(row)
    return out


def reference_distances(results: dict, reference: dict, quantities: list[dict], errors: dict,
                        defined: dict | None = None) -> list[dict]:
    """Every distance from the reference, each with where its largest sits and the reference's own error for that
    quantity beside it, or the reason it could not be computed. No verdict. An error stated by metric is shown under
    its metric. An error stated as a bare number is the error under the absolute metric; it is also shown beside the
    distance under max_relative_difference, as it was before errors were keyed by metric, and never beside a distance
    relative to the reference or under a metric the experiment defines."""
    out = []
    for q in quantities:
        row = {"quantity": q["quantity"], "metric": q["metric"]}
        if "floor" in q:
            row["floor"] = q["floor"]
        try:
            row["distance"], at = compare_at(results, reference, q["quantity"], q["metric"], q.get("floor"), defined=defined)
            if at is not None:
                row["at"] = at
        except (KeyError, ValueError) as e:
            row["problem"] = str(e)
        stated = errors.get(q["quantity"])
        if isinstance(stated, dict):
            stated = stated.get(q["metric"])
        elif q["metric"] not in ("max_abs_difference", "max_relative_difference"):
            stated = None
        if stated is not None:
            row["reference_error"] = stated
        out.append(row)
    return out


# The run ----------------------------------------------------------------------------------------------------------------

def run_comparison(experiment: dict, experiment_file: Path, jobs: list[dict], run: Path,
                   identity: list[str] = ()) -> dict:
    """Everything the comparator writes for one run folder, as one object; the files are written by the caller.
    `identity` names the results-file keys, such as parameter_file_sha256 and request_file_sha256, that a job's file
    and its reference must agree on for the reference to answer the same question. A job's `kind` is its entry's,
    numerical when the job carries none."""
    results: dict = {}
    job_results = {}
    kinds = {j["toolkit"]: j.get("kind", NUMERICAL) for j in jobs}
    for j in jobs:
        f = j["dir"] / "results.json"
        if f.is_file():
            data = json.loads(f.read_text(encoding="utf-8"))
            results.setdefault(j["toolkit"], {}).setdefault(j["member"], {})[j["level"]] = data
            job_results[id(j)] = data
    members = [m["id"] for m in experiment["members"]]
    references = load_references(experiment, experiment_file, {j["member"] for j in jobs})  # of the members the run holds
    defined = metric_definitions.load(experiment, experiment_file)
    checks = [evaluate_check(c, results, members, list(experiment["levels"]), kinds, references, identity, defined)
              for c in experiment["checks"]]
    quantities = reference_quantities(experiment)
    by_member = {m["id"]: m for m in experiment["members"]}
    per_job = []
    for j in jobs:
        entry = {"toolkit": j["toolkit"], "kind": kinds[j["toolkit"]], "member": j["member"], "level": j["level"],
                 "dir": str(j["dir"])}
        data = job_results.get(id(j))
        found = references.get(j["member"])
        reference, digest, problem = (found["results"], found["sha256"], found["problem"]) if found else (None, None, None)
        if data is None:
            entry.update({"status": "not run", "reason": "no results file"})
        elif found is None:
            entry.update({"status": "not run", "reason": "the member pins no reference"})
        elif reference is None:
            entry.update({"status": "error", "reason": problem})
            if digest:
                entry["reference"] = digest
        else:
            mismatched = [k for k in identity if value_at(data, k) != value_at(reference, k)]
            errors = by_member[j["member"]]["reference"].get("errors", {})
            rows = reference_distances(data, reference, quantities, errors, defined)
            problems = [f"{r['quantity']}: {r['problem']}" for r in rows if "problem" in r]
            entry.update({"reference": digest, "distances": rows})
            if mismatched:
                entry.update({"status": "error", "reason": "the reference does not answer the same question: "
                              + ", ".join(f"{k} differs" for k in mismatched)})
            elif problems:
                entry.update({"status": "error", "reason": "a distance could not be computed: " + "; ".join(problems)})
            else:
                entry["status"] = "computed"
                largest = max(rows, key=lambda r: r["distance"])
                entry["largest_distance"] = {k: largest[k] for k in ("quantity", "metric", "floor", "distance", "reference_error")
                                             if k in largest}
        per_job.append(entry)
    failed = any(c["verdict"] in ("fail", "error") for c in checks) or any(j["status"] == "error" for j in per_job)
    report = {"experiment": experiment["experiment"], "run": run.name, "entries": kinds,
              "member_references": describe_references(references, list(kinds)), "checks": checks, "reference": per_job,
              "failed": failed}
    if defined:
        report["metrics"] = metric_definitions.describe(experiment)
    return report


def _metric_text(definition: dict) -> str:
    """A metric's definition in words, for the report."""
    if "function" in definition:
        parameters = definition.get("parameters")
        return (f"the function `{definition['function']}`" + (f" with {json.dumps(parameters, sort_keys=True)}" if parameters else "")
                + f", its file's hash `{definition['sha256'][:12]}`")
    pointwise = {"abs_difference": "the absolute difference",
                 "relative_difference": "the absolute difference over the larger of one and the first value's magnitude",
                 "relative_to_reference": "the absolute difference over the larger of the floor and the reference's magnitude"
                 }[definition["pointwise"]]
    how = {"max": "the largest", "mean": "the mean", "rms": "the root of the mean square",
           "quantile": f"the quantile at {definition.get('q')}, with no interpolation,"}[definition["aggregate"]]
    return f"{how} over the quantity's numbers of {pointwise}" + (f", floor {definition['floor']:g}" if "floor" in definition else "")


def _producer_text(producer) -> str:
    if isinstance(producer, str):
        return producer
    return producer["toolkit"] + "".join(f", {k} {producer[k]}" for k in ("commit", "settings", "record") if k in producer)


def _errors_text(errors: dict) -> str:
    parts = []
    for quantity, stated in errors.items():
        if isinstance(stated, dict):
            parts.append(f"`{quantity}` " + ", ".join(f"{e:.3g} ({metric})" for metric, e in stated.items()))
        else:
            parts.append(f"`{quantity}` {stated:.3g}")
    return "; ".join(parts) or "none stated"


def _applies_to(check: dict) -> str:
    """The entries a check sets side by side, by their kind."""
    if check["compare"] == "reference":
        return check["kind"]
    return "every" if check["compare"] == "members" else NUMERICAL


def as_markdown(report: dict) -> str:
    """The run's comparison as tables a findings README can include: the reference, the checks, then the distances."""
    lines = [f"# Comparison: {report['experiment']}, run {report['run']}"]
    references = report.get("member_references", [])
    if references:
        lines += ["", "## The reference", "",
                  "| member | kind | produced by | certified by | the file's hash | stated errors |", "|---|---|---|---|---|---|"]
        for r in references:
            by = _producer_text(r["produced_by"]) if "produced_by" in r else "not stated"
            certified = "; ".join(_producer_text(p) for p in r.get("certified_by", []))
            state = "" if r["status"] == "loaded" else f" **{r['status']}**: {r['problem']}"
            lines.append(f"| {r['member']} | {r.get('kind', 'not stated')} | {by} | {certified} | `{r['results_sha256'][:12]}`{state} "
                         f"| {_errors_text(r['errors'])} |")
        for r in references:
            for name in r.get("producers_among_the_entries", []):
                lines += ["", f"What produced or certified the reference of {r['member']}, {name}, is also an entry of this run."]
    if report.get("metrics"):
        lines += ["", "## The metrics the experiment defines", "", "| metric | what it is |", "|---|---|"]
        lines += [f"| `{name}` | {_metric_text(definition)} |" for name, definition in report["metrics"].items()]
    kinds = report.get("entries", {})
    if any(kind != NUMERICAL for kind in kinds.values()):
        lines += ["", "The entries: " + ", ".join(f"{name}, {kind}" for name, kind in kinds.items()) + ". An exact entry is "
                  "held by the checks against the reference and left out of the checks between toolkits and between levels."]
    lines += ["", "## The experiment's checks", "",
              "| check | compare | entries | quantity | metric | expectation | verdict |", "|---|---|---|---|---|---|---|"]
    for c in report["checks"]:
        exp = c["expect"] if isinstance(c["expect"], str) else f"at most {c['expect']['at_most']:g}"
        metric = c["metric"] + (f", floor {c['floor']:g}" if "floor" in c else "")
        lines.append(f"| `{c['id']}` | {c['compare']} | {_applies_to(c)} | `{c['quantity']}` | {metric} | {exp} | **{c['verdict']}** |")
    for c in report["checks"]:
        if c["values"] or c["errors"]:
            lines += ["", f"`{c['id']}`:"]
            for v in c["values"]:
                vals, at = v["values"], v.get("at", {})
                shown = (", ".join(f"{x:.3g}" for x in vals) if isinstance(vals, list)
                         else ", ".join(f"{k} {x:.3g}" + (f" (at {at[k]})" if k in at else "") for k, x in vals.items()))
                who = v.get("toolkit") or " against ".join(v.get("toolkits", []))
                where = v.get("level") or v.get("member", "")
                beside = f"; the reference's error {v['reference_error']:.3g}" if "reference_error" in v else ""
                lines.append(f"- {who}, {where}: {shown}{beside}")
            for e in c["errors"]:
                lines.append(f"- error: {e}")
    lines += ["", "## Distances from the reference", "",
              "| toolkit | kind | member | level | quantity | metric | distance | at | the reference's error |",
              "|---|---|---|---|---|---|---|---|---|"]
    for j in report["reference"]:
        kind = j.get("kind", NUMERICAL)
        if j["status"] != "computed":
            lines.append(f"| {j['toolkit']} | {kind} | {j['member']} | {j['level']} | | | **{j['status']}**: {j['reason']} | | |")
            if "distances" not in j:
                continue
        for r in j["distances"]:
            d = f"{r['distance']:.3g}" if "distance" in r else f"not computed: {r['problem']}"
            e = f"{r['reference_error']:.3g}" if "reference_error" in r else "not stated"
            metric = r["metric"] + (f", floor {r['floor']:g}" if "floor" in r else "")
            lines.append(f"| {j['toolkit']} | {kind} | {j['member']} | {j['level']} | `{r['quantity']}` | {metric} | {d} "
                         f"| {r.get('at', '')} | {e} |")
    lines += ["", "A distance in this table is reported with the reference's error beside it and carries no verdict; `at` is the "
              "index, among the quantity's numbers, where the largest pointwise distance sits. The exit status is the checks' "
              "alone."]
    return "\n".join(lines) + "\n"


def write_outputs(report: dict, jobs: list[dict], run: Path) -> None:
    """The run's files, each job's file, and each record's comparison block."""
    (run / "comparison.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    (run / "comparison.md").write_text(as_markdown(report), encoding="utf-8")
    by_dir = {str(j["dir"]): j for j in jobs}
    for entry in report["reference"]:
        job = by_dir[entry["dir"]]
        job_report = {k: v for k, v in entry.items() if k != "dir"}
        (job["dir"] / "comparison.json").write_text(json.dumps(job_report, indent=1) + "\n", encoding="utf-8")
        record = job["dir"] / "record.json"
        if record.is_file():
            data = json.loads(record.read_text(encoding="utf-8"))
            block = {"status": entry["status"], "report": "comparison.json"}
            if entry.get("reason"):
                block["reason"] = entry["reason"]
            if entry.get("reference"):
                block["reference"] = entry["reference"]
            if entry.get("largest_distance"):
                block["largest_distance"] = entry["largest_distance"]
            data["extensions"]["sce-wg-1"]["comparison"] = block
            records.write(data, record)
