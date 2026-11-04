# Rosetta Stones

What a Rosetta Stone is and what it holds. The stones themselves live with each canonical model's repository, beside
the adapters they describe; the first are the buffer-stock model's, for HARK, dolo and QuantEcon's JAX code.

A Rosetta Stone says how one toolkit solves a family's members as the family's stage file states them. With a stone for
each toolkit, one stage file and one parameter file can be solved by every toolkit that has one. Each toolkit writes a
results file, the checker verifies each file, and the files are compared.

## The hub and the spokes

The hub is the family's statement: its stage file, one for each scenario, read in the family's model document, and its
parameter files. Each toolkit is a spoke, mapped to the hub alone. No stone translates one toolkit into another: two
toolkits meet only in their results files, which the family's results schema makes alike.

This is the design of Project Bellman's Rosetta stone. That registry records which operations and methods a toolkit's
routines carry out, and the conventions under which each correspondence holds (Bellman's documentation, *Core
concepts*). A stone here uses that registry's field names, so that Bellman can take it in as cards. It holds the
toolkit's side only: the operator's side, the stage's own, is Bellman's to fill. It also adds what this project needs at
the two ends, which Bellman's registry does not hold: the parameter file going in and the results file coming out.

## What a stone holds

Each stone is a document, with its cards in a YAML file beside it.
1. **The lexicon.** One row for each parameter of the stage file, each key of the parameter file and each object the
   results file reports. Each row gives the toolkit's name for it and its timing and normalization. Where the toolkit
   differs, it states the difference and what the adapter does about it, citing the toolkit's own documentation.
2. **The handlers.** One for each of the toolkit's routines that the adapter calls. Each names the stage target it
   carries out, the family's method targets. It also says whether it does the whole stage or one
   part, whether the stage's transition is built into it, and whether it takes one step or iterates to convergence.
3. **The adapter.** Code in two legs around the handler's call.
   - *Encode* takes a parameter file and the settings to the toolkit's arguments.
   - *Decode* takes the toolkit's output to a results file that reports the toolkit's effective member
     as the family's results schema asks.

   The adapter does not change the model. The laws, the transitions and the constraint are the member's. The grids and
   the nodes are settings, and any randomness has an explicit seed.
4. **The methods.** For each target, the method, its settings and the handler. A whole-stage handler covers several
   parts, and for each of them the stone says whether it honors the method file's setting, fixes the part inside, or
   cannot take it, so that the adapter must. The cards write these with Bellman's tokens: `honours`, `fixed`,
   `requires_own_handler` and `absent`. A part the whole-stage handler runs names no handler of its own.
   - The targets are the stage's, under the family's rules of attachment:
     an expectation's method on its operator, `E_ψ_θ_j`; the solution on `policy.euler.solve`; the rule's interpolation
     on `policy`.
   - A method is written in words, with its tag beside it where it has one. An entry lists only the settings its tag
     names, unless it names a handler that reads the rest; the others are in the handler's map of settings.
5. **The evidence.** What has been checked and how:
   - the source, read at a stated version;
   - the checker's verification of the adapter's files;
   - agreement with another toolkit.

   Nothing counts as correct until a run is recorded.

A stone records no run times or speeds: those belong to the run registry, with the machine and the conditions beside
them.

## The workflow

    stage file + parameter file + method file + settings element + request file
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
  by a quadrature unlike either household's own (`diagnostics.expectation`). The stationarity residual detects a
  distribution that is still moving. Both are diagnostics beside the measured tolerance, not the tolerance itself.
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
