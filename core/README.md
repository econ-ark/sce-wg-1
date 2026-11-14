# The core

What every canonical model's repository shares, as a package it pins: the runner, the execution records, the
canonical serialization and hash, the shock laws and the experiment checker, with the validators of an experiment
file, of an execution record and of a registry entry as its data. The apparatus it belongs to is
[`../apparatus.md`](../apparatus.md); the documents of what it implements are [`../schemas/experiments.md`](../schemas/experiments.md),
[`../schemas/execution-record.md`](../schemas/execution-record.md) and [`../schemas/shock-laws.md`](../schemas/shock-laws.md).

The package is under the Apache License 2.0 (`LICENSE`), as HARK is.

## Pinning it

A model repository adds the package at a tag of this repository, with uv's subdirectory syntax:

```sh
uv add "wg1-core @ git+https://github.com/econ-ark/sce-wg-1@v0.1.0#subdirectory=core"
```

and runs it as `uv run wg1core ...`. The package's version is in `wg1core/__init__.py` and `pyproject.toml`; the
records name it and, when the package was installed from git, the commit it was installed from, read from the
installation's own metadata, since the version alone does not identify a development commit. The package needs
Python 3.11 or later, so that it can be installed in every adapter's environment, whose adapters read the model
through it.

## What a model repository gives it

A registry file, `harness/toolkits.yaml` by default, read by every command. It names the toolkits and, under `model`,
what the core needs of the repository; every path is relative to the file, except inside the verifier's command,
which runs from the repository's root and names its paths from there.

```yaml
model:
  results_schema: ../schemas/bst/results.schema.json          # the family's results schema, which `reports` and checks resolve in
  anchors: ../ontologies/buffer-stock-models/bst-anchors.txt   # optional: the source page's anchors an experiment may cite
  experiments: ../schemas/bst/experiments                      # optional: where `list` looks for */experiment.yaml
  verifier: [uv, run, --project, harness, --frozen, python, schemas/checker/check.py, "{member}", --verify-results, "{results}"]
                                                               # optional: the command that verifies one results file, run from the
                                                               # repository's root with its paths written from there, `{member}` and
                                                               # `{results}` replaced by absolute paths; its exit status is the
                                                               # verdict; without it the results schema's validation is
  registry_dir: runs.registry                                  # optional: where `register` writes; this is the default
  identity: [parameter_file_sha256, request_file_sha256]       # optional: results-file keys a job's file and its reference must agree on
toolkits:
  hark:
    adapter: adapters/hark/adapter.py          # the adapter contract: <adapter> <parameter file> --out <dir> --level <n> --request <file>
    code: [adapters/common.py, adapters/hark/adapter.py, ../schemas/checker/*.py]   # what a run's output depends on besides the environment
    environment: adapters/hark/env             # the adapter's own: pyproject.toml, uv.lock, .python-version, Dockerfile
    stone: ../rosetta/hark.md
    levels: {low: 1, medium: 2, high: 3}       # the adapter's --level for each named level
    threads: 2                                 # the cap on each job's BLAS and OpenMP threads
    kind: numerical                            # optional: exact for an entry that evaluates a closed form; numerical when left out
```

`anchors` names BST's anchors file, or a file for each key of an experiment's `sources`: `anchors: {bst:
../ontologies/buffer-stock-models/bst-anchors.txt, <key>: <file>}`. An experiment's anchors for a source are checked
against that source's file; a source with no file, or whose file is not there, is not checked.

An entry's kind says how it obtains its solution ([`../schemas/experiments.md`](../schemas/experiments.md), "Kinds and
roles"). The run's manifest and every record the runner writes carry it, and the comparator sets only numerical
entries beside one another and along their levels. An entry stated to be exact has its kind in its jobs' fingerprints, so stating
it reruns that entry; a numerical entry's fingerprint is what it was before entries had kinds.

The repository's root is the git top level of the registry file's folder; the records are written against it. Every
record names the repository by its remote, `origin` normalized to its https form, so a clone whose origin is a local
path is refused before anything runs, until its origin is set. Under GitHub Actions a record's `where.ci` names the
run: the provider, the run's identifier and the address of the attempt that ran, read from the service's own
variables, since the runner's host name is a throwaway.

## The commands

```sh
wg1core list
wg1core run <experiment.yaml> --toolkits hark,dolo [--levels low,medium] [--members <id>,...] [--jobs 8] \
    [--out <run folder>] [--runtime uv|docker] [--cpus 2] [--memory 8g] [--wall-seconds 3600]
wg1core verify <run folder>
wg1core compare <run folder>
wg1core register <run folder>
wg1core status
```

- **`run`** checks the experiment with the model's results schema and anchors and refuses one with problems, then runs
  one job for each toolkit, member and level, in parallel. With `--runtime uv`, the default, each job runs in the
  adapter's uv project on this machine; with `--runtime docker`, each toolkit's image is built first from the Dockerfile
  in its environment directory, its build record written, and each job runs under the container contract: the
  repository mounted read-only at `/src`, the job's folder at `/out`, no network, the thread cap, a scratch `/tmp` for
  what the toolkit caches, and the processor, memory and wall-time caps given. A job writes into
  `<run folder>/<toolkit>/<member>/<level>/`, the folder named for the level and never for its position: the adapter's files, its log, `job.json` with the fingerprint of
  everything the output depends on, and `record.json`, its execution record. A job whose fingerprint is unchanged and
  whose results file exists is skipped. `manifest.json` names every hash.
- **`verify`** runs the model's verifier on every results file, or validates it against the results schema when the
  model names none, checks that each carries the experiment's `reports`, writes `verification.json`, and fills each
  record's verdict.
- **`compare`** evaluates the experiment's checks on the run's results files, each with a verdict of pass, fail, not
  applicable or error, among them the checks that hold the entries of one kind to a member's reference; and it reports
  every job's distances from its member's reference on the experiment's quantities, with where the largest sits and
  the reference's own error beside each, and no verdict. An entry's kind is the run's own, read from its manifest. A
  metric is one of the core's three or one the experiment defines; a metric defined as a function of the model's
  repository is imported and run by this command. A comparison that cannot be computed for a member that
  pins a reference, the reference not loading, not agreeing with the job's file on the model's identity keys, or a
  quantity not comparable, is an error. It writes `comparison.json` and `comparison.md` in the run folder, a report in
  each job's folder, and each record's comparison block; its exit status is the checks' and the errors', never a
  distance's. The levels are ordered as the experiment lists them.
- **`register`** copies a run's records into the registry folder, `<registry_dir>/<stamp>_<experiment>/`, one file per
  job and one per build, validating each against `wg1core/schemas/runs.registry.schema.json`.
- **`status`** runs nothing. It prints what the repository holds: for each experiment and toolkit, the run of record
  the repository names and what that run's records say, as the next section describes. Its exit status is nonzero
  when the file of runs of record, or a record of a run it names, has a problem.

## The runs of record and the status table

A registry folder holds every run that was registered. Which of them is the measurement is the repository's to say,
in one file, `runs-of-record.yaml` in the registry folder:

```yaml
runs_of_record:
  - experiment: restrained-limit/1               # the experiment's name
    toolkit: hark                                # as the registry file spells it
    mode: markov                                 # only where the toolkit's records carry a mode of solution
    run: 2026-11-05T02-25_restrained-limit-1     # a folder of the registry
```

The file names the run and states nothing else, since everything else is in the run's records. A run of record is
made from a clean tree, since a finding is not made from a dirty run ([the records' document](../schemas/execution-record.md));
the reader notes one that was not.

`wg1core/status.py` reads the registry file, the experiments, the registry's records and that file, and reports one
row for every toolkit of the registry file on every experiment the repository holds. A row with a run of record
gives the repository's commit, the toolkit's version, whether the run was in a container, the members and levels it
covers, the draft of the registry schema its records name and whether they validate under it, the verification's
verdicts, and the largest distance from the reference at each level with the reference's error beside it. It notes
a run from a tree with uncommitted changes, a job that did not end cleanly, an experiment whose hash is no longer the
run's, and a newer run of the same toolkit on the same experiment. A row without one says so. A record is checked
against the draft of the schema it names: the core's own, or an earlier draft that a published core wrote, which the
core keeps in [`wg1core/schemas/earlier/`](wg1core/schemas/earlier/). A record written under a draft the core does
not hold is reported as unchecked, never as invalid. No row carries a score, a rank or a duration.

The same report is a canonical model's row in the status table of REMARK's catalog. `remark status` pulls each
cataloged repository at its tag and asks a reader, chosen by the kind of unit the repository declares, what it
holds. A canonical model's repository declares its kind in the front matter of its `REMARK.md`:

```yaml
kind: canonical-model
```

and this package offers the reader for that kind, `wg1core.status:read`, as an entry point in the group
`remark.status`, so that REMARK finds it wherever both packages are installed. The core imports nothing of REMARK's.

## The modules

| module | what it does |
|---|---|
| `runner` | the commands above |
| `records` | the records: the repository's state from git, the environment's hash over what git records, the machine, the stamps and durations, the validation |
| `canonical` | the strict YAML subset, the canonical serialization and the hash that identifies a model |
| `laws` | the shock laws a parameter file states, with their moments in closed form and their counterparts in the stage files' language |
| `experiment` | experiment files and what their validator cannot say |
| `metrics` | the distance between two files' numbers: the core's three metrics, and those an experiment defines |
| `comparator` | the experiment's checks evaluated on a run, and every job's distance from its member's reference |
| `status` | what a repository holds, its runs of record with what their records say; REMARK's reader for the kind `canonical-model` |
| `schemas/` | `experiment.schema.json`, `execution-record.schema.json`, `runs.registry.schema.json` |

The tests, `tests/test_core.py` and `tests/test_status.py`, build a tiny model repository of their own and run
everything on it:

```sh
uv run --project core --with pytest pytest -q core/tests
```
