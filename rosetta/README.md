# Rosetta Stones

What a Rosetta Stone is and what it holds. The stones themselves live with each canonical model's repository, beside
the adapters they describe; the first are the buffer-stock model's, for HARK, dolo and QuantEcon's endogenous-grid
operator.

A Rosetta Stone says how one toolkit solves a family's members as the family's stage file states them. With a stone for
each toolkit, one stage file and one parameter file can be solved by every toolkit that has one. Each toolkit writes a
results file, the checker verifies each file, and the files are compared.

A stone is written for a competent reader: an AI session or a person who reads the toolkit's documentation and code,
knows the mathematical structure of the problem, and is given the [parameters](https://bellman.io/wiki/parameters/) and the
[settings](https://bellman.io/wiki/settings/). It states what the
toolkit is expected to perform, and it records what a reader did to make the toolkit perform it. It does not prescribe
how the toolkit is to be called: that is the reader's to work out from the toolkit, and to record.

## The hub and the spokes

The hub is the family's statement: its stage file, one for each scenario, read in the family's model document, and its
parameter files. Each toolkit is a spoke, mapped to the hub alone. No stone translates one toolkit into another: two
toolkits meet only in their results files, which the family's results schema makes alike.

This is the design of Project Bellman's Rosetta stone. That registry records which operations and methods a toolkit's
routines carry out, and the conventions under which each correspondence holds (Bellman's documentation,
[*How Bellman-SYM works*](https://bellman.io/overview/01-concepts/#32-from-semantics-to-code), and its
[workflow](https://bellman.io/overview/06-workflow/)). A stone holds the toolkit's side only: the operator's side, the stage's own, is Bellman's to fill. It adds
what this project needs at the two ends, which Bellman's registry does not hold: the parameter file going in and the
results file coming out.

## What a stone holds

A stone has two parts, which answer two questions: what is expected of the toolkit, and what a reader did.

### The desiderata

What the reader may not decide for itself. Short, exact, and in one place each.

1. **The model, by reference.** The family's stage file and the member's parameter file. The stone restates neither.
2. **The method expected at each of the stage's places:** the endogenous grid method on the policy's block, an
   interpolation on the evaluation that closes it, a quadrature on an expectation, a histogram on the population's
   transition, and so on, under the family's rules of attachment. Each place takes one method. The methods are
   stated in two files, each part in exactly one of them.
   - *The methods addition* holds whatever Bellman's language can state. It is a methods file in Bellman's form
     (Bellman's documentation, [*Addition*](https://bellman.io/wiki/addition/) and
     [*Methodization*](https://bellman.io/Bellman-Sym/04-methodization/)): an addition to the family's stage file, kept beside
     the adapter, one for each family the toolkit solves. An entry names the place by its path in the stage and the
     method by Bellman's word for it, from Bellman's published
     [method types](https://bellman.io/Bellman-Sym/reference/methods/); once a reader has realized the method,
     the entry also names the [handler](https://bellman.io/wiki/handler/), as a package and a callable in it. A place whose method Bellman has no word
     for carries its handler alone. The addition is checked by
     [binding it](https://bellman.io/Bellman-Sym/04-methodization/#7-loading-and-binding) on the stage file under Bellman's package,
     which refuses a place the stage does not have and a word the place does not admit.
   - *The YAML method file* holds what an addition cannot: a part the stage has no place for, such as the stationary
     population, and a method that is neither a word nor a routine at a place. Every run writes it beside its
     results, with the addition the run used, and names that addition by the hash of its bytes, so that the one hash
     a record carries covers both.

   A toolkit that computes no value function enters nothing at the value's place, in either file: silence there
   means not computed, and the results file reports what needs the value, such as welfare, as not computed. The
   harness's own instruments, such as the expectation in the Euler residuals, are no toolkit's method and are in no
   method file; the results file names them.
3. **The settings at each named level**, in the toolkit's own names and with their values, in the stone's ladder file
   (the numerics document): the grids, the tolerances, the limits of iteration, the nodes. The toolkit's own defaults
   are an element of their own, read from the toolkit's documentation at the pin, with the citation. Settings are the
   one thing a reader must not infer. A setting that another toolkit's run produces says so where it is named, and the
   run's settings file records the value.
4. **The conventions that move a reported number** and that neither the math nor the toolkit decides: which
   side's slope is reported at a point that is a node of a grid; how far above a natural limit a grid may start; what
   a solve that stops at its cap is. A convention every toolkit meets is the family's results document's, and the
   stone points to it.
5. **What the results file says of the toolkit:** its name, its version and commit at the pin, and how it represents
   the laws. The results schema names these fields; the stone fills them.

### The realization

What a reader did, so that the next reader can check it.

6. **The adapter.** Code in two legs around the toolkit's call. *Encode* takes a parameter file and the settings to the
   toolkit's arguments. *Decode* takes the toolkit's output to a results file that reports the toolkit's effective
   member as the family's results schema asks. The adapter does not change the model: the laws, the transitions and
   the constraint are the member's, the grids and the nodes are settings, and any randomness has an explicit seed. The
   toolkit is imported at its pin and never copied and changed; what has to differ is done from outside it, and the
   record says what.
7. **The record.** What the reader read in the toolkit's documentation and source, and where; every choice the
   desiderata left to it, with its reason; every value it fixed, with its reason; every statement in the stone or the
   hub that it found wrong or stale. A value with no reason is a finding, not a default. What two readers decide
   differently is a desideratum that was missing, and goes into the stone.
8. **The evidence.** The toolkit's source read at a stated version; the checker's verification of the adapter's files;
   the comparator's distances from the reference; the ladder's convergence; agreement with another toolkit. Nothing
   counts as correct until a run is recorded.

### The document, and the cards

The document is for people: the lexicon, one row for each parameter of the stage file, each key of the parameter
file and each object the results file reports, with the toolkit's name for it, its timing and normalization, and,
where the toolkit differs, the difference and what the adapter does about it, citing the toolkit's documentation; and
the departures. It is written from the record, not before it, and it states no value that the desiderata state: it
points.

The cards, in the field names of Bellman's registry, are an export from the method and ladder files, made when that
registry takes cards. Nobody edits them by hand.

### What a stone does not hold

Whatever is the same for every toolkit. The adapter contract, the command line and the files between the harness and
an adapter, is the harness's. Where a model's adapters share code, what a toolkit's part hands it is that code's own
page to state; such code is a reference realization of the toolkit-neutral parts, the effective member, the
population, the residuals and the files, which a reader may use or replace under the same acceptance.

A stone records no run times or speeds: those belong to the run registry, with the machine and the conditions beside
them.

## How a stone is accepted

By its outcome, not by its form.

- A reader given the stone's folder and the hub, and nothing of an earlier adapter, produces a toolkit's part whose
  results verify with the checker and stand from the reference within the level's own error, with no quantity the
  experiment asks for missing.
- Its record names a source for every value that is not in the desiderata: the toolkit's documentation, a decision
  with its reason, or a convention of the hub.

This is run when a stone's desiderata change and when the toolkit's pin changes, not on every commit. The checks of
form, that the lexicon covers every parameter and key and that the cards keep their shape, run on every commit.

## The vocabulary

A **parameter** is the model's, stated in the parameter file; a **setting** is a method's, stated in the ladder file,
whatever the toolkit calls it; an **argument** is an input of a call. A **desideratum** states what is expected of
the toolkit; a **realization** is what a reader did to meet it; the **reader** is whoever builds or checks an adapter
from the stone.

## The workflow

    stage file + parameter file + method files + settings element + request file
      → each toolkit's adapter → one results file per toolkit
      → check.py --verify-results on each
      → the comparison of the files, at the request file's points

The harness runs the adapters and verifies the files; the comparison is the comparator's.

## Comparing two toolkits

These rules come from comparing successive versions of one emitter's results files number by number, and from the
reviews of this draft.
- **The effective members are compared first,** once the two files' parameter-file hashes are found equal. That means
  their expectations, their lowest values, the derived parameters and every condition's factor and verdict.
  - Two toolkits whose effective members fall on opposite sides of a condition report a difference of regime, not of
    values.
  - The gap between the two toolkits' expectations, such as E[ψ^(−ϱ)], is the first source of a gap in the rule, and
    is reported beside it.
- **The rule is compared at the request file's points,** which removes both grids. A distribution is compared only
  through statistics that both methods define alike.
- **A quantity that is not a property of the solution is not compared.** Q(1), the quantile at probability one, was one.
  On a grid it is the farthest point carrying any mass (there, weight 1.7·10⁻¹⁷⁰), and it moved from 61.56 to 4.40 on a
  change of 10⁻¹⁵ in a cumulative mass; the schema's quantiles stop at 0.999. An extreme, or anything that reads
  mass at or beyond a grid's top, needs the representation's coverage, which the results schema carries, or no
  comparison at all.
- **Each quantity has its own scale:**
  - relative, for levels: means, the rule at the points, MPCs;
  - absolute, or relative to the variable's mean, for ordinates near zero;
  - a bound, for residuals: each file's against its own bound, by size, never value for value. The stationarity residual
    is round-off; the Euler residual is the method's own error, from its grid and its nodes.
- **Tolerances come from measured convergence.**
  - Each toolkit's ladder of levels gives an error estimate e for each quantity.
  - Two toolkits agree when |A − B| ≤ k(e_A + e_B), with k about 2 or 3.
  - A simulating toolkit adds its sampling standard error, measured across independent panels.
  - Where the expectation is itself a Monte Carlo mean, its ladder varies the number of draws, the seed, the periods and
    the households as well as the grid. Otherwise the measured tolerance is too tight, and a difference of method looks
    like a difference of model.
- **The residuals say whether the same model was solved.** The Euler residual is taken against the stated member's laws,
  by a quadrature unlike either household's own: the harness's, one for every toolkit, which the results file names.
  The stationarity residual detects a distribution that is still moving. Both are diagnostics beside the measured
  tolerance, not the tolerance itself.
- **A difference of method is reported as one.** An example is the kink of a code that drops the pair at zero saving.
- **Within one toolkit, identity is attainable:** the same code, libraries and machine, with the same threads, give the
  same bits.
  - Across thread counts the last bits change. The linear algebra's dot product reorders its sums once a reduction
    passes about 50,000 elements, and weighted means moved by up to 9.3·10⁻¹⁶. So about 10⁻¹⁵ relative is the honest
    tolerance within one toolkit when the threads differ.
  - The numerical environment therefore belongs in the provenance: the threads of the linear algebra, and for JAX the
    floating-point precision.
- **A quantity present in one file only is reported, not failed,** since the results schema's optional fields may be
  absent.
- **Mass at an artificial constraint is a point mass.** A grid method needs a node there; a simulation counts the
  households with c = m.
