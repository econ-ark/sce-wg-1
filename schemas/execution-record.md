# Execution records

What every build of an environment and every run of a script writes, so that a result can be traced to the exact
state that produced it and reproduced from it. The format is [`execution-record.schema.json`](../core/wg1core/schemas/execution-record.schema.json), in the core's package,
the core every project shares, with a project's own fields under an `extensions` object keyed by namespace;
[`runs.registry.schema.json`](../core/wg1core/schemas/runs.registry.schema.json) is the pattern of a canonical model repository's entry, the
core with that repository's fields under its namespace. The core is drafted here for REMARK, the econ-ark standard for
reproducible projects, whose tool is to write records in this format for any cataloged repository.

## Two kinds of record

A **build** record is written once per environment built or created: the repository and commit, the environment's
specification and its hash, the image's name and identifier when the environment is an image, the machine, the
conditions, the start, end and duration of the build, and how it ended.

An **execution** record is written once per script run in one environment, and refers to its build by the image's
identifier when the run was in a container: the recorder that wrote it, the run it belongs to when a tool runs many
scripts at once, the repository and commit, the script and its arguments, the environment, the image, the machine, the
conditions, the start, end and duration, the outcome, and the extensions.

## What the fields mean

- **The repository's state.** The remote, normalized to the https form the catalog names; the commit; whether the
  working tree was dirty, which means that `git status --porcelain` printed anything, tracked changes or untracked
  files that are not ignored; and when it was, the tree of the working tree as it stood, written through a temporary
  index that both git commands read, so that the real index is neither read nor touched. A finding is not made from
  a dirty run, but the record says exactly what ran.
- **The environment's hash** is taken over what git records under the environment's directory in the tree that ran,
  the commit's tree when clean and the working tree's when dirty, listed with `git ls-tree`, never from the index or
  the files on disk, since the index can hold staged blobs and the bytes on disk can differ from a blob under
  line-ending conversion, filters or large-file storage. Each blob is hashed alone; then a sorted listing of type,
  mode, hash and path is hashed, so that two specifications compare file by file. It identifies the specification, not
  the result: builds are not bit-reproducible, and a REMARK's image depends on its whole checkout. The image's
  identifier is the image's identity.
- **The machine** is the host's facts alone: the processor, its logical cores, the memory, the operating system and
  kernel, and the container runtime, or none for a run on the host. **The conditions** are what the run was set and
  limited to: the thread variables actually set, whether a just-in-time compiler's cache was cold, so that the duration
  includes compilation, and the caps on processors, memory, wall time and network.
- **The stamps** are RFC 3339 with an offset, and the **duration** comes from a monotonic clock around the build or the
  script alone. A duration is read with the machine and the conditions beside it, never alone and never as a ranking.
- **How it ended** is kept apart from the exit code: an exit of its own, the wall cap, the memory cap, which the
  container runtime reports, or another signal, since an exit code of 137 alone cannot tell the last three apart.
- **The outputs** are the files the project names, each with its hash, so that a later run is compared file by file,
  relative to the output directory the record names.
- **Formats are patterns.** Timestamps and remotes are checked by regular expressions rather than format assertions,
  which a validator silently skips when it cannot check them. A record may name its own schema.

## A model repository's fields

Under the namespace `sce-wg-1`: the experiment and its hash, the toolkit and, when it has several ways of solving the
same member, the mode, the adapter's path and the hash of its code, the member with its canonical hash and its file's
hash, the request file's hash, the level, the settings', methods' and results files' hashes, the toolkit's version, the
verification's verdict with its problems, the comparison's verdict against the reference, and the version of the core
that gated the run. A run's records are registered in the model repository's registry, one file per job and one per
build, and one validation covers the folder, since the model's schema dispatches on the record's kind.
