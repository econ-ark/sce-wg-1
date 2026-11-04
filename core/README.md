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
what the core needs of the repository; every path is relative to the file.

```yaml
model:
  results_schema: ../schemas/bst/results.schema.json          # the family's results schema, which `reports` and checks resolve in
  anchors: ../ontologies/buffer-stock-models/bst-anchors.txt   # optional: the source page's anchors an experiment may cite
  experiments: ../schemas/bst/experiments                      # optional: where `list` looks for */experiment.yaml
  verifier: [uv, run, --project, ., --frozen, python, ../schemas/checker/check.py, "{member}", --verify-results, "{results}"]
                                                               # optional: the command that verifies one results file; its exit
                                                               # status is the verdict; without it the results schema's validation is
  registry_dir: runs.registry                                  # optional: where `register` writes; this is the default
toolkits:
  hark:
    adapter: adapters/hark/adapter.py          # the adapter contract: <adapter> <parameter file> --out <dir> --level <n> --request <file>
    code: [adapters/common.py, adapters/hark/adapter.py, ../schemas/checker/*.py]   # what a run's output depends on besides the environment
    environment: adapters/hark/env             # the adapter's own: pyproject.toml, uv.lock, .python-version, Dockerfile
    stone: ../rosetta/hark.md
    levels: {low: 1, medium: 2, high: 3}       # the adapter's --level for each named level
    threads: 2                                 # the cap on each job's BLAS and OpenMP threads
```

The repository's root is the git top level of the registry file's folder; the records are written against it.

## The commands

```sh
wg1core list
wg1core run <experiment.yaml> --toolkits hark,dolo [--levels low,medium] [--members <id>,...] [--jobs 8] \
    [--out <run folder>] [--runtime uv|docker] [--cpus 2] [--memory 8g] [--wall-seconds 3600]
wg1core verify <run folder>
wg1core register <run folder>
```

- **`run`** checks the experiment with the model's results schema and anchors and refuses one with problems, then runs
  one job for each toolkit, member and level, in parallel. With `--runtime uv`, the default, each job runs in the
  adapter's uv project on this machine; with `--runtime docker`, each toolkit's image is built first from the Dockerfile
  in its environment directory, its build record written, and each job runs under the container contract: the
  repository mounted read-only at `/src`, the job's folder at `/out`, no network, the thread cap, a scratch `/tmp` for
  what the toolkit caches, and the processor, memory and wall-time caps given. A job writes into
  `<run folder>/<toolkit>/<member>/level-<n>/`: the adapter's files, its log, `job.json` with the fingerprint of
  everything the output depends on, and `record.json`, its execution record. A job whose fingerprint is unchanged and
  whose results file exists is skipped. `manifest.json` names every hash.
- **`verify`** runs the model's verifier on every results file, or validates it against the results schema when the
  model names none, checks that each carries the experiment's `reports`, writes `verification.json`, and fills each
  record's verdict.
- **`register`** copies a run's records into the registry folder, `<registry_dir>/<stamp>_<experiment>/`, one file per
  job and one per build, validating each against `wg1core/schemas/runs.registry.schema.json`.

## The modules

| module | what it does |
|---|---|
| `runner` | the commands above |
| `records` | the records: the repository's state from git, the environment's hash over what git records, the machine, the stamps and durations, the validation |
| `canonical` | the strict YAML subset, the canonical serialization and the hash that identifies a model |
| `laws` | the shock laws a parameter file states, with their moments in closed form and their counterparts in the stage files' language |
| `experiment` | experiment files and what their validator cannot say |
| `schemas/` | `experiment.schema.json`, `execution-record.schema.json`, `runs.registry.schema.json` |

The tests, `tests/test_core.py`, build a tiny model repository of their own and run everything on it:

```sh
uv run --project core --with pytest pytest -q core/tests
```
