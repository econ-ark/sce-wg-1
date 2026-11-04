"""Generate the ontology's Turtle file and JSON table from its one source, or check that they are current.

    uv run --with pyyaml --with jsonschema python generate.py            # write both files
    uv run --with pyyaml --with jsonschema python generate.py --check    # exit 1 if either is out of date

The source is source.yaml, validated against source.schema.json. The generated files are probability-distributions.ttl,
OWL 2 in Turtle, and probability-distributions.json, a flat table with one row per measure, operator, property,
constraint, family and chart, references resolved to identifiers. The same source always gives the same bytes.

Beyond the schema, the generator refuses a source whose identifiers repeat or reuse a retired one, whose names repeat,
whose references do not resolve, whose formulas leave the formula syntax or name what their place does not allow, whose
charts lack a conversion to the canonical chart or label it wrongly, or whose written forms and cross-references use a
format or prefix the source does not declare.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import yaml

import formulas

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source.yaml"
SCHEMA = HERE / "source.schema.json"
TURTLE = HERE / "probability-distributions.ttl"
TABLE = HERE / "probability-distributions.json"

KINDS = {"measures": "measure", "operators": "operator", "properties": "property", "constraints": "constraint"}


class SourceError(ValueError):
    pass


def load(path: Path = SOURCE) -> tuple[dict, str]:
    """The source, validated against its schema, and the SHA-256 of its bytes."""
    raw = path.read_bytes()
    source = yaml.safe_load(raw.decode("utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(source), key=lambda e: list(e.path))
    if errors:
        raise SourceError(
            "; ".join(f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors[:10])
        )
    return source, hashlib.sha256(raw).hexdigest()


def _check_formula(text: str, allowed: set[str], where: str, expectation: bool = False) -> str:
    try:
        extra = formulas.names(text) - allowed
        if formulas.uses_expectation(text) and not expectation:
            raise SourceError(f"{where}: {text!r} takes an expectation, which only a coordinate's as_expectation may")
    except formulas.FormulaError as e:
        raise SourceError(f"{where}: {e}") from None
    if extra:
        raise SourceError(f"{where}: {text!r} names {sorted(extra)}; only {sorted(allowed)} are allowed here")
    return text


def _check_definitions(definitions: dict, allowed: set[str], where: str) -> tuple[dict, set[str]]:
    """Check auxiliary definitions in order: each may use the allowed names and the definitions before it."""
    names = set(allowed)
    for name, text in definitions.items():
        if name in names:
            raise SourceError(f"{where}: the auxiliary {name!r} shadows a name already in use")
        _check_formula(text, names, f"{where}, {name}")
        names.add(name)
    return dict(definitions), names


def build(source: dict, digest: str) -> dict:
    """Resolve the source into the table: every check the schema cannot make, then one row per object."""
    meta = source["ontology"]
    retired = set(source["retired"])
    seen_ids: dict[str, str] = {}

    def claim(identifier: str, what: str) -> str:
        if identifier in retired:
            raise SourceError(f"{what}: {identifier} is retired and may not be used again")
        if identifier in seen_ids:
            raise SourceError(f"{what}: {identifier} is already {seen_ids[identifier]}")
        seen_ids[identifier] = what
        return identifier

    # Names, by kind.
    index: dict[str, dict[str, dict]] = {}
    for key in (*KINDS, "families"):
        index[key] = {}
        for row in source[key]:
            if row["name"] in index[key]:
                raise SourceError(f"{key}: the name {row['name']!r} is used twice")
            index[key][row["name"]] = row
            claim(row["id"], f"{key[:-1] if key != 'properties' else 'property'} {row['name']}")
    families = index["families"]
    for fam in source["families"]:
        names = [c["name"] for c in fam["charts"]]
        if len(set(names)) != len(names):
            raise SourceError(f"family {fam['name']}: a chart name is used twice")
        for chart in fam["charts"]:
            claim(chart["id"], f"chart {fam['name']}/{chart['name']}")

    def ident(key: str, name: str, where: str) -> str:
        if name not in index[key]:
            raise SourceError(f"{where}: no {key[:-1] if key != 'properties' else 'property'} named {name!r}")
        return index[key][name]["id"]

    def root_of(fam: dict) -> dict:
        chain = [fam["name"]]
        while "subfamily_of" in fam:
            parent = fam["subfamily_of"]
            if parent not in families:
                raise SourceError(f"family {chain[-1]}: no family named {parent!r}")
            if parent in chain:
                raise SourceError(f"family {fam['name']}: subfamily_of loops through {chain}")
            chain.append(parent)
            fam = families[parent]
        return fam

    def canonical_of(root: dict) -> dict:
        charts = {c["name"]: c for c in root["charts"]}
        if root["canonical_chart"] not in charts:
            raise SourceError(f"family {root['name']}: no chart named {root['canonical_chart']!r}")
        return charts[root["canonical_chart"]]

    def coords(chart: dict) -> list[str]:
        return [c["name"] for c in chart["coordinates"]]

    formats = set(meta["formats"])
    prefixes = meta["prefixes"]
    rows: list[dict] = []

    for m in source["measures"]:
        where = f"measure {m['name']}"
        rows.append({"id": m["id"], "kind": "measure", "name": m["name"], "label": m["label"],
                     "stated_set": m["stated_set"], "notation": m["notation"],
                     "density": _check_formula(m["density"], {"z"}, f"{where}, density"),
                     "support": {k: _check_formula(m["support"][k], set(), f"{where}, support") for k in ("lower", "upper")},
                     "definition": m["definition"]})

    for op in source["operators"]:
        where = f"operator {op['name']}"
        row = {"id": op["id"], "kind": "operator", "name": op["name"], "label": op["label"]}
        if "case_of" in op:
            row["case_of"] = ident("operators", op["case_of"], where)
        row["arguments"] = [dict(a) for a in op["arguments"]]
        for key in ("map", "set"):
            if key in op:
                row[key] = _check_formula(op[key], {"z"} | {a["name"] for a in op["arguments"]}, where)
        if "written_as" in op:
            for fmt in op["written_as"]:
                if fmt not in meta["formats"]:
                    raise SourceError(f"{where}: the format {fmt!r} is not declared")
            row["written_as"] = {fmt: [dict(f) for f in forms] for fmt, forms in op["written_as"].items()}
        row["definition"] = op["definition"]
        rows.append(row)

    for p in source["properties"]:
        rows.append({"id": p["id"], "kind": "property", "name": p["name"], "label": p["label"],
                     "definition": p["definition"]})

    for con in source["constraints"]:
        where = f"constraint {con['name']}"
        rows.append({"id": con["id"], "kind": "constraint", "name": con["name"], "label": con["label"],
                     "property": ident("properties", con["property"], where), "relation": con["relation"],
                     "value": _check_formula(con["value"], set(), where), "definition": con["definition"]})

    for fam in source["families"]:
        where = f"family {fam['name']}"
        root = root_of(fam)
        canonical = canonical_of(root)
        canon = coords(canonical)
        row = {"id": fam["id"], "kind": "family", "name": fam["name"], "label": fam["label"]}
        if fam is root:
            row["stated_set"] = fam["stated_set"]
        else:
            row["subfamily_of"] = families[fam["subfamily_of"]]["id"]
            row["constraints"] = [ident("constraints", c, where) for c in fam["constraints"]]
        row["definition"] = fam["definition"]
        aux, known = _check_definitions(fam.get("where", {}), set(canon), f"{where}, where") if fam is root \
            else ({}, set(canon))
        state = fam.get("state")
        if state is not None:
            _check_formula(state["range"], known, f"{where}, state range")
        if fam is root:
            row["measure"] = fam["measure"]
            if state is not None:
                row["state"] = dict(state)
            if "built_from" in fam:
                mixing = fam["built_from"].get("mixture")
                component_names = known | ({"j"} if mixing else set())
                steps = []
                for i, step in enumerate(fam["built_from"]["operators"]):
                    op = index["operators"].get(step["operator"])
                    if op is None:
                        raise SourceError(f"{where}: no operator named {step['operator']!r}")
                    expected = {a["name"] for a in op["arguments"]}
                    given = set(step) - {"operator"}
                    if given != expected:
                        raise SourceError(f"{where}: step {i} gives {sorted(given)} to {op['name']}, "
                                          f"which takes {sorted(expected)}")
                    steps.append({"operator": op["id"], "arguments": {
                        a["name"]: _check_formula(step[a["name"]], component_names, f"{where}, step {i}")
                        for a in op["arguments"]}})
                row["built_from"] = {"base": ident("measures", fam["built_from"]["base"], where),
                                     "operators": steps}
                if mixing:
                    row["built_from"] = {"mixture": {"weights": _check_formula(mixing["weights"], known,
                                                                               f"{where}, mixture weights")},
                                         **row["built_from"]}
            if aux:
                row["where"] = aux
            row["canonical_chart"] = canonical["id"]
        row["charts"] = [c["id"] for c in fam["charts"]]
        if fam is root:
            props = {}
            for name, value in fam["properties"].items():
                ident("properties", name, where)
                allowed = known | ({"k"} if name in ("moments", "log-moments") else set()) \
                    | ({state["name"]} if state else set())
                if isinstance(value, str):
                    props[name] = _check_formula(value, allowed, f"{where}, {name}")
                elif isinstance(value, list):
                    props[name] = [{k: _check_formula(v, allowed, f"{where}, {name}") for k, v in item.items()}
                                   for item in value]
                else:
                    props[name] = {k: (_check_formula(v, allowed, f"{where}, {name}.{k}") if isinstance(v, str)
                                       and k not in ("orders",) else v) for k, v in value.items()}
            row["properties"] = props
            bounds = []
            for b in fam.get("boundaries", []):
                coordinate, _, value = b["where"].partition(" = ")
                if coordinate not in canon:
                    raise SourceError(f"{where}: a boundary's condition names {coordinate!r}, "
                                      f"not a canonical coordinate")
                _check_formula(value, set(canon), f"{where}, boundary")
                target = families.get(b["family"])
                if target is None or "subfamily_of" in target:
                    raise SourceError(f"{where}: a boundary names {b['family']!r}, which is not a root family")
                charts = {c["name"]: c for c in target["charts"]}
                if b["chart"] not in charts:
                    raise SourceError(f"{where}: family {b['family']} has no chart {b['chart']!r}")
                free = set(coords(charts[b["chart"]]))
                if not free <= set(canon) - {coordinate}:
                    raise SourceError(f"{where}: the boundary chart's coordinates {sorted(free)} must be "
                                      f"canonical coordinates of {fam['name']} other than {coordinate}")
                bounds.append({"where": b["where"], "family": target["id"], "chart": charts[b["chart"]]["id"]})
            if bounds:
                row["boundaries"] = bounds
            reductions = []
            for r in fam.get("reductions", []):
                _check_formula(r["when"], known, f"{where}, reduction")
                target = families.get(r["family"])
                if target is None or "subfamily_of" in target:
                    raise SourceError(f"{where}: a reduction names {r['family']!r}, which is not a root family")
                charts = {c["name"]: c for c in target["charts"]}
                if r["chart"] not in charts:
                    raise SourceError(f"{where}: family {r['family']} has no chart {r['chart']!r}")
                if not set(coords(charts[r["chart"]])) <= set(canon):
                    raise SourceError(f"{where}: a reduction's chart must use canonical coordinates of {fam['name']}")
                reductions.append({"when": r["when"], "family": target["id"], "chart": charts[r["chart"]]["id"]})
            if reductions:
                row["reductions"] = reductions
        rows.append(row)

        for chart in fam["charts"]:
            cwhere = f"chart {fam['name']}/{chart['name']}"
            own = coords(chart)
            if len(set(own)) != len(own):
                raise SourceError(f"{cwhere}: a coordinate name is used twice")
            for c in chart["coordinates"]:
                for key in ("as_expectation", "as_component_expectation"):
                    if key in c:
                        _check_formula(c[key], {"X"}, f"{cwhere}, {c['name']}.{key}", expectation=True)
                if "as_component_expectation" in c and "mixture" not in root.get("built_from", {}):
                    raise SourceError(f"{cwhere}: {c['name']} has a component's meaning, but {root['name']} mixes nothing")
            is_canonical = fam is root and chart["name"] == root["canonical_chart"]
            crow = {"id": chart["id"], "kind": "chart", "name": chart["name"],
                    "qualified_name": f"{fam['name']}/{chart['name']}", "label": chart["label"],
                    "family": fam["id"], "canonical": is_canonical,
                    "coordinates": [dict(c) for c in chart["coordinates"]]}
            if "domain_conditions" in chart:
                crow["domain_conditions"] = [_check_formula(c, set(own), f"{cwhere}, domain condition")
                                             for c in chart["domain_conditions"]]
            conversion_keys = {"covers", "to_canonical", "from_canonical", "conversion", "to_canonical_where",
                               "from_canonical_where"}
            if is_canonical:
                if conversion_keys & set(chart):
                    raise SourceError(f"{cwhere}: the canonical chart carries no conversion")
            else:
                for key in ("to_canonical", "from_canonical", "conversion"):
                    if key not in chart:
                        raise SourceError(f"{cwhere}: a chart other than the canonical one needs {key}")
                if set(chart["to_canonical"]) != set(canon):
                    raise SourceError(f"{cwhere}: to_canonical must give exactly {canon}")
                if set(chart["from_canonical"]) != set(own):
                    raise SourceError(f"{cwhere}: from_canonical must give exactly {own}")
                if "covers" in chart:
                    crow["covers"] = _check_formula(chart["covers"], set(canon), f"{cwhere}, covers")
                to_aux, to_known = _check_definitions(chart.get("to_canonical_where", {}), set(own),
                                                      f"{cwhere}, to_canonical_where")
                from_aux, from_known = _check_definitions(chart.get("from_canonical_where", {}), set(canon),
                                                          f"{cwhere}, from_canonical_where")
                if to_aux:
                    crow["to_canonical_where"] = to_aux
                crow["to_canonical"] = {k: _check_formula(chart["to_canonical"][k], to_known, f"{cwhere}, {k}")
                                        for k in canon}
                if from_aux:
                    crow["from_canonical_where"] = from_aux
                crow["from_canonical"] = {k: _check_formula(chart["from_canonical"][k], from_known, f"{cwhere}, {k}")
                                          for k in own}
                exact = all(formulas.is_exact(f) for f in (*to_aux.values(), *crow["to_canonical"].values(),
                                                           *from_aux.values(), *crow["from_canonical"].values()))
                if chart["conversion"] != ("exact" if exact else "irrational"):
                    raise SourceError(f"{cwhere}: its formulas make the conversion "
                                      f"{'exact' if exact else 'irrational'}, not {chart['conversion']}")
                crow["conversion"] = chart["conversion"]
            if "written_as" in chart:
                for fmt, forms in chart["written_as"].items():
                    if fmt not in formats:
                        raise SourceError(f"{cwhere}: the format {fmt!r} is not declared")
                    for form in forms:
                        args = form.get("arguments", [])
                        for a in (args.values() if isinstance(args, dict) else args):
                            _check_formula(a, set(own), f"{cwhere}, {fmt} argument")
                        for k, v in form.get("defaults", {}).items():
                            if not isinstance(args, dict) or k not in args:
                                raise SourceError(f"{cwhere}: a default for {k!r}, which is not a field of {fmt}")
                            _check_formula(v, set(), f"{cwhere}, default of {k}")
                        for k, v in form.get("none", {}).get("values", {}).items():
                            if not isinstance(args, dict) or k not in args:
                                raise SourceError(f"{cwhere}: a none value for {k!r}, which is not a field of {fmt}")
                            _check_formula(v, set(), f"{cwhere}, none value of {k}")
                crow["written_as"] = {fmt: [dict(form) for form in forms] for fmt, forms in chart["written_as"].items()}
            if "cross_references" in chart:
                refs = []
                for ref in chart["cross_references"]:
                    prefix, _, local = ref["target"].partition(":")
                    if prefix not in prefixes:
                        raise SourceError(f"{cwhere}: the prefix {prefix!r} is not declared")
                    refs.append({"predicate": ref["predicate"], "target": ref["target"],
                                 "iri": prefixes[prefix] + local, **({"note": ref["note"]} if "note" in ref else {})})
                crow["cross_references"] = refs
            if "provenance" in chart:
                crow["provenance"] = chart["provenance"]
            rows.append(crow)

    rows.sort(key=lambda r: r["id"])
    return {
        "ontology": {
            "title": meta["title"], "version": meta["version"], "namespace": meta["namespace"],
            "prefix": meta["prefix"], "license": meta["license"], "formats": meta["formats"],
            "prefixes": meta["prefixes"], "sources": meta["sources"], "source_sha256": digest,
        },
        "retired": sorted(retired),
        "rows": rows,
    }


# ----------------------------------------------------------------------------------------------------------------------
# Turtle

VOCABULARY = {
    "classes": {
        "Measure": "A measure on a stated set.",
        "Family": "A named map from a parameter space into measures. A kernel is a family one of whose arguments is a state.",
        "Chart": "A coordinate system on a family's parameters. It changes no measure.",
        "Operator": "A map from measures to measures.",
        "Property": "A map from a measure to a value.",
        "Constraint": "A property set equal to, or bounded by, a value. A constraint on a family defines a subfamily.",
    },
    "object": {
        "caseOf": "The operator of which this one is a named case.",
        "constrains": "The property a constraint sets.",
        "subfamilyOf": "The family whose members satisfying the constraints make up this one.",
        "hasConstraint": "A constraint defining the subfamily.",
        "canonicalChart": "The chart in which two laws of the family are compared.",
        "hasChart": "A chart of the family.",
        "chartOf": "The family a chart coordinatizes.",
        "builtFrom": "The family's measure as operators applied in order to a named measure.",
        "base": "The measure a construction starts from.",
        "step": "One operator of a construction.",
        "operator": "The operator a step applies.",
        "boundary": "Where the canonical chart's domain ends at a member of another family.",
        "boundaryChart": "The chart of the other family that writes the members at the boundary.",
        "reduction": "Where a point of the canonical chart is a member of another family.",
        "reductionChart": "The chart of the other family that writes the members a reduction names.",
        "auxiliary": "An auxiliary quantity of the family, a formula in the canonical coordinates.",
        "toCanonicalAuxiliary": "An auxiliary quantity of the conversion to the canonical chart.",
        "fromCanonicalAuxiliary": "An auxiliary quantity of the conversion from the canonical chart.",
        "hasPropertyValue": "The value of a property for the family's members, in the canonical coordinates.",
        "support": "The support of a named measure, by its infimum and supremum.",
        "property": "The property a value is the value of.",
        "coordinate": "A coordinate of the chart.",
        "toCanonical": "A formula giving one canonical coordinate in this chart's coordinates.",
        "fromCanonical": "A formula giving one of this chart's coordinates in the canonical coordinates.",
        "writtenAs": "How a format writes a point of the chart.",
        "argument": "An argument of an operator, or of one step of a construction.",
        "state": "A kernel's state argument.",
    },
    "data": {
        "statedSet": "The set the measures live on.",
        "notation": "The mathematical notation for the measure.",
        "density": "A measure's density with respect to Lebesgue measure, as a formula in z.",
        "measureExpression": "The family's measure in the operator notation, in the canonical coordinates.",
        "map": "The map of a case of the pushforward, as a formula in z and the arguments.",
        "set": "The set of a case of conditioning, as a condition in z and the arguments.",
        "when": "The condition of a reduction.",
        "domainCondition": "A condition on a chart's coordinates jointly.",
        "head": "The name a format gives the law: a stage file's family call, a parameter file's key.",
        "relation": "How a constraint relates its property to its value.",
        "value": "A value, as a formula.",
        "position": "The position of a coordinate, a step or an argument, from one.",
        "name": "A name within its row: of a coordinate, an argument, or a format.",
        "symbol": "The symbol of a coordinate.",
        "meaning": "What a coordinate or an argument is.",
        "domain": "The domain of a coordinate.",
        "asExpectation": "A coordinate's meaning as an expectation under the law, a formula in E(·) of the draw X.",
        "asComponentExpectation": "A mixture chart's vector coordinate's meaning, entry by entry, as an expectation under each component's law.",
        "formula": "A formula in the ontology's formula syntax.",
        "covers": "The part of the canonical chart's domain a chart reaches, as a condition.",
        "conversion": "exact when the conversion is rational in the coordinates; irrational otherwise.",
        "format": "A written form, by its name in the ontology.",
        "spelling": "How the format writes a point of the chart.",
        "default": "A coordinate's default in a written form, as name = value.",
        "noneToken": "The token a format writes for an absent bound.",
        "noneValue": "The value the none token stands for in a field, as name = value.",
        "perComponent": "Whether a written form gives its fields once per component of a mixture.",
        "where": "A boundary's condition.",
        "infimum": "The infimum of the support.",
        "supremum": "The supremum of the support.",
        "massAtInfimum": "The mass at the infimum of the support.",
        "orders": "The orders for which a moment is finite.",
        "atomAt": "The point of an atom.",
        "atomMass": "The mass of an atom.",
        "provenance": "Where a row's content comes from, when it is copied.",
        "range": "The number of positions a kernel's state takes, as a formula.",
        "mixtureWeights": "The weights of a construction's components, as a formula.",
        "sourceDigest": "The SHA-256 of the source file the ontology was generated from.",
    },
}

ANNOTATIONS = ["skos:definition", "skos:notation", "skos:exactMatch", "skos:closeMatch", "skos:broadMatch",
               "skos:narrowMatch", "skos:relatedMatch", "dcterms:license", "dcterms:source",
               "dcterms:bibliographicCitation"]

KIND_CLASS = {"measure": "Measure", "family": "Family", "chart": "Chart", "operator": "Operator",
              "property": "Property", "constraint": "Constraint"}


def _lit(text, lang: str | None = None) -> str:
    s = str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
    return f'"{s}"' + (f"@{lang}" if lang else "")


def _block(subject: str, pairs: list[tuple[str, str]], indent: str = "") -> str:
    lines = [f"{indent}{subject}"]
    for i, (p, o) in enumerate(pairs):
        end = " ." if i == len(pairs) - 1 else " ;"
        lines.append(f"{indent}    {p} {o}{end}")
    return "\n".join(lines)


def _bnode(pairs: list[tuple[str, str]]) -> str:
    return "[ " + " ; ".join(f"{p} {o}" for p, o in pairs) + " ]"


def _written_pairs(pd: str, row: dict) -> list[tuple[str, str]]:
    pairs = []
    for fmt, forms in row.get("written_as", {}).items():
        for form in forms:
            inner = [(f"{pd}:format", _lit(fmt)), (f"{pd}:spelling", _lit(form["spelling"])),
                     (f"{pd}:head", _lit(form["head"]))]
            args = form.get("arguments", [])
            items = args.items() if isinstance(args, dict) else ((None, a) for a in args)
            for i, (k, v) in enumerate(items, 1):
                inner.append((f"{pd}:argument", _bnode([(f"{pd}:position", str(i))]
                                                       + ([(f"{pd}:name", _lit(k))] if k else [])
                                                       + [(f"{pd}:formula", _lit(v))])))
            inner += [(f"{pd}:default", _lit(f"{k} = {v}")) for k, v in form.get("defaults", {}).items()]
            if form.get("per_component"):
                inner.append((f"{pd}:perComponent", "true"))
            if "none" in form:
                inner.append((f"{pd}:noneToken", _lit(form["none"]["token"])))
                inner += [(f"{pd}:noneValue", _lit(f"{k} = {v}")) for k, v in form["none"]["values"].items()]
            pairs.append((f"{pd}:writtenAs", _bnode(inner)))
    return pairs


def turtle(table: dict) -> str:
    meta = table["ontology"]
    ns = meta["namespace"]
    pd = meta["prefix"]
    out = [
        f"# {meta['title']}, version {meta['version']}. Generated by generate.py from source.yaml; do not edit.",
        f"@prefix {pd}: <{ns}> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
    ]
    for prefix, iri in meta["prefixes"].items():
        out.append(f"@prefix {prefix}: <{iri}> .")
    out.append("")

    header = [("a", "owl:Ontology"), ("rdfs:label", _lit(meta["title"], "en")),
              ("owl:versionInfo", _lit(meta["version"])), ("dcterms:license", f"<{meta['license']}>")]
    for src in meta["sources"]:
        header.append(("dcterms:source", f"<{src['iri']}>"))
        header.append(("dcterms:bibliographicCitation", _lit(src["citation"], "en")))
    header.append((f"{pd}:sourceDigest", _lit("sha256:" + meta["source_sha256"])))
    out.append(_block(f"<{ns.rstrip('/')}>", header))
    out.append("")

    for p in ANNOTATIONS:
        out.append(f"{p} a owl:AnnotationProperty .")
    for name, text in VOCABULARY["classes"].items():
        out.append(_block(f"{pd}:{name}", [("a", "owl:Class"), ("rdfs:label", _lit(name.lower(), "en")),
                                             ("skos:definition", _lit(text, "en"))]))
    for name, text in VOCABULARY["object"].items():
        out.append(_block(f"{pd}:{name}", [("a", "owl:ObjectProperty"), ("skos:definition", _lit(text, "en"))]))
    for name, text in VOCABULARY["data"].items():
        out.append(_block(f"{pd}:{name}", [("a", "owl:DatatypeProperty"), ("skos:definition", _lit(text, "en"))]))
    out.append("")

    def ref(identifier: str) -> str:
        return f"{pd}:{identifier}"

    def formula_pairs(mapping: dict) -> list[str]:
        return [_bnode([(f"{pd}:name", _lit(k)), (f"{pd}:formula", _lit(v))]) for k, v in mapping.items()]

    for row in table["rows"]:
        pairs = [("a", f"owl:NamedIndividual, {pd}:{KIND_CLASS[row['kind']]}"),
                 ("rdfs:label", _lit(row["label"], "en")), ("skos:notation", _lit(row.get("qualified_name", row["name"])))]
        if "definition" in row:
            pairs.append(("skos:definition", _lit(row["definition"], "en")))
        kind = row["kind"]
        if kind == "measure":
            pairs += [(f"{pd}:statedSet", _lit(row["stated_set"])), (f"{pd}:notation", _lit(row["notation"])),
                      (f"{pd}:density", _lit(row["density"])),
                      (f"{pd}:support", _bnode([(f"{pd}:infimum", _lit(row["support"]["lower"])),
                                                (f"{pd}:supremum", _lit(row["support"]["upper"]))]))]
        elif kind == "operator":
            if "case_of" in row:
                pairs.append((f"{pd}:caseOf", ref(row["case_of"])))
            for i, a in enumerate(row["arguments"], 1):
                pairs.append((f"{pd}:argument", _bnode([(f"{pd}:position", str(i)), (f"{pd}:name", _lit(a["name"])),
                                                       (f"{pd}:meaning", _lit(a["meaning"], "en"))])))
            for key in ("map", "set"):
                if key in row:
                    pairs.append((f"{pd}:{key}", _lit(row[key])))
            pairs += _written_pairs(pd, row)
        elif kind == "constraint":
            pairs += [(f"{pd}:constrains", ref(row["property"])), (f"{pd}:relation", _lit(row["relation"])),
                      (f"{pd}:value", _lit(row["value"]))]
        elif kind == "family":
            if "stated_set" in row:
                pairs.append((f"{pd}:statedSet", _lit(row["stated_set"])))
            if "subfamily_of" in row:
                pairs.append((f"{pd}:subfamilyOf", ref(row["subfamily_of"])))
                pairs += [(f"{pd}:hasConstraint", ref(c)) for c in row["constraints"]]
            if "measure" in row:
                pairs.append((f"{pd}:measureExpression", _lit(row["measure"])))
            if "state" in row:
                st = row["state"]
                pairs.append((f"{pd}:state", _bnode([(f"{pd}:name", _lit(st["name"])), (f"{pd}:symbol", _lit(st["symbol"])),
                                                     (f"{pd}:meaning", _lit(st["meaning"], "en")),
                                                     (f"{pd}:range", _lit(st["range"]))])))
            if "built_from" in row:
                steps = []
                for i, s in enumerate(row["built_from"]["operators"], 1):
                    args = [_bnode([(f"{pd}:position", str(j)), (f"{pd}:name", _lit(k)), (f"{pd}:formula", _lit(v))])
                            for j, (k, v) in enumerate(s["arguments"].items(), 1)]
                    steps.append(_bnode([(f"{pd}:position", str(i)), (f"{pd}:operator", ref(s["operator"]))]
                                        + [(f"{pd}:argument", a) for a in args]))
                mixing = row["built_from"].get("mixture")
                pairs.append((f"{pd}:builtFrom", _bnode(
                    ([(f"{pd}:mixtureWeights", _lit(mixing["weights"]))] if mixing else [])
                    + [(f"{pd}:base", ref(row["built_from"]["base"]))] + [(f"{pd}:step", s) for s in steps])))
            for i, (k, v) in enumerate(row.get("where", {}).items(), 1):
                pairs.append((f"{pd}:auxiliary", _bnode([(f"{pd}:position", str(i)), (f"{pd}:name", _lit(k)),
                                                         (f"{pd}:formula", _lit(v))])))
            if "canonical_chart" in row:
                pairs.append((f"{pd}:canonicalChart", ref(row["canonical_chart"])))
            pairs += [(f"{pd}:hasChart", ref(c)) for c in row["charts"]]
            for name, value in row.get("properties", {}).items():
                prop = next(r["id"] for r in table["rows"] if r["kind"] == "property" and r["name"] == name)
                inner = [(f"{pd}:property", ref(prop))]
                if isinstance(value, str):
                    inner.append((f"{pd}:formula", _lit(value)))
                elif isinstance(value, list):
                    inner += [(f"{pd}:value", _bnode([(f"{pd}:atomAt", _lit(a["at"])), (f"{pd}:atomMass", _lit(a["mass"]))]))
                              for a in value]
                else:
                    keymap = {"infimum": "infimum", "supremum": "supremum", "mass_at_infimum": "massAtInfimum",
                              "orders": "orders", "formula": "formula"}
                    for k, v in value.items():
                        obj = ("true" if v else "false") if isinstance(v, bool) else _lit(v)
                        inner.append((f"{pd}:{keymap[k]}", obj))
                pairs.append((f"{pd}:hasPropertyValue", _bnode(inner)))
            for b in row.get("boundaries", []):
                pairs.append((f"{pd}:boundary", _bnode([(f"{pd}:where", _lit(b["where"])),
                                                        (f"{pd}:boundaryChart", ref(b["chart"]))])))
            for r in row.get("reductions", []):
                pairs.append((f"{pd}:reduction", _bnode([(f"{pd}:when", _lit(r["when"])),
                                                         (f"{pd}:reductionChart", ref(r["chart"]))])))
        elif kind == "chart":
            pairs.append((f"{pd}:chartOf", ref(row["family"])))
            for i, c in enumerate(row["coordinates"], 1):
                pairs.append((f"{pd}:coordinate", _bnode([(f"{pd}:position", str(i)), (f"{pd}:name", _lit(c["name"])),
                                                         (f"{pd}:symbol", _lit(c["symbol"])),
                                                         (f"{pd}:meaning", _lit(c["meaning"], "en")),
                                                         (f"{pd}:domain", _lit(c["domain"]))]
                                                        + ([(f"{pd}:asExpectation", _lit(c["as_expectation"]))]
                                                           if "as_expectation" in c else [])
                                                        + ([(f"{pd}:asComponentExpectation",
                                                             _lit(c["as_component_expectation"]))]
                                                           if "as_component_expectation" in c else []))))
            pairs += [(f"{pd}:domainCondition", _lit(c)) for c in row.get("domain_conditions", [])]
            if "covers" in row:
                pairs.append((f"{pd}:covers", _lit(row["covers"])))
            for key, prop in (("to_canonical_where", "toCanonicalAuxiliary"), ("from_canonical_where", "fromCanonicalAuxiliary")):
                for i, (k, v) in enumerate(row.get(key, {}).items(), 1):
                    pairs.append((f"{pd}:{prop}", _bnode([(f"{pd}:position", str(i)), (f"{pd}:name", _lit(k)),
                                                          (f"{pd}:formula", _lit(v))])))
            pairs += [(f"{pd}:toCanonical", b) for b in formula_pairs(row.get("to_canonical", {}))]
            pairs += [(f"{pd}:fromCanonical", b) for b in formula_pairs(row.get("from_canonical", {}))]
            if "conversion" in row:
                pairs.append((f"{pd}:conversion", _lit(row["conversion"])))
            pairs += _written_pairs(pd, row)
            for x in row.get("cross_references", []):
                pairs.append((x["predicate"], f"<{x['iri']}>"))
            if "provenance" in row:
                pairs.append((f"{pd}:provenance", _lit(row["provenance"], "en")))
        out.append(_block(ref(row["id"]), pairs))
        out.append("")
    return "\n".join(out)


def table_json(table: dict) -> str:
    return json.dumps(table, ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if a generated file is out of date")
    args = parser.parse_args(argv)
    try:
        source, digest = load()
        table = build(source, digest)
    except SourceError as e:
        print(f"source.yaml: {e}", file=sys.stderr)
        return 1
    outputs = {TABLE: table_json(table), TURTLE: turtle(table)}
    if args.check:
        stale = [p.name for p, text in outputs.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if stale:
            print(f"out of date: {', '.join(stale)}; run generate.py", file=sys.stderr)
            return 1
        return 0
    for path, text in outputs.items():
        path.write_text(text, encoding="utf-8")
    print(f"wrote {TABLE.name} and {TURTLE.name}: {len(table['rows'])} rows, version {table['ontology']['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
