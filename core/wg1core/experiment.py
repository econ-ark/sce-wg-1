"""Experiment files (../../schemas/experiments.md): loading one, and what its validator cannot say about it.

`problems(experiment, folder, results_schema, anchors)` returns everything wrong with an experiment, the validator's
errors first: missing or misnamed files, hashes that differ, a request file for another member, checks naming
undeclared members or levels, a check against the reference for a member that pins none or whose reference states no
error the check needs, a metric that is neither the core's nor defined by the experiment, a metric's function that is
missing or changed, quantities the model's results schema does not define, missing report scripts, and anchors a
source's page does not have. The results schema and the anchors are the model repository's, named in its registry
file, the anchors by the key in `sources` they are for; the runner calls this before it runs anything.

A solution has a kind and a role. Its kind is how it is obtained: `exact`, evaluated from a closed form, or
`numerical`, approximated by a method with settings at a level. Its role is what it is for in an experiment: the
`reference`, which a member pins with its stated errors, or an `entry`, a registered toolkit's solution measured
against it. `stated_error` reads what a reference states.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import jsonschema

from . import canonical, metrics

SCHEMA = json.loads((Path(__file__).resolve().parent / "schemas" / "experiment.schema.json").read_text(encoding="utf-8"))


def load(path: Path) -> dict:
    return canonical.load_strict(Path(path).read_text(encoding="utf-8"))


def read_anchors(path: Path) -> set[str]:
    """The anchors of a source page, one per line, comments and blank lines left out."""
    return {line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def stated_error(reference: dict, quantity: str, metric: str) -> float | None:
    """The error a member's reference states for a quantity under a metric; None when it states none. A bare number
    is the error under the absolute metric, as every experiment wrote it before errors were keyed by metric."""
    value = (reference.get("errors") or {}).get(quantity)
    if isinstance(value, dict):
        return value.get(metric)
    return value if metric == "max_abs_difference" else None


def _deref(node: dict, results: dict) -> dict:
    while "$ref" in node:
        node = results["$defs"][node["$ref"].split("/")[-1]]
    return node


def _branches(node: dict, results: dict):
    node = _deref(node, results)
    yield node
    for key in ("allOf", "anyOf", "oneOf"):
        for sub in node.get(key, []):
            yield from _branches(sub, results)


def resolves(path: str, results: dict) -> bool:
    """Whether a quantity's path names something the results schema defines."""
    nodes = [results]
    for segment in path.split("."):
        key, every = (segment[:-2], True) if segment.endswith("[]") else (segment, False)
        found = []
        for node in nodes:
            for branch in _branches(node, results):
                prop = branch.get("properties", {}).get(key)
                if prop is None:
                    continue
                if every:
                    found += [b["items"] for b in _branches(prop, results) if "items" in b]
                else:
                    found.append(prop)
        if not found:
            return False
        nodes = found
    return True


def problems(experiment: dict, folder: Path, results_schema: dict | None = None,
             anchors: dict[str, set[str]] | set[str] | None = None) -> list[str]:
    """What the validator cannot say about an experiment: its files, hashes, names and quantities. Without a results
    schema the quantities are not checked. `anchors` holds each source's anchors by its key in `sources`; a set alone
    is BST's, as before a model could name anchors for another source. A source without anchors is not checked."""
    folder = Path(folder)
    out = [f"{'/'.join(map(str, e.path))}: {e.message}"
           for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(experiment)]
    if out:
        return out
    ids = [m["id"] for m in experiment["members"]]
    if len(set(ids)) != len(ids):
        out.append("a member's id is repeated")
    for m in experiment["members"]:
        p, r = folder / m["parameter_file"], folder / m["request_file"]
        if p.stem != m["id"]:
            out.append(f"{m['id']}: the id is not its parameter file's name")
        if not p.is_file() or not r.is_file():
            out.append(f"{m['id']}: a file is missing")
            continue
        member, request = load(p), load(r)
        if canonical.model_hash(member) != m["parameter_file_sha256"]:
            out.append(f"{m['id']}: the parameter file's hash differs")
        if canonical.model_hash(request) != m["request_file_sha256"]:
            out.append(f"{m['id']}: the request file's hash differs")
        if request.get("family") != member.get("family") or request.get("parameter_file_sha256") != m["parameter_file_sha256"]:
            out.append(f"{m['id']}: the request file is for another member")
        if m.get("reference"):
            ref = folder / m["reference"]["results_file"]
            if not ref.is_file():
                out.append(f"{m['id']}: no reference file {m['reference']['results_file']}")
            elif hashlib.sha256(ref.read_bytes()).hexdigest() != m["reference"]["results_sha256"]:
                out.append(f"{m['id']}: the reference file's hash differs")
            if results_schema is not None:
                out += [f"the results schema has no {q}" for q in m["reference"].get("errors", {}) if not resolves(q, results_schema)]
    out += metrics.static_problems(experiment, folder)
    check_ids = [c["id"] for c in experiment["checks"]]
    if len(set(check_ids)) != len(check_ids):
        out.append("a check's id is repeated")
    references = {m["id"]: m["reference"] for m in experiment["members"] if m.get("reference")}
    for c in experiment["checks"]:
        named = [i for pair in c.get("pairs", []) for i in pair] + c.get("members", [])
        out += [f"{c['id']}: no member {i}" for i in named if i not in ids]
        out += [f"{c['id']}: the experiment has no level {lv}" for lv in c.get("levels", []) if lv not in experiment["levels"]]
        if c["compare"] == "reference":
            # A check against the reference needs one: for each member it names, or for some member when it names none.
            held = [i for i in c.get("members", references) if i in ids]
            out += [f"{c['id']}: {i} pins no reference" for i in held if i not in references]
            if not held:
                out.append(f"{c['id']}: it compares with the reference, and no member pins one")
            if c["expect"] == "within_reference_error":
                out += [f"{c['id']}: {i}'s reference states no error for {c['quantity']} under {c['metric']}"
                        for i in held if i in references and stated_error(references[i], c["quantity"], c["metric"]) is None]
    if results_schema is not None:
        named = experiment["reports"] + [c["quantity"] for c in experiment["checks"]]
        named += [q["quantity"] for q in experiment.get("reference_quantities", [])]
        for q in named:
            if not resolves(q, results_schema):
                out.append(f"the results schema has no {q}")
    for s in experiment.get("report_scripts", []):
        if not (folder / s["path"]).is_file():
            out.append(f"no report script {s['path']}")
    if isinstance(anchors, (set, frozenset)):
        anchors = {"bst": anchors}
    for key, cited in experiment.get("sources", {}).items():
        if anchors and key in anchors:
            out += [f"the source page of {key} has no anchor {a}" for a in cited if a not in anchors[key]]
    return out
