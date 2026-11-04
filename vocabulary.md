# Vocabulary

The words the working group's apparatus uses, each in the one sense it has here. The names the schemas coin are
registered in [the conventions](conventions.md).

## The definition

- **Family:** a versioned template of models with named parameters and one stage file, such as `bst-artificial/1`,
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
  expectation over one shock, named by the stage file's own name for it.
- **Method file:** the algorithm chosen for each part of the model, with no numerical values. **Settings file:** plain
  values for the settings those methods read. **Method registry:** the definitions of the methods, each with its
  contract and the settings it reads.
- **Handler:** the routine a method entry names, which carries out what the entry's method tag leaves open.
- **Ladder:** one method file run under many settings, so that results show how each quantity converges. **Level:** a
  named rung of a toolkit's ladder, the one input the harness passes that is not a parameter.
- **Experiment:** what every toolkit is to do with some members, and what the results must show, stated in an
  experiment file. **Reports:** the results-file quantities every run of an experiment must carry beyond what the
  schema requires. **Checks:** the experiment's comparisons across members, toolkits or levels of one quantity, each
  under a metric and an expectation.
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
- **Adapter:** the program, one per toolkit, that takes a parameter file, a request file, a level and a folder, and
  writes a results file with its method and settings files: the stone's mapping as code and the harness's plug-in for
  the toolkit. Its **encode** leg turns the member into the toolkit's arguments and its **decode** leg turns the
  toolkit's output into the results file. The adapter defines and pins the toolkit's **environment**, a lock file and
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
  no network, the thread cap, a scratch space, and the caps given; the adapter's command line inside it.
- **Toolkit registry:** the file naming each toolkit's adapter, stone, environment, levels and thread cap.
- **Runner:** the harness's program that expands an experiment into **jobs**, one per toolkit, member and level, runs
  them, verifies every results file, writes the **run folder** with its **manifest**, and registers the records.
  **Comparator:** the program that evaluates an experiment's checks and runs its report scripts.
- **Execution record:** what every build and every job writes: the repository's state, the environment's hash, the
  image, the machine, the conditions, the duration, how it ended and the outputs' hashes, with the model repository's
  own fields under its namespace. **Run registry:** a model repository's folder of registered records, one per job
  and per build of each run of record.
- **Reference solution,** or **the reference:** the organizer's solve of a member to very high precision by continuous
  methods, the standard every solution at default settings is compared to; its own error is reported beside every
  distance. **The continuous methods:** the expectation integrated against the shocks' continuous laws and split at
  the kink's preimage, the cubic Hermite interpolation that makes legal, the natural limit from the laws' infima, and
  the continuous landing of the transition's mass on the distribution grid.
- **The bench:** the organizer's own numerical code, which is no toolkit: the diagnostics' quadrature, the comparator,
  the reference solver.
- **Probe:** a measurement made for planning and recorded as a finding; not a run of record. **Run of record:** a run
  whose files are kept and cited as the measurement, made through the harness. **Finding:** the record of a
  measurement with its artifacts, what it establishes and what it does not.
- **Stub adapter:** the harness tests' stand-in toolkit, which copies committed files and solves nothing.
- **Organizer and participant:** the organizer runs the comparison and holds the reference; a participant is a
  toolkit's author who provides a card, an adapter or results files.
- **REMARK:** a repository that meets econ-ark's standard for a reproducible project: a tagged release, a Dockerfile,
  a reproduce script, an environment file, and at the higher tiers a citation file and an archived release. A
  canonical model's repository is one.
- **Records:** a project's own memory, its rulings, journal, findings and deferred follow-ups, kept with the model's
  repository and written for publication.
