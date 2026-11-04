"""Generate the ontology's Turtle file and JSON table from its one source, or check that they are current.

    uv run --with pyyaml --with jsonschema python generate.py            # write both files
    uv run --with pyyaml --with jsonschema python generate.py --check    # exit 1 if either is out of date

The source is source.yaml, validated against source.schema.json. The generated files are buffer-stock-models.ttl, OWL 2
in Turtle, and buffer-stock-models.json, a flat table with one row per term, references resolved to identifiers. The same
source always gives the same bytes.

Beyond the schema, the generator refuses a source whose identifiers repeat or reuse a retired one, whose names repeat,
whose references do not resolve, whose formulas leave the formula syntax or name a symbol not defined before them, whose
results assume or conclude anything but a condition or a property, whose perches and states do not resolve or disagree,
or whose citations are not pinned: a bst anchor not in bst-anchors.txt, a registry key not in registry-keys.txt, a
Bellman-SYM concept not in bellman-concepts.txt, a law or law property not a row of the ontology of probability
distributions, a source, format or format role the source does not declare.

The formula syntax is the ontology of probability distributions' (its formulas.py), shared rather than copied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import jsonschema
import yaml

HERE = Path(__file__).resolve().parent
PD = HERE.parent / "probability-distributions"
sys.path.insert(0, str(PD))
import formulas  # noqa: E402  the formula syntax of the ontology of probability distributions

SOURCE = HERE / "source.yaml"
SCHEMA = HERE / "source.schema.json"
TURTLE = HERE / "buffer-stock-models.ttl"
TABLE = HERE / "buffer-stock-models.json"
BST_ANCHORS = HERE / "bst-anchors.txt"
REGISTRY_KEYS = HERE / "registry-keys.txt"
BELLMAN_CONCEPTS = HERE / "bellman-concepts.txt"
PD_TABLE = PD / "probability-distributions.json"

# The source's sections, in order, with the kind each row is of.
SECTIONS = {
    "model-classes": "model-class", "axioms": "axiom", "objects": "object", "moments": "moment",
    "quantities": "quantity", "conditions": "condition", "properties": "property", "results": "result",
    "identities": "identity", "families": "family", "divergences": "divergence",
}
EXPECTATION_DRAW = "X"  # the draw a moment's E(...) is taken over


class SourceError(ValueError):
    pass


def _pinned(path: Path) -> set[str]:
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def load(path: Path = SOURCE) -> tuple[dict, str]:
    """The source, validated against its schema, and the SHA-256 of its bytes."""
    raw = path.read_bytes()
    source = yaml.safe_load(raw.decode("utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = sorted(jsonschema.Draft202012Validator(schema).iter_errors(source), key=lambda e: list(e.path))
    if errors:
        raise SourceError("; ".join(f"{'/'.join(map(str, e.path)) or '(root)'}: {e.message}" for e in errors[:10]))
    return source, hashlib.sha256(raw).hexdigest()


def rows(source: dict) -> list[tuple[str, dict]]:
    """Every row, with its kind, in the source's order."""
    return [(kind, row) for section, kind in SECTIONS.items() for row in source[section]]


def symbols(source: dict) -> dict[str, str]:
    """Each formula symbol, with the name of the row that defines it."""
    out = {}
    for section in ("objects", "moments", "quantities"):
        for row in source[section]:
            if "symbol" in row:
                out[row["symbol"]] = row["name"]
    return out


def check(source: dict) -> None:
    """Refuse a source that fails any check the schema cannot express."""
    problems: list[str] = []
    all_rows = rows(source)
    ids, names = {}, {}
    for kind, row in all_rows:
        if row["id"] in ids:
            problems.append(f"{row['id']} is used by {ids[row['id']]} and {row['name']}")
        if row["id"] in source["retired"]:
            problems.append(f"{row['name']}: {row['id']} is retired")
        if row["name"] in names:
            problems.append(f"the name {row['name']} is used twice")
        ids[row["id"]], names[row["name"]] = row["name"], kind
    by_kind = {kind: {r["name"] for k, r in all_rows if k == kind} for kind in SECTIONS.values()}

    def need(name, kinds, where):
        if names.get(name) not in kinds:
            problems.append(f"{where}: {name!r} is not a {' or '.join(kinds)}")

    # model classes and their axioms
    for row in source["model-classes"]:
        for key in ("subclass_of", "benchmark_of"):
            if key in row:
                need(row[key], {"model-class"}, f"{row['name']}/{key}")
        if "reduces_to" in row:
            need(row["reduces_to"]["class"], {"model-class"}, f"{row['name']}/reduces_to")
        for axiom in row.get("axioms", []):
            need(axiom, {"axiom"}, f"{row['name']}/axioms")
    axiom_of = {a["name"]: a["of"] for a in source["axioms"]}
    listed = {a: c["name"] for c in source["model-classes"] for a in c.get("axioms", [])}
    for name, of in axiom_of.items():
        need(of, {"model-class"}, f"{name}/of")
        if listed.get(name) != of:
            problems.append(f"{name}: of {of}, but listed by {listed.get(name)}")
    if not any(c["name"] == "buffer-stock-model" and "subclass_of" not in c for c in source["model-classes"]):
        problems.append("there is no root class buffer-stock-model")

    # objects: categories, perches and the states a value or a function is of
    objects = {row["name"]: row for row in source["objects"]}
    for row in source["objects"]:
        if row["category"] not in source["categories"]:
            problems.append(f"{row['name']}: no category {row['category']!r}")
        for key, category in (("perch", "perch"), ("of_state", "state")):
            if key in row and objects.get(row[key], {}).get("category") != category:
                problems.append(f"{row['name']}/{key}: {row[key]!r} is not an object of category {category}")
        state = objects.get(row.get("of_state"), {})
        if "perch" in row and "perch" in state and state["perch"] != row["perch"]:
            problems.append(f"{row['name']}: at {row['perch']}, but its state {state['name']} is at {state['perch']}")
    for category, concept in source["category_concepts"].items():
        if category not in source["categories"]:
            problems.append(f"category_concepts: no category {category!r}")
    roles = source["ontology"]["format_roles"]
    for fmt, spec in source["ontology"]["formats"].items():
        if spec["role"] not in roles:
            problems.append(f"format {fmt}: role {spec['role']!r} is not declared")

    # moments, quantities, conditions: the formulas
    syms = symbols(source)
    if len(syms) != sum("symbol" in r for s in ("objects", "moments", "quantities") for r in source[s]):
        problems.append("a formula symbol is defined twice")
    defined = {r["symbol"] for r in source["objects"] if "symbol" in r}

    def formula(text, allowed, where, expectation=False):
        try:
            if formulas.uses_expectation(text) and not expectation:
                problems.append(f"{where}: {text!r} takes an expectation, which only a moment may")
            extra = formulas.names(text) - allowed
            if extra:
                problems.append(f"{where}: {text!r} names {sorted(extra)}, not defined before it")
        except formulas.FormulaError as e:
            problems.append(f"{where}: {e}")

    for row in source["moments"]:
        need(row["of"], {"object"}, f"{row['name']}/of")
        formula(row["formula"], defined | {EXPECTATION_DRAW}, row["name"], expectation=True)
        defined.add(row["symbol"])
    for row in source["quantities"]:
        formula(row["formula"], defined, row["name"])
        defined.add(row["symbol"])
        if "domain" in row:
            need(row["domain"], {"condition"}, f"{row['name']}/domain")
    for row in source["conditions"]:
        need(row["factor"], {"quantity"}, f"{row['name']}/factor")
        formula(row["holds"], defined, row["name"])
    for row in source["axioms"]:
        if "check" in row:
            formula(row["check"], defined, row["name"])

    # results, families, divergences
    for row in source["results"]:
        for literal in row["assumes"] + row["concludes"]:
            need(literal.removeprefix("not "), {"condition", "property"}, f"{row['name']}")
        if "within" in row:
            need(row["within"], {"model-class"}, f"{row['name']}/within")
        if "limit_in" in row:
            need(row["limit_in"], {"model-class"}, f"{row['name']}/limit_in")
    for row in source["families"]:
        for c in row["writes"]:
            need(c, {"model-class"}, f"{row['name']}/writes")
        if not (HERE / row["schema"]).resolve().is_file():
            problems.append(f"{row['name']}: no schema at {row['schema']}")
    for row in source["divergences"]:
        if row["term"] not in names:
            problems.append(f"{row['name']}: no term {row['term']!r}")
        if row["where"] not in source["ontology"]["sources"]:
            problems.append(f"{row['name']}: where {row['where']!r} is not a declared source")

    # citations and written forms
    anchors, registry, concepts = _pinned(BST_ANCHORS), _pinned(REGISTRY_KEYS), _pinned(BELLMAN_CONCEPTS)
    pd_ids = {r["id"] for r in json.loads(PD_TABLE.read_text(encoding="utf-8"))["rows"]}
    for category, concept in source["category_concepts"].items():
        if concept not in concepts:
            problems.append(f"category_concepts/{category}: Bellman-SYM concept {concept!r} is not pinned")
    declared_sources, formats = source["ontology"]["sources"], source["ontology"]["formats"]
    for kind, row in all_rows:
        for key, cited in row.get("sources", {}).items():
            if key not in declared_sources:
                problems.append(f"{row['name']}: source {key!r} is not declared")
            if key == "bst":
                problems += [f"{row['name']}: bst anchor {a!r} is not pinned" for a in cited if a not in anchors]
        for fmt, spelling in row.get("written_as", {}).items():
            if fmt not in formats:
                problems.append(f"{row['name']}: format {fmt!r} is not declared")
            if fmt == "registry" and spelling not in registry:
                problems.append(f"{row['name']}: registry key {spelling!r} is not pinned")
        for pd_id in row.get("law", {}).get("pd", []) + row.get("law_property", {}).get("pd", []):
            if pd_id not in pd_ids:
                problems.append(f"{row['name']}: {pd_id} is not a row of the probability distributions")
        if "bellman_concept" in row and row["bellman_concept"] not in concepts:
            problems.append(f"{row['name']}: Bellman-SYM concept {row['bellman_concept']!r} is not pinned")
    if problems:
        raise SourceError("; ".join(problems))


# The generated files.

KIND_CLASS = {
    "model-class": "ModelClass", "axiom": "Axiom", "object": "Object", "moment": "Moment", "quantity": "Quantity",
    "condition": "Condition", "property": "Property", "result": "Result", "identity": "Identity",
    "family": "Family", "divergence": "Divergence",
}
FORMAT_PROPERTY = {"bst": "inBST", "registry": "registryKey", "parameter-file": "inParameterFile",
                   "bellman-sym": "inBellmanSym"}
OBJECT_PROPERTIES = {
    "axiomOf": "The model class an axiom belongs to.",
    "hasAxiom": "An axiom of a model class.",
    "benchmarkOf": "The class of which a model class is the limiting benchmark, outside it.",
    "reducesTo": "The class an extension reduces to under its stated restriction.",
    "momentOf": "The shock whose law a moment is taken under.",
    "dependsOn": "A row whose symbol a formula names.",
    "hasFactor": "The quantity a condition bounds.",
    "domain": "The condition under which a quantity is finite.",
    "assumes": "A condition or property a result assumes to hold.",
    "assumesFailureOf": "A condition or property a result assumes to fail.",
    "concludes": "A condition or property a result concludes holds.",
    "concludesFailureOf": "A condition or property a result concludes fails.",
    "within": "The model class to which a result applies.",
    "limitIn": "The model class in which the limit a result describes lies.",
    "writes": "A model class whose members a written family writes.",
    "concerns": "The term a divergence concerns.",
    "lawIn": "A family or constraint of the ontology of probability distributions that a shock's law belongs to.",
    "atPerch": "The perch at which a field is known, or a function's state lies.",
    "functionOf": "The state of which a value or a function is a function.",
    "lawProperty": "The property of a law, in the ontology of probability distributions, that a bound is.",
}
DATA_PROPERTIES = {
    "formula": "A formula in the ontology's formula syntax.",
    "holdsWhen": "The inequality under which a condition holds, in the formula syntax.",
    "check": "A predicate on the symbols that an axiom requires, in the formula syntax.",
    "symbol": "The name a formula uses for this row.",
    "tier": "membership, a requirement of the class; or hypothesis, an assumption of its results.",
    "status": "Who states it: the paper (bst), a citation in it, a ruling of the owner, a proposal, or a deduction.",
    "ruled": "The date of the owner's ruling.",
    "category": "The category of an object.",
    "resultKind": "A theorem, lemma, proposition, property or remark.",
    "identityKind": "An equivalence or a reduction.",
    "reductionWhen": "The restriction under which an extension is its parent.",
    "where": "Where a divergence is found.",
    "shortName": "A condition's abbreviation in the paper.",
    "note": "A note.",
    "schemaDocument": "The schema document of a written family, relative to this folder.",
    "sourceDigest": "The SHA-256 of the source this file was generated from.",
    "bellmanConcept": "The slug of Bellman-SYM's concept this term is, its documentation not being public.",
    "stateDomain": "The set a state or control takes its values in, as a stage file declares it.",
    "divergenceKind": "meaning, notation, approximation, convention or absence.",
    "formatRole": "notation, calibration or realization.",
}


def _lit(text: str, lang: bool = True) -> str:
    escaped = str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"@en' if lang else f'"{escaped}"'


def _camel(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("-"))


# The papers the ontology cites by their own numbering.
PAPERS = ("mst-2020", "mst-2022")


def source_urls(source: dict, cited: dict) -> list[str]:
    """The URLs of a row's citations: a bst anchor on the published page; a file and line at a pinned commit; a paper
    cited by its own numbering, as the paper's page."""
    base = {k: v["url"] for k, v in source["ontology"]["sources"].items()}
    out = []
    for a in cited.get("bst", []):
        out.append(f"{base['bst']}#{a}")
    for key in PAPERS:
        if cited.get(key):
            out.append(base[key])
    for key in ("hafiscal-qe",):
        root = base[key].replace("/tree/", "/blob/")
        for spec in cited.get(key, []):
            path, _, lines = spec.partition(":")
            anchor = ""
            if lines:
                first, _, last = lines.partition("-")
                anchor = f"#L{first}" + (f"-L{last}" if last else "")
            out.append(f"{root}/{path}{anchor}")
    return out


def table(source: dict, digest: str) -> dict:
    ident = {row["name"]: row["id"] for _, row in rows(source)}
    syms = symbols(source)

    def ref(name):
        return ident[name.removeprefix("not ")]

    out_rows = []
    for kind, row in rows(source):
        r = {"id": row["id"], "kind": kind}
        for key, value in row.items():
            if key == "id":
                continue
            if key == "kind":  # a result's or an identity's own kind, kept apart from the row's kind in the ontology
                r[f"{kind}_kind"] = value
                continue
            if key in ("subclass_of", "benchmark_of", "of", "factor", "within", "limit_in", "term", "domain", "perch", "of_state"):
                value = {"name": value, "id": ident.get(value, value)}
            elif key == "axioms" or key == "writes":
                value = [{"name": v, "id": ident[v]} for v in value]
            elif key in ("assumes", "concludes"):
                value = [{"literal": v, "id": ref(v), "holds": not v.startswith("not ")} for v in value]
            elif key == "reduces_to":
                value = {"class": {"name": value["class"], "id": ident[value["class"]]}, "when": value["when"]}
            r[key] = value
        text = row.get("formula") or row.get("holds") or row.get("check")
        if text:
            r["depends_on"] = sorted(ident[syms[s]] for s in formulas.names(text) if s in syms)
        if "sources" in row:
            r["source_urls"] = source_urls(source, row["sources"])
        out_rows.append(r)
    meta = dict(source["ontology"])
    meta["source_digest"] = f"sha256:{digest}"
    return {"ontology": meta, "kinds": source["kinds"], "categories": source["categories"],
            "retired": source["retired"], "rows": out_rows}


def turtle(source: dict, digest: str) -> str:
    o = source["ontology"]
    p = o["prefix"]
    ns = o["namespace"]
    ident = {row["name"]: row["id"] for _, row in rows(source)}
    syms = symbols(source)
    lines = [
        f"# {o['title']}, version {o['version']}. Generated by generate.py from source.yaml; do not edit.",
        f"@prefix {p}: <{ns}> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
    ]
    lines += [f"@prefix {k}: <{v}> ." for k, v in o["imports"].items()]
    lines.append("")
    head = [f"<{ns.rstrip('/')}>", "    a owl:Ontology ;", f"    rdfs:label {_lit(o['title'])} ;",
            f"    owl:versionInfo {_lit(o['version'], False)} ;", f"    dcterms:license <{o['license']}> ;"]
    head += [f"    owl:imports <{v.rstrip('/')}> ;" for v in o["imports"].values()]
    head += [f"    dcterms:source <{s['url']}> ;" for s in o["sources"].values()]
    head.append(f"    {p}:sourceDigest {_lit('sha256:' + digest, False)} .")
    lines += head + [""]
    for prop in ("skos:definition", "skos:notation", "skos:note", "dcterms:license", "dcterms:source"):
        lines.append(f"{prop} a owl:AnnotationProperty .")
    lines.append("")
    # the kinds and categories
    lines += [f"{p}:Model a owl:Class ;", f"    rdfs:label {_lit('model')} ;",
              f"    skos:definition {_lit('A model: a member of a model class.')} .", ""]
    for kind, cls in KIND_CLASS.items():
        lines += [f"{p}:{cls} a owl:Class ;", f"    rdfs:label {_lit(kind)} ;",
                  f"    skos:definition {_lit(source['kinds'][kind])} .", ""]
    for cat, text in source["categories"].items():
        concept = source["category_concepts"].get(cat)
        extra = [f"    {p}:bellmanConcept {_lit(concept, False)} ;"] if concept else []
        lines += [f"{p}:{_camel(cat)} a owl:Class ;", f"    rdfs:subClassOf {p}:Object ;", *extra,
                  f"    rdfs:label {_lit(cat)} ;", f"    skos:definition {_lit(text)} .", ""]
    for prop, text in OBJECT_PROPERTIES.items():
        lines += [f"{p}:{prop} a owl:ObjectProperty ;", f"    skos:definition {_lit(text)} .", ""]
    for prop, text in DATA_PROPERTIES.items():
        lines += [f"{p}:{prop} a owl:DatatypeProperty ;", f"    skos:definition {_lit(text)} .", ""]
    for fmt, prop in FORMAT_PROPERTY.items():
        spec = o["formats"][fmt]
        lines += [f"{p}:{prop} a owl:AnnotationProperty ;",
                  f"    skos:definition {_lit('Its written form in ' + spec['text'] + '.')} ;",
                  f"    {p}:formatRole {_lit(spec['role'], False)} .", ""]

    for kind, row in rows(source):
        me = f"{p}:{row['id']}"
        triples = []
        if kind == "model-class":
            triples.append("a owl:Class")
            triples.append(f"rdfs:subClassOf {p}:{ident[row['subclass_of']]}" if "subclass_of" in row
                           else f"rdfs:subClassOf {p}:Model")
            triples.append(f"a {p}:ModelClass")
        else:
            cls = _camel(row["category"]) if kind == "object" else KIND_CLASS[kind]
            triples.append(f"a owl:NamedIndividual, {p}:{cls}")
        triples.append(f"rdfs:label {_lit(row.get('label', row['name']))}")
        triples.append(f"skos:notation {_lit(row['name'], False)}")
        text = row.get("definition") or row.get("statement")
        if text:
            triples.append(f"skos:definition {_lit(text.strip())}")
        if "note" in row:
            triples.append(f"skos:note {_lit(row['note'])}")
        simple = {"symbol": "symbol", "formula": "formula", "holds": "holdsWhen", "check": "check", "tier": "tier",
                  "status": "status", "category": "category", "short": "shortName", "where": "where",
                  "schema": "schemaDocument", "domain_note": "note", "bellman_concept": "bellmanConcept",
                  "state_domain": "stateDomain"}
        for key, prop in simple.items():
            if key in row:
                triples.append(f"{p}:{prop} {_lit(row[key], False)}")
        if "ruled" in row:
            triples.append(f'{p}:ruled "{row["ruled"]}"^^xsd:date')
        if kind == "result":
            triples.append(f"{p}:resultKind {_lit(row['kind'], False)}")
        if kind == "identity":
            triples.append(f"{p}:identityKind {_lit(row['kind'], False)}")
        if kind == "divergence":
            triples.append(f"{p}:divergenceKind {_lit(row['kind'], False)}")
        refs = {"benchmark_of": "benchmarkOf", "of": "axiomOf" if kind == "axiom" else "momentOf",
                "factor": "hasFactor", "within": "within", "limit_in": "limitIn", "term": "concerns", "domain": "domain",
                "perch": "atPerch", "of_state": "functionOf"}
        for key, prop in refs.items():
            if key in row:
                triples.append(f"{p}:{prop} {p}:{ident[row[key]]}")
        for a in row.get("axioms", []):
            triples.append(f"{p}:hasAxiom {p}:{ident[a]}")
        for c in row.get("writes", []):
            triples.append(f"{p}:writes {p}:{ident[c]}")
        if "reduces_to" in row:
            triples.append(f"{p}:reducesTo {p}:{ident[row['reduces_to']['class']]}")
            triples.append(f"{p}:reductionWhen {_lit(row['reduces_to']['when'], False)}")
        for key, yes, no in (("assumes", "assumes", "assumesFailureOf"), ("concludes", "concludes", "concludesFailureOf")):
            for literal in row.get(key, []):
                prop = no if literal.startswith("not ") else yes
                triples.append(f"{p}:{prop} {p}:{ident[literal.removeprefix('not ')]}")
        text = row.get("formula") or row.get("holds") or row.get("check")
        if text:
            for s in sorted(formulas.names(text)):
                if s in syms and syms[s] != row["name"]:
                    triples.append(f"{p}:dependsOn {p}:{ident[syms[s]]}")
        for pd_id in row.get("law", {}).get("pd", []):
            triples.append(f"{p}:lawIn pd:{pd_id}")
        for pd_id in row.get("law_property", {}).get("pd", []):
            triples.append(f"{p}:lawProperty pd:{pd_id}")
        for fmt, spelling in row.get("written_as", {}).items():
            triples.append(f"{p}:{FORMAT_PROPERTY[fmt]} {_lit(spelling, False)}")
        for url in source_urls(source, row.get("sources", {})):
            triples.append(f"dcterms:source <{url}>")
        lines.append(me)
        lines += [f"    {t} ;" for t in triples[:-1]] + [f"    {triples[-1]} .", ""]
    return "\n".join(lines)


def build(path: Path = SOURCE) -> tuple[str, str]:
    source, digest = load(path)
    check(source)
    return turtle(source, digest), json.dumps(table(source, digest), ensure_ascii=False, indent=1) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if a generated file is out of date")
    args = parser.parse_args(argv)
    try:
        ttl, js = build()
    except SourceError as e:
        print(f"source.yaml: {e}", file=sys.stderr)
        return 2
    if args.check:
        stale = [f.name for f, text in ((TURTLE, ttl), (TABLE, js))
                 if not f.exists() or f.read_text(encoding="utf-8") != text]
        if stale:
            print(f"out of date: {', '.join(stale)}; run generate.py", file=sys.stderr)
            return 1
        return 0
    TURTLE.write_text(ttl, encoding="utf-8")
    TABLE.write_text(js, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
