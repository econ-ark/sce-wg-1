# Experiments: what every toolkit is asked to do

What an experiment is and what its file holds. [`experiment.schema.json`](../core/wg1core/schemas/experiment.schema.json), in the core's package, is the file's
validator; the harness's runner reads the file and its comparator evaluates the checks. The first experiment, the
restrained-limit experiment, is in the buffer-stock model's repository with its tests.

A family's schemas say what a model is. An **experiment** says what every toolkit is to do with some of a family's
members, and what the results must show. An experiment file names:
- the members, with the request file each is solved with;
- the precision levels every toolkit runs;
- what every results file must carry;
- the checks the harness makes on the results files.

It names no toolkit and holds none of a toolkit's settings. Those stay in the toolkit's method and settings files,
and its Rosetta Stone says how it maps onto the family. An experiment is to the
toolkits what CMIP's experiment protocols and data request are to climate models: one statement of what everyone runs
and reports, so that the results can be laid side by side.

- [`experiment.schema.json`](../core/wg1core/schemas/experiment.schema.json) is its validator, part of the core's package ([`../core/`](../core/README.md)).
- The buffer-stock model's repository holds the first experiment, and the tests of the validator and the file.

## What the harness gives a toolkit, and what it asks of it

Three rules:
- **It gives parameters, never methods or settings.** An adapter receives the member's parameter file, the request
  file, the name of a precision level, and a folder to write into; nothing else. What a level means is the
  toolkit's own ladder's business; the harness only maps the names.
- **The stated model's laws are the parameter file's, and each toolkit represents them as it likes:** by discretizing, by a
  continuous representation, or otherwise. No experiment and no code the adapters share prescribes nodes, grids or a
  population method. What a toolkit chose is read from its method file, its stone and its reported effective member.
- **It asks every toolkit for,** through the family's results schema: the rule and its
  special points, the buffer-stock target among them; the stationary distributions of m, a and c under both measures,
  which carry the population's means of m, a and c, and marginal welfare, E[u′(c)]; the stationary distribution of
  permanent income, for its Lorenz curve, which is all that is asked of it; and, where an experiment asks for it, the
  joint distribution of (m, 𝐩, c, a) the economy generates.

## What an experiment file holds

| key | what it holds |
|---|---|
| `experiment` | the name and version, as a family's: `restrained-limit/1`. A change to what it asks makes a new version |
| `title`, `statement` | what it shows, in words |
| `sources` | where it comes from, by anchor, under each source's key; a source's anchors must be among its page's, in the file the model's registry file names for that key (BST's is `bst-anchors.txt` in the ontology) |
| `members` | for each member: its `id` (the parameter file's name), the parameter file and the request file, each with its hash as the checker takes it, and optionally its `reference`: the reference results file, that file's hash, its `kind`, what it was `produced_by` and `certified_by`, the record that produced it, and the reference's certified `errors` per quantity (below). Pinning the hashes means an edited member or reference makes the experiment fail its test, not silently change; a changed reference is a new experiment version. The hash identifies the reference's file, not a reproduction of it: a results file need not be byte-identical across machines, so a solution is compared with the reference by distance, never by hash |
| `levels` | the named precision levels every toolkit runs: `low`, `medium` and `high`, as a toolkit's ladder names its elements. A toolkit may run more |
| `reports` | the results-file quantities every run must carry beyond what the results schema requires of every file, as paths into it: `types[].rule.c`, `types[].kink` |
| `metrics` | optional: the metrics the experiment defines, by name (below) |
| `checks` | what the results must show (below) |
| `reference_quantities` | optional: the quantities every job is compared with its member's reference on, each with its metric, and its `floor` under the metric relative to the reference; the `reports` under the absolute metric when left out |
| `report_scripts` | optional scripts of the experiment's own that write tables and figures from the results files alone, solving nothing |

The file is strict YAML, like a parameter file, so it has a hash, and its keys and values follow the schemas' own spelling,
with underscores. A quantity's path must resolve in the family's results schema; the experiment's checker verifies it.

## Kinds and roles

A solution has two properties, which the apparatus keeps apart.

**Its kind is how it is obtained.**
- **exact:** evaluated from a closed form. It has no settings, so each level names the same computation, and its only
  error is round-off. An exact entry is still registered with the levels' names and run at each, since a run is a
  job for every toolkit, member and level.
- **numerical:** approximated by a method with settings, at a level. Its error is not known beforehand and is what
  an experiment measures.

**Its role is what it is for in an experiment.**
- **the reference:** the standard a member's other solutions are measured against, pinned by the experiment with
  its stated errors.
- **an entry:** a registered toolkit's solution, measured against the reference.

Each combination occurs. An exact reference is a closed form that the model repository's checker evaluates. A
numerical reference is a solve carried far along its ladder and certified. A numerical entry is a toolkit's solver.
An exact entry is the closed form written in a toolkit's language: it shows that the language encodes the solution,
and it is no second method.

Where each is stated:
- **An entry's kind** is the registry file's: `kind: exact` or `kind: numerical` under the toolkit, numerical when
  left out. The run's manifest carries it, and so does every record the runner writes from then on; a job the runner
  skips, its fingerprint unchanged, keeps the record it had.
- **A reference's kind** is the experiment's, `kind` under the member's `reference`, with what produced it:
  `produced_by`, as words, such as the checker at a commit, or as a toolkit with its commit, its settings and the
  record of the solve; and `certified_by`, a list of the same, for an independent second solve. A producer names no
  entry of the registry file. The comparator says so when a producer is written as the name of one of a run's
  entries, or as a toolkit of that name, since an entry measured against its own solution shows nothing.
- **A reference's errors** are stated by quantity. A number is the error under the absolute metric. A mapping states
  the error under each metric it names, `{max_abs_difference: 1.0e-14, max_relative_to_reference: 1.0e-9}`, since a
  quantity near zero can have a small absolute error and a large relative one. An error relative to the reference is
  stated for the floor the experiment uses.

## Metrics

A metric is the distance between two files' numbers for one quantity. Every check and every reference quantity names
the metric it uses. No metric is the default, and which metrics an experiment uses is its own to say.

**The core has three, by name,** each a distance at every number with the largest taken:
- `max_abs_difference`: the absolute difference;
- `max_relative_difference`: the absolute difference divided by the larger of one and the first value's magnitude,
  which for a quantity far below one is the absolute difference;
- `max_relative_to_reference`, against a reference: the absolute difference divided by the reference's own magnitude
  at that number, or by the check's `floor` where the reference is smaller.

**An experiment defines others under `metrics`,** each by a name. Its checks, its reference quantities and its
references' errors then use that name as they use the three, whose names are reserved. A definition is one of two
things.
- **A pointwise distance with an aggregate.** `pointwise` is `abs_difference`, `relative_difference`, or
  `relative_to_reference` with its `floor`, which only a comparison with the reference can use. `aggregate` is `max`,
  `mean`, `rms`, the root of the mean of the squares, or `quantile` with its fraction `q`: the smallest pointwise
  distance with at least the fraction `q` of them at or below it, taken with no interpolation, so that two programs
  cannot differ on it. The core's three are the three pointwise distances with `max`.
- **A function of the model's repository:** `function: file.py:name`, the file by its path from the experiment
  file, with the file's `sha256` and, optionally, `parameters`. The function is called with the two files' numbers
  as two lists, an entry's first and the reference's or the other file's second, and the parameters by name. It
  returns the distance, a number not below zero, or the distance and the index among the numbers where its largest
  pointwise distance sits. It must give the same answer each time. The comparator imports the file and runs the
  function in its own process: it is the model repository's code run by the core, as the model's adapters and
  verifier are. It runs where the comparison does, in the environment of the model repository's harness, so it may
  import the standard library, what the core depends on, numpy and scipy among it, and whatever else that
  environment declares. The hash is pinned as a member's files are, so a changed function is a changed experiment;
  the experiment's checker reads the file and runs nothing.

```yaml
metrics:
  mean_abs_difference: {pointwise: abs_difference, aggregate: mean}
  rms_relative_to_reference: {pointwise: relative_to_reference, floor: 1.0e-12, aggregate: rms}
  weighted_abs_difference: {function: "metrics.py:weighted_abs_difference", sha256: "…", parameters: {power: 2}}
```

Three rules hold for every metric:
- **`at`.** With every distance the comparator reports where the largest pointwise distance sits, as the index among
  the quantity's numbers. For a largest that is where the distance itself sits; for a mean it is the worst point. A
  function that returns no index reports none.
- **A reference's error under a metric** is stated under the metric's name. A metric that an exact entry is held to,
  or that a fall against the reference rests on, needs the error stated under that same name.
- **A value that is not a number** is refused by every metric an experiment defines. The core's three refuse one in
  a check against the reference and otherwise pass over one that is not the first, as they always have.

The comparator's report states each defined metric, a function's with its file's hash, so that a reader sees what a
distance means.

## The checks

Each check compares results files and says what the comparison must show. It has an `id`, a `statement` in words, and:
- **`compare`,** what is set side by side:
  - `members`: one toolkit's files at one level, between the named `pairs` of members, for every entry;
  - `toolkits`: two numerical entries' files for one member at one level, for every pair of them run;
  - `levels`: one numerical entry's files for one member, at successive levels;
  - `reference`: for each entry of the check's `kind`, its files for one member beside the member's pinned
    reference. The check names the `kind` of entry it applies to, and applies to every member that pins a reference
    unless it names its `members`;
  - `stated`: one toolkit's files for one member at successive levels, against the checker's report of the stated
    member: the quantity's distance from its closed form, such as the effective member's expectations from the laws'.
- **`quantity`,** a path into the results file. Every number it holds is compared: a rule's values at the request's
  points, or the whole `effective_member` block.
- **`metric`,** by name: one of the core's three, or one the experiment defines (above). The check's `floor` goes
  with `max_relative_to_reference` alone, so that a reference value of zero is not divided by; a defined metric
  states its own.
- **`levels`,** optional: the levels the check applies to, in the order its expectation reads them; every level, as
  the experiment lists them, when left out.
- **`expect`:**
  - `decreasing`: each pair's metric smaller than the pair before it, at every level (for `members`);
  - `falls_with_level`: the metric smaller at each finer level (for `toolkits`, `levels`, and a numerical entry
    against the `reference`). Between toolkits and between levels the fall is strict. Against a reference, a level
    whose distance is no larger than the reference's stated error under the check's metric is as close as the
    reference resolves, and the step to it counts as a fall;
  - `{at_most: x}`: the metric no larger than x, at every level;
  - `within_reference_error`: every distance, at every level, no larger than the reference's stated error under the
    check's metric (for an exact entry against the `reference`). The reference must state that error, or the
    experiment's checker refuses the check. This is a test that the entry encodes the solution, not a measurement of
    a method. A value that is not a number, in the entry's file or the reference's, makes a check against the
    reference an error;
  - `within_own_convergence`: at the finest level, the metric no larger than the sum of the two toolkits' own movements
    of the same quantity between their two finest levels (for `toolkits`).

**How the comparator reports.** It evaluates the checks as written and gives each a verdict: pass, fail, not applicable
when the run holds too little to apply it, such as one level for a check on successive levels, or error when two
files cannot be compared. An exact entry has no method to compare and no ladder to converge along, so the checks
between toolkits and between levels leave it out; what holds it is a check against the reference. For every job
whose member has a reference pinned, it also reports the distance from the reference on each named quantity, with
where among the quantity's numbers the largest distance sits and the reference's own error beside it, and no
verdict: a distance in that table is reported, never judged, and no experiment is required to hold an entry to the
reference. A check with `compare: reference` is how an experiment does. Its report states each member's reference,
with its kind, what produced it and its errors, and each entry's kind. It writes `comparison.json` and
`comparison.md` in the run folder, a report in each job's folder, and the comparison block of each job's record. A comparison that cannot be computed for a member
that pins a reference, the reference not loading, not agreeing with the job's file on the identity keys the model
names, or a quantity not comparable, is an error. Its exit status is the checks' and the errors', never a reported
distance's. A numerical reference's solver is named for its code and run far along its ladder, with records of its
own, and an exact reference is named for what evaluates the closed form; the experiment pins the file either
produced.

**How two toolkits are compared.** A comparison of two toolkits takes its tolerance from measured convergence. Since
each toolkit represents the laws its own way, the two solve
different effective members, each an approximation of the stated one, and their rules differ by about their
representation errors; so the first experiment asks three things:
- **Each approaches the stated member.** The distance between a toolkit's effective member, the expectations it
  reports, and the checker's closed forms for the stated laws falls at each finer level (`compare: stated`).
- **Each converges, and the two agree within their own convergence.** At the finest level the two rules differ by no
  more than the sum of each toolkit's own movement between its two finest levels (`within_own_convergence`): a toolkit
  converged to 10⁻⁵ and one to 10⁻³ must agree to about 10⁻³, and a toolkit that converges to the wrong rule is
  caught by the next check.
- **Each solves the stated model.** The Euler residuals under the stated laws, which the results schema requires,
  fall with the level. That trusts no toolkit's representation.

The first version of the first experiment compared two adapters that shared their nodes and grids through common
code, so that its check of a shared effective member tested the code rather than the toolkits; the sharing was undone
and the check with it. A tolerance from a ladder of method-only settings at fixed nodes would be a sharper test of a
single toolkit, and is deferred.

## The first experiment: restrained-limit

The restrained-limit experiment, in the buffer-stock model's repository, states BST's "The Liquidity Constrained
Solution as a Limit". It has four members and request files, BST's calibration with ℒ = 1, and the levels `low`,
`medium` and `high`, each toolkit's own. It asks for:
- the rule and its MPCs, the kink and the target;
- the stationary populations: the mean MPC and the mass at the constraint.

It asks for no distribution of permanent income and no joint: its members have no mortality, so the first is
`undefined` for them, and the second would add nothing to the populations' ordinates.

It makes three checks:
- `rungs_approach_the_limit`: each natural rule is closer to the restrained one than the rung before, at every level;
- `approaches_stated_member`: each toolkit's effective member approaches the stated one with the level;
- `toolkits_agree`: the rules agree within the toolkits' own convergence.

Its first version, with the check `same_effective_member`, was evaluated on the results of HARK's and dolo's runs by
a prototype of the comparator, and all three of its checks passed:

| check | HARK | dolo | HARK against dolo |
|---|---|---|---|
| `rungs_approach_the_limit`, `high` | 0.137, 0.061, 0.0267 | 0.137, 0.061, 0.0267 | |
| `same_effective_member`, largest at any level | | | 3.3 · 10⁻¹⁶ |
| `toolkits_agree`, `bst-restrained` | | | 4.4 · 10⁻⁴, 1.4 · 10⁻⁴, 3.7 · 10⁻⁵ |

## What the experiment's checker establishes

The checker of experiment files, part of the harness's core, checks that:
- the validator is a valid JSON Schema;
- the experiment file is strict YAML and validates;
- the members' and request files exist and hash as the file says, and each request file is for its member;
- the checks name declared members, and every quantity resolves in the family's results schema;
- the report scripts exist, and each source's anchors are its page's, for a source whose anchors the model names;
- the members of a member-against-member check ask for the same points;
- a check names levels the experiment has, and a check against the reference names members that pin one, each
  stating the error an exact entry is to be held to;
- every metric named is the core's or one the experiment defines, and a metric's function is in its file, the file
  hashing as stated;
- breaks are caught, from a wrong hash to a toolkit's setting written into the file.

It solves nothing and says nothing about whether a toolkit passes. That is the harness's job.

## Open points

- A **ladder of method-only settings** at fixed nodes, to give a comparison of toolkits a measured tolerance: deferred.
- **A region** for a check, such as m ≤ 20, where the rule is far from the grid's top. Not needed by the first
  experiment, which passes over all its points.
- **Checks on the levels' own convergence,** `compare: levels`, which the first experiment does not use.
- The **iMPC** in the results schema, when an experiment needs it.
