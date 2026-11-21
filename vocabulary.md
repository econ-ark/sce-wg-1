# Vocabulary

The words the working group's apparatus uses, each in the one sense it has here. The names the schemas coin are
registered in [the conventions](conventions.md).

## The definition

- **Family:** a versioned template of models with named parameters and one [stage file](https://bellman.io/wiki/stage/), such as `bst-artificial/1`,
  buffer-stock theory with an artificial borrowing constraint, version 1.
- **Member:** one complete parameterization of a family.
- **Stated member:** the member a parameter file names, with its laws as stated. What can be computed about it is in
  general a limit, approached numerically; for laws whose moments have closed forms, the checker computes it exactly.
- **Effective member:** the member a toolkit actually solves, with its own approximation of the laws in its own
  representation. The schemas know it through the expectations the family names, the conditions decided on it and the
  derived parameters it used, all reported in the results file.
- **Derived parameter:** a quantity the parameters determine that enters the model's statement, such as the natural
  borrowing limit; a toolkit uses its effective member's own and reports it.
- **Model-changing and method-only settings:** descriptions of a toolkit's settings, not requirements on them. The
  first alter its effective member, such as a shock's nodes or a truncation; the second alter only how the solution is
  approximated, such as a grid or a tolerance. The two converge in different things and are read separately.
- **Valid solution method:** a procedure that approximates a member's problem as stated and nothing else, every choice
  of its own refinable without bound. A toolkit at fixed settings is an approximation, not a method in this sense; its
  ladder, with its model-changing settings refined as well, is.
- **Exact definition:** a definition under which every valid solution method, given unbounded computation, converges
  to the same solution as every other. A disagreement between two toolkits in the limit is a gap in the definition or
  a departure in one toolkit, and the toolkit's stone, read against the definition, says which.
- **Canonical definition:** the exact definition the working group fixes for a model: the hub to which every stone
  maps its toolkit.
- **Model schema:** the document that states a family's mathematics.
- **Parameter file:** a member written down, in YAML, to the parameter schema. Its hash, taken over a canonical
  serialization, identifies the model.
- **Results file:** what a toolkit returns, in JSON, to the results schema.
- **Shock law:** the probability distribution of one shock in a parameter file, a point of a chart of the ontology of
  probability distributions.
- **Validator:** a JSON Schema file that checks a parameter or results file's form.
- **Checker:** a program that checks what a validator cannot express, such as a law's mean or a regularity condition.
- **Addressable part** and **method target:** a part of a family's model that a method can be attached to, such as the
  expectation over one shock. It is named by its **place** in the family's stage file, as Bellman names it
  ([methodization](https://bellman.io/wiki/methodization/)): a block by
  its identifier, the evaluation that closes a block, an operator by its name.
- **Method files:** the algorithm chosen for each part of the model, with no numerical values, in two files with each
  part in exactly one. The **methods addition** is a file in Bellman's language
  ([addition](https://bellman.io/wiki/addition/)), added to the family's stage file,
  whose entries name a method word or a handler at a place. The YAML **method file**, which every run writes, holds
  what an addition cannot, such as a part the stage has no place for, and names the addition with its hash.
  **Settings file:** plain values for the [settings](https://bellman.io/wiki/settings/) those methods read. **Method registry:** the definitions of the
  methods, each with its contract and the settings it reads; for a method word, Bellman's table of
  [method types](https://bellman.io/Bellman-Sym/reference/methods/).
- **Handler:** the routine a place's entry names ([Bellman's handler](https://bellman.io/wiki/handler/)), which carries out what the method word leaves open, or stands alone
  where Bellman has no word for the method.
- **Ladder:** the same methods run under many settings, so that results show how each quantity converges. **Level:** a
  rung of the ladder, named by the experiment. To an adapter on the contract's first form it is the one input the
  harness passes that is not a parameter, and the toolkit's ladder says what it means. To one on the second the harness
  passes the level's **suggestions** instead: settings in the model's own terms that the toolkit may take, adapt or
  decline, saying which in its settings file, judged only by the outcome; an exact entry, which has no settings,
  answers each **not applicable**. A level with no suggestions is the toolkit's own defaults.
- **Experiment:** what every toolkit is to do with some members, and what the results must show, stated in an
  experiment file. **Reports:** the results-file quantities every run of an experiment must carry beyond what the
  schema requires. **Checks:** the experiment's comparisons across members, toolkits or levels of one quantity, each
  under a metric and an expectation.
- **Metric:** the distance between two files' numbers for one quantity: a distance at each number with an aggregate
  over them, the largest, the mean, the root mean square or a quantile, or a function of the model's repository. A
  check names its metric, and none is the default.
- **Request file:** the comparison points at which a results file reports, kept apart from the parameter file so that
  the model's hash does not change. **Comparison points:** the values of the state at which the rule, its derivative,
  the Euler residuals and the distribution function are reported; the **request rule** generates them from a **quick
  solution** of the member and moves a point off a **genuine atom**, an atom of the stated member's distribution whose
  location the parameters fix.
- **Validity condition:** a condition on the parameters that a member must meet to be accepted at all. **Domain
  rule:** a condition that decides whether a member defines one reported quantity; a quantity it does not define is
  reported as undefined. **Implication:** an exact consequence of a member's parameters that tests a solution,
  computed for the stated member by the checker.
- **Observation map:** a stated transformation from the standard rule to what a household does, kept outside the
  household's problem. **Level law:** a law of a quantity in levels, as against a mean-one shock law. **Regime:** an
  aggregate Markov state of the household's chain. **The floor of a law:** how a law behaves at the lowest value of its
  support, which decides the lower tail of the stationary distribution.
- **Semantic ontology:** a model's meaning stated apart from any code: what exists, what stands for what, and what is
  written down, with when the reading holds. A family's schemas are the syntax of its model class's ontology. **Model
  class:** a class of models defined by membership axioms; a family writes members of one or more classes.

## The apparatus

- **Toolkit:** a solution library that a stone and an adapter serve.
- **Rosetta Stone,** or **stone:** the document, one per toolkit, that says how the toolkit solves a family's members
  as the stage file states them: its lexicon, its handlers, its adapter's two legs, its departures. Its **cards** are
  the lexicon's rows in a file beside it. The family's statement is the **hub** and each toolkit a **spoke** mapped to
  the hub alone; no stone translates one toolkit into another. Its first section is the **card** an author writes
  before any code.
- **Adapter:** the program, one per toolkit, started by its **command**, that takes a parameter file, a request file,
  a folder and a level or the level's suggestions, and writes a results file, on the **contract**'s first form, or the
  toolkit's solution, on its second, with its method and settings files: the stone's mapping as code and the harness's
  plug-in for the toolkit. Its **encode** leg turns the member into the toolkit's arguments and its **decode** leg
  turns the toolkit's output into the results file or the solution file. It supplies none of the toolkit's numerical
  choices. A **reading** is where it reads the toolkit's internals rather than the object the toolkit returns; the
  solution file declares each and the stone says why.
- **Solution file:** what an adapter on the contract's second form writes: the toolkit's rules as the toolkit holds
  them, in a form the bench can read exactly, the representation of the laws it solved on, what the toolkit computes
  for itself, and the toolkit's own evaluations at stated points, by which the bench checks its reading. Its schema is
  the model's. **Solve step and measure step:** the two parts of a job on the second form, the adapter's in the
  toolkit's environment and the bench's in the harness's, each with its own record. The adapter defines and pins the toolkit's **environment**, a lock file and
  a Dockerfile beside it, built into an **image**.
- **Mode of solution:** one of several ways a toolkit solves the same member, such as a solver that treats
  unemployment as an income shock and one that treats it as a Markov state; each mode is a spoke of its own.
- **Representation:** a toolkit's own approximation of the laws, as nodes or atoms, and of the stationary
  distribution, as a grid, a lottery, a sample or a density; what the effective member is solved on.
- **Scenario:** a family's borrowing-constraint case, each with its own stage file. **Types:** a member's
  discount-factor types, each with a population share; **pooled** blocks are the types pooled by share. **Population
  measure and income measure:** the stationary cross-section weighted by households, and weighted by permanent income.
- **Exported rule:** the rule at dense points of the toolkit's choosing, with the kink and the range. **Coverage:** the
  results-file block that says how far a representation of the distribution reaches and what became of the mass
  beyond it.
- **Container contract:** how one job runs in a toolkit's image: the repository read-only, the job's folder writable,
  no network, the thread cap, a scratch space, and the caps given; the adapter's command inside it.
- **Toolkit registry:** the file naming each toolkit's adapter, its command where that is not `python <adapter>`, its
  contract, stone, environment, levels and thread cap, and under `model` the model's bench.
- **Runner:** the harness's program that expands an experiment into **jobs**, one per toolkit, member and level, runs
  them, measures each solution of an adapter on the contract's second form with the model's bench, verifies every
  results file, writes the **run folder** with its **manifest**, and registers the records.
  **Comparator:** the program that evaluates an experiment's checks and runs its report scripts.
- **Execution record:** what every build and every job writes: the repository's state, the environment's hash, the
  image, the machine, the conditions, the duration, how it ended and the outputs' hashes, with the model repository's
  own fields under its namespace. **Run registry:** a model repository's folder of registered records, one per job,
  two for a job on the contract's second form (its solve and its measure), and one per build of each registered run, with the file that names, for each experiment, toolkit and mode, its run of
  record.
- **Reference solution,** or **the reference:** the organizer's solve of a member to very high precision by continuous
  methods, the standard every solution at default settings is compared to; its own error is reported beside every
  distance. Where the model has a closed form, the reference is the closed form, evaluated exactly. **The continuous
  methods:** the expectation integrated against the shocks' continuous laws and split at the kink's preimage, the
  cubic Hermite interpolation that makes legal, the natural limit from the laws' infima, and the continuous landing
  of the transition's mass on the distribution grid.
- **Kind of a solution:** how it is obtained: **exact,** evaluated from a closed form, with no settings and no error
  but round-off, or **numerical,** approximated by a method with settings at a level. **Role of a solution:** what it
  is for in an experiment: the **reference,** which a member pins with its stated errors, or an **entry,** a
  registered toolkit's solution measured against it. A reference may be of either kind, and so may an entry: an exact
  entry is the closed form written in a toolkit's language, and is no second method.
- **The bench:** the organizer's own numerical code, which is no toolkit: the model's bench, which measures every
  solution of an adapter on the contract's second form by one code, outside the toolkit's container (the effective
  member, the stationary population, the statistics, the residuals and the results file), with its settings named
  in the experiment; the diagnostics' quadrature; the comparator; the reference solver.
- **Probe:** a measurement made for planning and recorded as a finding; not a run of record. **Run of record:** a run
  whose files are kept and cited as the measurement, made through the harness. **Finding:** the record of a
  measurement with its artifacts, what it establishes and what it does not.
- **Stub adapter:** the harness tests' stand-in toolkit, which copies committed files and solves nothing.
- **Organizer and participant:** the organizer runs the comparison and holds the reference; a participant is a
  toolkit's author who provides a card, an adapter or results files.
- **REMARK:** a repository that meets econ-ark's standard for a reproducible project: a tagged release, a Dockerfile,
  a reproduce script, an environment file, and at the higher tiers a citation file and an archived release. A
  canonical model's repository is one. **Kind of unit:** what sort of unit a cataloged repository is, declared in its
  `REMARK.md`; a canonical model's is `canonical-model`. **Status table:** the catalog's table of what each
  repository holds at its tag, read and never run, each row by the reader for the repository's kind.
- **Records:** a project's own memory, its rulings, journal, findings and deferred follow-ups, kept with the model's
  repository and written for publication.
