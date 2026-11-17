"""The reader of a canonical model's repository for the status table of REMARK's catalog
(../../schemas/execution-record.md, "The runs of record and the status table"): what the repository holds at the
commit read. Nothing is run.

REMARK's `remark status` pulls every entry of its catalog at its pin and asks a reader, chosen by the kind of unit
the repository declares in the front matter of its REMARK.md, what it finds there. A canonical model's repository
declares

    kind: canonical-model

and `read` is the reader REMARK finds for that kind, through the entry point this package offers in the group
`remark.status`. Nothing of REMARK's package is imported: the reader is a function of the checkout's folder.
`wg1core status` prints the same for the repository it is run in.

It reads the registry file, the experiments the registry file's folder of experiments holds, the records in the run
registry, and the file that names the runs of record, `runs-of-record.yaml` in the registry folder:

    runs_of_record:
      - experiment: restrained-limit/1              # the experiment's name
        toolkit: hark                               # as the registry file spells it
        mode: markov                                # only where the toolkit's records carry a mode of solution
        run: 2026-11-05T02-25_restrained-limit-1    # a folder of the run registry

A cell is an experiment, a toolkit and, where the records carry one, a mode of solution. The table has a row for
every cell: every toolkit of the registry file on every experiment the repository holds, and every cell the records
or the file name besides. A row with a run of record says what that run's records say: the repository's commit, the
toolkit's version, whether it ran in a container, the members and levels it covers, which draft of the registry
schema the records name and whether they are valid under it, the verification's verdicts, and the largest distance
from the reference at each level with the reference's error beside it. It notes a run from a tree with uncommitted
changes, a job that did not end cleanly, an experiment whose hash is no longer the run's, and a newer run of the same
cell in the registry. A row without one says so, and names the newest run the registry holds for the cell.

A record is checked against the draft of the schema it names: this core's own, or an earlier one the core holds. A
record that names a draft the core does not hold is reported as unchecked, never as invalid. An experiment's hash is
compared as this core computes it. Nothing here is a score, a rank or a duration: a distance is reported with the
reference's error beside it and carries no verdict.

Two things are kept apart. A problem is something wrong with what the repository states: the file of runs of record
malformed, or naming a folder, a toolkit or an experiment the repository does not hold, or a record of a run of
record that does not validate. A note is a fact a reader should weigh. `wg1core status` exits nonzero on a problem and
never on a note.
"""

from __future__ import annotations

import collections
import datetime
import json
import re
from pathlib import Path

import yaml

from . import canonical, records
from .runner import REGISTRY_FILES, Model

KIND = "canonical-model"
OF_RECORD = "runs-of-record.yaml"
NAMESPACE = "sce-wg-1"
ENTRY_KEYS = {"experiment", "toolkit", "mode", "run"}
EARLIEST = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)


# What the repository holds ---------------------------------------------------------------------------------------------

def registry_file(checkout: Path) -> Path:
    """A checkout's registry file, where the runner looks for it."""
    for candidate in REGISTRY_FILES:
        if (Path(checkout) / candidate).is_file():
            return Path(checkout) / candidate
    raise ValueError(f"no registry file: none of {', '.join(REGISTRY_FILES)} in the checkout")


def load_model(file: Path) -> Model:
    """The model repository as the runner reads it. The runner refuses a registry file by exiting, which is a
    command's way; a reader's caller reports an exception, so the refusal is raised as one."""
    try:
        return Model(Path(file))
    except SystemExit as e:
        raise ValueError(str(e)) from None


def experiments(model: Model, problems: list[str]) -> dict[str, dict]:
    """The experiments the repository holds, by name: the file, the hash as this core computes it, the levels in the
    experiment's order, and the members."""
    out = {}
    for path in sorted(model.experiments_dir.glob("**/experiment.yaml")):
        try:
            data = canonical.load_strict(path.read_text(encoding="utf-8"))
            out[data["experiment"]] = {"file": model.rel(path), "sha256": canonical.model_hash(data),
                                       "levels": list(data["levels"]), "members": [m["id"] for m in data["members"]]}
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as e:
            problems.append(f"{model.rel(path)}: not read as an experiment ({type(e).__name__}: {e})")
    return out


def registered(model: Model, problems: list[str]) -> dict[str, dict]:
    """The run registry: for each run's folder, its execution records by cell and its build records by toolkit. An
    execution record is placed by what it says, not by its file's name; a build record says nothing of its toolkit, so
    it is placed by the name `register` gave its file."""
    runs = {}
    if not model.registry_dir.is_dir():
        return runs
    for folder in sorted(p for p in model.registry_dir.iterdir() if p.is_dir()):
        cells, builds = collections.defaultdict(list), {}
        for path in sorted(folder.glob("*.json")):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                if record["kind"] == "build":
                    builds[path.name.removesuffix("_build.json")] = record
                else:
                    fields = record["extensions"][NAMESPACE]
                    cells[(fields["experiment"]["id"], fields["toolkit"], fields.get("mode"))].append(record)
            except (OSError, ValueError, KeyError, TypeError) as e:
                problems.append(f"{model.rel(path)}: not read as a record ({type(e).__name__}: {e})")
        runs[folder.name] = {"cells": dict(cells), "builds": builds}
    return runs


def runs_of_record(model: Model, problems: list[str]) -> tuple[Path, dict | None]:
    """The file of runs of record and what it names, the run's folder by cell; None when the repository has no such
    file. An entry that is not an experiment, a toolkit and a run, with a mode at most, is a problem and names
    nothing, as is a second entry for a cell."""
    path = model.registry_dir / OF_RECORD
    if not path.is_file():
        return path, None
    named: dict = {}
    try:
        data = canonical.load_strict(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as e:
        problems.append(f"{model.rel(path)}: not read ({type(e).__name__}: {e})")
        return path, named
    entries = data.get("runs_of_record") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        problems.append(f"{model.rel(path)}: no list under runs_of_record")
        return path, named
    for entry in entries:
        well_formed = (isinstance(entry, dict) and set(entry) <= ENTRY_KEYS and {"experiment", "toolkit", "run"} <= set(entry)
                       and all(isinstance(v, str) and v for v in entry.values()) and "/" not in entry["run"])
        if not well_formed:
            problems.append(f"{model.rel(path)}: an entry is not an experiment, a toolkit and a run's folder, each a "
                            f"string, with a mode at most: {json.dumps(entry, ensure_ascii=False, default=str)}")
            continue
        cell = (entry["experiment"], entry["toolkit"], entry.get("mode"))
        if cell in named:
            problems.append(f"{model.rel(path)}: more than one entry for {cell_name(cell)}")
            continue
        named[cell] = entry["run"]
    return path, named


# One cell --------------------------------------------------------------------------------------------------------------

def cell_name(cell: tuple) -> str:
    experiment, toolkit, mode = cell
    return f"{toolkit}{' in mode ' + mode if mode else ''} on {experiment}"


def started(cell_records: list[dict]) -> datetime.datetime | None:
    """When the earliest of some records' jobs started; None when no stamp reads as one."""
    stamps = []
    for record in cell_records:
        try:
            stamp = datetime.datetime.fromisoformat(record["when"]["started"])
            stamps.append(stamp if stamp.tzinfo else stamp.replace(tzinfo=datetime.timezone.utc))
        except (KeyError, TypeError, ValueError):
            pass
    return min(stamps) if stamps else None


def schema_draft(record: dict) -> str:
    """The draft of the schema a record names, as the last part of the identifier it carries."""
    name = record.get("$schema")
    return Path(name).name.removesuffix(".json") if isinstance(name, str) and name else "none named"


def checked(cell_records: list[dict]) -> dict:
    """Each record against the draft of the schema it names: valid or invalid where the core holds that draft, its
    own or an earlier one, and unchecked where it does not."""
    out = {"valid": 0, "invalid": 0, "unchecked": 0, "drafts": sorted({schema_draft(r) for r in cell_records}), "errors": []}
    drafts = records.held()
    for record in cell_records:
        if record.get("$schema") not in drafts:
            out["unchecked"] += 1
            continue
        try:
            records.validate(record, record["$schema"])
            out["valid"] += 1
        except ValueError as e:
            out["invalid"] += 1
            lines = str(e).splitlines()
            out["errors"].append(lines[min(1, len(lines) - 1)].strip())  # the validator's first line, after the heading
    return out


def in_order(levels, order: list[str]) -> list[str]:
    """Levels as the experiment lists them; one it does not list comes last."""
    return sorted(levels, key=lambda lv: (order.index(lv) if lv in order else len(order), lv))


def describe(cell_records: list[dict], build: dict | None, experiment: dict | None) -> dict:
    """What a run's records say of one cell."""
    fields = [r["extensions"][NAMESPACE] for r in cell_records]
    order = experiment["levels"] if experiment else []
    first = started(cell_records)
    members = sorted({f["member"]["id"] for f in fields})
    comparison = collections.Counter((f.get("comparison") or {}).get("status", "not recorded") for f in fields)
    reasons = sorted({f["comparison"]["reason"] for f in fields if (f.get("comparison") or {}).get("reason")})
    largest: dict = {}
    for f in fields:
        block = f.get("comparison") or {}
        if block.get("status") == "computed" and block.get("largest_distance"):
            best = largest.get(f["level"])
            if best is None or block["largest_distance"]["distance"] > best["distance"]:
                largest[f["level"]] = {**block["largest_distance"], "member": f["member"]["id"]}
    out = {
        "started": first.isoformat() if first else None,
        "commits": sorted({r["repository"]["commit"] for r in cell_records}),
        "uncommitted_changes": any(r["repository"].get("dirty") for r in cell_records),
        "toolkit_versions": sorted({f["toolkit_version"] for f in fields if f.get("toolkit_version")}),
        "core": sorted({" ".join(str(r["recorder"][k]) for k in ("name", "version", "commit") if r["recorder"].get(k))
                        for r in cell_records}),
        "runtimes": sorted({r["where"]["runtime"] for r in cell_records}),
        "members": members,
        "members_of_the_experiment": len(experiment["members"]) if experiment else None,
        "levels": in_order({f["level"] for f in fields}, order),
        "records": len(cell_records) + (1 if build else 0),
        "schema": checked(cell_records + ([build] if build else [])),
        "jobs_not_ended_cleanly": sum(1 for r in cell_records
                                      if r["outcome"].get("exit_code") != 0 or r["outcome"].get("termination") != "exited"),
        "verification": dict(collections.Counter(f["verification"]["verdict"] for f in fields)),
        "comparison": {"statuses": dict(comparison), "reasons": reasons,
                       "largest_distance_by_level": {lv: largest[lv] for lv in in_order(largest, order)}},
        "experiment_sha256": sorted({f["experiment"]["sha256"] for f in fields}),
    }
    return out


def read_cell(cell: tuple, named: dict | None, runs: dict, exps: dict, toolkits: list[str], problems: list[str]) -> dict:
    """One row: the cell, its run of record as the file names it, what that run's records say, and the notes."""
    experiment, toolkit, mode = cell
    held = {name: run["cells"][cell] for name, run in runs.items() if cell in run["cells"]}
    out = {"experiment": experiment, "toolkit": toolkit, "mode": mode, "run_of_record": (named or {}).get(cell),
           "runs_in_the_registry": sorted(held), "notes": []}
    newest = max(held, key=lambda name: (started(held[name]) or EARLIEST, name), default=None)
    if toolkit not in toolkits:
        out["notes"].append("the registry file has no such toolkit")
    if experiment not in exps:
        out["notes"].append("the repository holds no such experiment")
    run = out["run_of_record"]
    if run is None:
        out["notes"].append(f"no run of record; the registry's newest run is {newest}" if newest
                            else "no run of record, and no run in the registry")
        return out
    for what, missing in (("a toolkit the registry file does not have", toolkit not in toolkits),
                          ("an experiment the repository does not hold", experiment not in exps)):
        if missing:
            problems.append(f"the run of record for {cell_name(cell)} names {what}")
    if run not in runs:
        problems.append(f"the run of record for {cell_name(cell)} is {run}, a folder the registry does not hold")
        out["notes"].append("the registry holds no such folder")
        return out
    if run not in held:
        problems.append(f"the run of record for {cell_name(cell)} is {run}, which holds no record of it")
        out["notes"].append("the run holds no record of this toolkit on this experiment")
        return out
    try:
        out.update(describe(held[run], runs[run]["builds"].get(toolkit), exps.get(experiment)))
    except (KeyError, TypeError, AttributeError) as e:  # a record of a shape no draft this reader knows has
        problems.append(f"the records of {run} for {cell_name(cell)} could not be read ({type(e).__name__}: {e})")
        out["notes"].append("its records could not be read")
        return out
    if out["schema"]["invalid"]:
        problems.append(f"{out['schema']['invalid']} of the records of {run} for {cell_name(cell)} do not validate: "
                        + out["schema"]["errors"][0])
    if out["uncommitted_changes"]:
        out["notes"].append("run from a tree with uncommitted changes")
    if len(out["commits"]) > 1:
        out["notes"].append("its records name more than one commit")
    if out["jobs_not_ended_cleanly"]:
        out["notes"].append(f"{out['jobs_not_ended_cleanly']} of its jobs did not end cleanly")
    if experiment in exps:
        out["experiment_changed"] = out["experiment_sha256"] != [exps[experiment]["sha256"]]
        if out["experiment_changed"]:
            out["notes"].append("the experiment has changed since the run")
    mine = started(held[run])
    newer = sorted(name for name in held if name != run and mine and (started(held[name]) or mine) > mine)
    if newer:
        out["newer_runs"] = newer
        out["notes"].append(f"a newer run is in the registry: {newer[-1]}")
    return out


# The report ------------------------------------------------------------------------------------------------------------

def counted(n: int, noun: str) -> str:
    return f"{n} {noun}{'' if n == 1 else 's'}"


def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def records_text(cell: dict) -> str:
    """How many of a run's records for the cell are valid, invalid or unchecked, and the drafts they name."""
    s = cell["schema"]
    parts = [f"{n} {word}" for word, n in (("valid", s["valid"]), ("invalid", s["invalid"]), ("unchecked", s["unchecked"])) if n]
    return ", ".join(parts) + f" ({', '.join(s['drafts'])})"


def comparison_text(cell: dict) -> str:
    c = cell["comparison"]
    total, computed = sum(c["statuses"].values()), c["statuses"].get("computed", 0)
    parts = []
    if computed:
        distances = "; ".join(f"{level} {d['distance']:.3g} ("
                              + (f"{d['reference_error']:.3g}" if "reference_error" in d else "not stated") + ")"
                              for level, d in c["largest_distance_by_level"].items())
        parts.append((f"computed for {computed} of {total}: " if computed < total else "") + distances)
    for status in ("error", "not run", "not recorded"):
        if c["statuses"].get(status):
            reason = f": {c['reasons'][0]}" if status != "not recorded" and len(c["reasons"]) == 1 and not computed else ""
            parts.append(f"{status} for {c['statuses'][status]} of {total}{reason}")
    return "; ".join(parts)


def as_markdown(cells: list[dict], problems: list[str], of_record: str | None) -> str:
    """The unit's own table: a row for each cell, then the problems."""
    lines = ["| experiment | toolkit | mode | run of record | repository's commit | toolkit's version | ran in | members "
             "| levels | records | verification | largest distance from the reference at each level (the reference's error) "
             "| notes |", "|" + "---|" * 13]
    for c in cells:
        row = [c["experiment"], c["toolkit"], c["mode"] or "", c["run_of_record"] or ""]
        if "records" in c:
            of = c["members_of_the_experiment"]
            row += [", ".join(h[:10] for h in c["commits"]),
                    "; ".join(re.sub(r"\b([0-9a-f]{10})[0-9a-f]{30}\b", r"\1", v) for v in c["toolkit_versions"]),
                    ", ".join("the host" if r == "none" else f"a container ({r})" for r in c["runtimes"]),
                    f"{len(c['members'])} of {of}" if of else str(len(c["members"])), ", ".join(c["levels"]), records_text(c),
                    ", ".join(f"{n} {verdict}" for verdict, n in sorted(c["verification"].items())), comparison_text(c)]
        else:
            row += [""] * 8
        lines.append("| " + " | ".join(_cell(x) for x in row + ["; ".join(c["notes"])]) + " |")
    lines += ["", "A distance is reported with the reference's error beside it and carries no verdict; nothing here ranks "
                  "toolkits. A record that names a draft of the schema this reader's core does not hold is unchecked, not "
                  "invalid."]
    if of_record is None:
        lines += ["", f"The repository has no file of runs of record, `{OF_RECORD}` in its registry folder."]
    if problems:
        lines += ["", "Problems:", ""] + [f"- {p}" for p in problems]
    return "\n".join(lines) + "\n"


def summarize(cells: list[dict], toolkits: list[str], exps: dict, problems: list[str], has_file: bool) -> str:
    """One line for the catalog's row."""
    of_record = [c for c in cells if "records" in c]
    line = f"{counted(len(toolkits), 'toolkit')} on {counted(len(exps), 'experiment')}: "
    if not has_file:
        line += "no file of runs of record"
    else:
        verdicts = collections.Counter()
        for c in of_record:
            verdicts.update(c["verification"])
        line += f"runs of record for {len(of_record)} of {len(cells)}"
        if of_record:
            line += f"; {verdicts.get('verified', 0)} of their {counted(sum(verdicts.values()), 'job')} verified"
        noted = sum(1 for c in of_record if c["notes"])
        if noted:
            line += f"; notes on {noted}"
    if problems:
        line += f"; {counted(len(problems), 'problem')}"
    return line


def report(file: Path) -> dict:
    """Everything the reader finds in the repository a registry file describes: the one-line summary, the table, and
    the same as data."""
    model, problems = load_model(file), []
    exps, runs = experiments(model, problems), registered(model, problems)
    path, named = runs_of_record(model, problems)
    toolkits = list(model.toolkits)
    found = set(named or {}) | {cell for run in runs.values() for cell in run["cells"]}
    with_mode = {cell[:2] for cell in found if cell[2]}
    found |= {(e, t, None) for e in exps for t in toolkits if (e, t) not in with_mode}

    def order(cell: tuple) -> tuple:
        """The repository's experiments by name and its toolkits as the registry file lists them, then the rest."""
        experiment, toolkit, mode = cell
        return ((0, experiment) if experiment in exps else (1, experiment),
                (0, toolkits.index(toolkit), "") if toolkit in toolkits else (1, 0, toolkit), mode or "")

    cells = [read_cell(cell, named, runs, exps, toolkits, problems) for cell in sorted(found, key=order)]
    of_record = model.rel(path) if named is not None else None
    return {"summary": summarize(cells, toolkits, exps, problems, named is not None),
            "table": as_markdown(cells, problems, of_record),
            "data": {"registry_file": model.rel(model.file), "runs_of_record_file": of_record, "toolkits": toolkits,
                     "experiments": exps, "runs_in_the_registry": sorted(runs), "cells": cells, "problems": problems}}


def read(checkout, entry=None) -> dict:
    """REMARK's reader for the kind `canonical-model`: `checkout` is the folder the catalog's entry was pulled into
    at its pin; `entry`, the catalog's own record of it, is not used. Raises when the checkout has no registry file
    or the runner would refuse the one it has, which REMARK reports as a repository it could not read."""
    return report(registry_file(Path(checkout)))
