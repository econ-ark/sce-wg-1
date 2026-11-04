# The apparatus

What the working group builds for the models it takes up, where each part lives, and how a toolkit takes part. The
words are fixed in [the vocabulary](vocabulary.md).

## The purpose it serves

For each model the group takes up, it fixes a canonical definition that is exact: every valid solution method, given
unbounded computation, converges to the same solution as every other. A toolkit is tested by whether it does. Its
solution of a member is verified against the definition and measured against a reference solution, and the test is a
reproduction that anyone can rerun. Two valid methods that converge to different solutions have located a convention
the definition left unstated, which is a finding of the kind the group exists to report; a method that departs from
the definition is located by its Rosetta Stone, which says how the toolkit reads the definition. The apparatus exists
to make that test cheap to run, hard to get wrong, and honest about what it establishes.

## The parts

- **A canonical model's repository.** One repository per model, holding the definition: the families' stage files,
  the parameter and results schemas, the members and their conditions, the syntax of the model class's ontology; the
  experiments; the reference solutions; the toolkits' stones and adapters; the runs of record and their registry. It
  is a REMARK, a reproducible project in econ-ark's sense: its reproduce script builds each toolkit's image, runs every
  experiment, verifies every results file, compares against the reference, registers the records, and exits nonzero on
  any failure. A tagged release with a DOI is a results of record. The first such repository is the buffer-stock
  model's.
- **The core, this repository's.** What every model shares: the vocabulary and the conventions; the semantic
  ontologies, of the model classes and of the probability distributions the laws are written on; the convention for a
  Rosetta Stone; the schemas of an experiment and of an execution record; the harness's generic parts, the runner that
  expands an experiment into jobs, runs each under the container contract, verifies the results and registers the
  records; and the rules of participation. A model's repository pins the core at a version.
- **The toolkits' images.** A toolkit's environment is defined and pinned by its adapter: a lock file and a Dockerfile
  beside it, built into an image identified by its digest. The image holds the toolkit and its dependencies and
  nothing of the model, which is mounted when a job runs.
- **The container contract.** One job: the repository mounted read-only, the job's folder writable, no network, the
  thread cap, a scratch space for what the toolkit caches, and caps on processors, memory and wall time. The adapter's
  command line takes the parameter file, the request file, the level and the output folder, and writes the results,
  method and settings files. Verification and the comparison run outside the toolkit's container, so that nothing the
  toolkit does changes the verdict.
- **The execution records and the registry.** Every image built and every job run writes a record: the repository's
  commit and whether its tree was dirty, the environment's hash over what git records, the image, the machine, the
  conditions, the start, end and duration, how the job ended, the outputs' hashes, and the model repository's own
  fields, the verification's verdict among them. A run's records are registered in the model's repository. A duration
  is read with its machine and conditions beside it, never alone and never as a ranking of toolkits.
- **REMARK's tool,** econ-ark/REMARK's: it pulls a cataloged repository at its tag, builds its image, executes its
  reproduce script and lints it against the standard. The working group's additions to it, in order: execution
  without a terminal, a package of its functions, the execution records, builds from a subdirectory, and an entry
  point with arguments.

## Where each part lives

| part | where |
|---|---|
| the purpose, the apparatus, the vocabulary, the conventions | this repository |
| the semantic ontologies | this repository, `ontologies/` |
| the stone convention, the experiment and record schemas, the harness's core, the rules of participation | this repository |
| a canonical model: its definition, experiments, references, stones, adapters, runs and records | the model's own repository, a REMARK; the first is the buffer-stock model's |
| the tool that pulls, builds, executes and lints a REMARK, and the catalog | econ-ark/REMARK |
| a toolkit's own code | the toolkit's repository, pinned by its adapter's lock file |

## How a toolkit takes part

1. **The card:** half a page, the first section of the toolkit's stone: the toolkit and its version, the families it
   solves, how it represents the laws, its method on each of the stage file's targets, its names, timing and
   normalization for the parameter file's keys and the results objects, and what it does not compute.
2. **The adapter:** the contract's command line in any language, reading the parameter and request files and writing
   the results, method and settings files, with its environment pinned beside it.
3. **The run:** the harness runs the adapter on every experiment at the toolkit's levels, verifies every results file
   with the checker, compares it with the reference, and registers the records.
4. **The stone:** the lexicon, the handlers, the departures and the evidence, revised on the verified runs.

A toolkit whose authors cannot provide an environment submits results files, which are verified and shown as
submitted rather than reproduced; only a reproduced run becomes a finding.

## What the comparison establishes

A toolkit that passes an experiment's checks is consistent with the definition and with the others, not proved right.
A discrepancy is shown with its reading, never scored, and the reference's own error is reported beside every
distance. Nothing ranks toolkits. What the comparison can establish is that the definition is complete, that a
departure traces to a stated setting of one toolkit, and, where neither holds, that a convention was left unstated.
