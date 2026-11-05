"""Experiment files (../../schemas/experiments.md): loading one, and what its validator cannot say about it.

`problems(experiment, folder, results_schema, anchors)` returns everything wrong with an experiment, the validator's
errors first: missing or misnamed files, hashes that differ, a request file for another member, checks naming
undeclared members, quantities the model's results schema does not define, missing report scripts, and anchors the
model's source page does not have. The results schema and the anchors are the model repository's, named in its
registry file; the runner calls this before it runs anything.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from . import canonical

SCHEMA = json.loads((Path(__file__).resolve().parent / "schemas" / "experiment.schema.json").read_text(encoding="utf-8"))


def load(path: Path) -> dict:
    return canonical.load_strict(Path(path).read_text(encoding="utf-8"))


def read_anchors(path: Path) -> set[str]:
    """The anchors of a source page, one per line, comments and blank lines left out."""
    return {line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


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
             anchors: set[str] | None = None) -> list[str]:
    """What the validator cannot say about an experiment: its files, hashes, names and quantities. Without a results
    schema the quantities are not checked; without anchors the sources are not."""
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
    check_ids = [c["id"] for c in experiment["checks"]]
    if len(set(check_ids)) != len(check_ids):
        out.append("a check's id is repeated")
    for c in experiment["checks"]:
        named = [i for pair in c.get("pairs", []) for i in pair] + c.get("members", [])
        out += [f"{c['id']}: no member {i}" for i in named if i not in ids]
    if results_schema is not None:
        for q in experiment["reports"] + [c["quantity"] for c in experiment["checks"]]:
            if not resolves(q, results_schema):
                out.append(f"the results schema has no {q}")
    for s in experiment.get("report_scripts", []):
        if not (folder / s["path"]).is_file():
            out.append(f"no report script {s['path']}")
    if anchors is not None:
        out += [f"the source page has no anchor {a}" for a in experiment.get("sources", {}).get("bst", [])
                if a not in anchors]
    return out
