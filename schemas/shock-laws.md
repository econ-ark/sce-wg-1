# Shock laws

Draft. The laws of the shocks in a parameter file of the working group's schemas; the families that use them are in
each canonical model's repository, the first being the buffer-stock model's.

A **shock law** is the probability distribution of one shock in a parameter file. Every law here describes a positive
random variable ψ with mean one. The family decides which shocks exist and what they do; the parameter file chooses the
law of each.

The law belongs to the model. How a toolkit takes expectations under it (its quadrature) and how it draws from it are
the toolkit's choice.

Each law here is a chart of a subfamily of mean one in the [ontology of probability distributions](../ontologies/probability-distributions/),
version 0.1.0-draft.1, whose identifier is given with the law. The ontology defines each law as a measure, converts its
coordinates to its family's canonical chart and to Bellman-SYM's, and decides when two written laws are the same law.
The checker, the core's program that checks what a validator cannot express, reads every law through a copy of the
ontology's table and compares the ontology's formulas with its own closed forms.

## Rules for every law

- **One written form per law.** A parameter file's hash identifies its model, so two files describing the same model must
  produce the same hash. Each law can therefore be written in only one way, and several constraints below exist only to
  enforce that.
- **No silent normalization.** Where a law's mean is not one by construction, the checker verifies it and rejects a file
  that fails. It never rescales.
- **Defaults, and no bound.** A truncation bound left out is three standard deviations of the normal before truncation:
  −3 below, 3 above. No bound on a side is written `null`, as Distributions.jl writes `nothing` and PyMC and NumPyro
  `None`. A file holds no infinity, which JSON cannot write. The hash is taken over the filled form, with every omitted
  bound written in, so a law written with its defaults and the same law written without them are one model; a `null`
  stays `null`.
- **Who checks what.** The validator, [`shock-laws.schema.json`](shock-laws.schema.json), checks names, types and ranges.
  The checker checks the rest: orderings, sums, means, and the rules for tables.

In a parameter file a law is a mapping with one key, the law's name, whose value holds its parameters:

```yaml
permanent_shock: {TruncatedLogNormal: {sd_log: 0.0548, bot: -3.0, top: 3.0}}
```

## The laws

### Degenerate

ψ = 1. This is the only way to switch a shock off, which is why every other law requires a positive spread. Ontology:
`PD_0000025`, the point mass at one.

```yaml
{Degenerate: {}}
```

### LogNormal

ln ψ ~ N(−σ²/2, σ²), with `sd_log` σ > 0. The support is unbounded. Ontology: `PD_0000019`, the lognormal with mean
one.

```yaml
{LogNormal: {sd_log: 0.1}}
```

### TruncatedLogNormal

ln ψ = μ + sZ, where Z is a standard normal conditioned on `bot` ≤ Z ≤ `top`. The bounds are in standard deviations of
the normal before truncation, so ±3 means three of them either side. A bound left out is three; `null` is no bound on that
side, but not on both: a lognormal with no bound on either side is `LogNormal`. The checker requires `bot` < `top`.
Ontology: `PD_0000032`, the truncated lognormal with mean one.

`sd_log` is the standard deviation of ln ψ itself, after the truncation. An estimated standard deviation is therefore entered
as it is, and the truncated law keeps it. The scale s of the normal before truncation is larger:

    s = sd_log / √v,   v = Var(Z | bot ≤ Z ≤ top)
      = 1 + [bot φ(bot) − top φ(top)] / [Φ(top) − Φ(bot)] − ([φ(bot) − φ(top)] / [Φ(top) − Φ(bot)])²

Here φ and Φ are the standard normal density and CDF, and a term with an infinite bound is zero. For symmetric bounds,
1/√v is 1.136847 at ±2 and 1.013604 at ±3.

μ is set so that E[ψ] = 1 after truncation:

    μ = −ln E[exp(sZ) | bot ≤ Z ≤ top]

The moments have closed forms:

    E[ψ^k] = exp(kμ + k²s²/2) · [Φ(top − ks) − Φ(bot − ks)] / [Φ(top) − Φ(bot)]

```yaml
{TruncatedLogNormal: {sd_log: 0.0548, bot: -3.0, top: 3.0}}
{TruncatedLogNormal: {sd_log: 0.0548}}                        # the same law: each bound three
{TruncatedLogNormal: {sd_log: 0.0548, top: null}}            # truncated below only, at three
```

### Uniform

ψ ~ U[1 − w, 1 + w] in levels, with `half_width` w and 0 < w < 1. The mean is one by construction, and the lowest
value stays positive. Ontology: `PD_0000037`, the uniform with mean one.

```yaml
{Uniform: {half_width: 0.2}}
```

### Discrete

ψ takes the stated `values` with the stated `probs`. The points are the model, not a quadrature of some other law.
Ontology: `PD_0000045`, the finite discrete law with mean one.

- At least two values, positive and strictly increasing; one value would be `Degenerate`.
- One probability per value, each positive, summing to one.
- The checker requires Σ probs · values = 1.

```yaml
{Discrete: {values: [0.8, 1.2], probs: [0.5, 0.5]}}
```

### LogNormalMixture

ln ψ = c + X, where X is drawn from component j with probability `weight`_j, a normal with mean `mean_log`_j and standard
deviation `sd_log`_j. One common shift c makes E[ψ] = 1. Ontology: `PD_0000054`, the lognormal mixture with mean one.

- At least two components; one component would be a `LogNormal`.
- Weights positive, summing to one.
- The stated means are relative: the checker requires Σ weight_j · mean_log_j = 0, since adding the same amount to every
  mean would describe the same law.
- Components in increasing order of `mean_log`, ties broken by increasing `sd_log`.

```yaml
{LogNormalMixture: {components: [
    {weight: 0.1, mean_log: -0.9, sd_log: 0.30},
    {weight: 0.9, mean_log: 0.1, sd_log: 0.05}]}}
```

### TruncatedLogNormalMixture

As `LogNormalMixture`, but component j is a normal truncated at `bot`_j and `top`_j, in standard deviations of that
normal before truncation, with mean `mean_log`_j and standard deviation `sd_log`_j after truncation. Its scale is set
from `sd_log`_j exactly as for `TruncatedLogNormal`, and it is centered so that its mean after truncation is `mean_log`_j.
A bound left out is three; `null` is no bound. Ontology: `PD_0000058`, the truncated lognormal mixture with mean one.

- The rules of `LogNormalMixture`, with ties in `mean_log` and `sd_log` broken by increasing `bot`, then `top`.
- `bot`_j < `top`_j in every component.
- Some component has a bound: with none, the law is a `LogNormalMixture`. A component with `null` on both sides is a
  lognormal among truncated ones.

```yaml
{TruncatedLogNormalMixture: {components: [
    {weight: 0.1, mean_log: -0.9, sd_log: 0.30},                    # truncated at three either side
    {weight: 0.9, mean_log: 0.1, sd_log: 0.05, bot: null, top: 2.0}]}}
```

### Tabulated

A law of the user's own, given as its quantile function Q, the inverse of the CDF. The file lists `points` (u, Q(u)) for
u from 0 to 1, and Q is linear in u between consecutive points. The table *is* the law, not an approximation of one, so
every toolkit reconstructs exactly the same distribution. Ontology: `PD_0000063`, the quantile table with mean one.

A table describes continuous, discrete and mixed laws in the same way:

- a stretch where u and Q both rise has a flat density: across that stretch the law is a histogram;
- a stretch where u rises and Q stays flat is a point mass, whose size is the rise in u;
- a u value listed twice in a row, with Q higher the second time, is a jump in Q: a gap in the support.

Rules:

- The first u is 0 and the last is 1, and neither is repeated. u never falls, and any interior value appears at most
  twice, in consecutive points.
- Q never falls, and the first Q, the lowest value of ψ, is positive. The support is bounded, from the first Q to the
  last.
- At least one stretch where both u and Q rise. A table of steps alone is a `Discrete` law, and a single rising stretch
  is a `Uniform` law; both must be written as such.
- No interior point lies exactly on the line through its neighbors. Such a point adds nothing, and would give the same
  law a second written form. The checker tests this on the parsed numbers, in exact rational arithmetic.
- The mean, Σ (u₊ − u)(Q + Q₊)/2 over consecutive points, must equal one to within 10⁻¹².

Every expectation is E[f(ψ)] = ∫₀¹ f(Q(u)) du. On a rising stretch it is an integral of f over an interval of ψ, so the
moments and logarithmic moments that the regularity conditions need have closed forms. A draw is Q(U), with U uniform on
[0, 1].

A user with a continuous law of their own tabulates it at as many points as they like. The table they submit is the
model.

```yaml
{Tabulated: {points: [[0.0, 0.5], [0.1, 0.5], [0.5, 1.0], [1.0, 1.6]]}}   # a point mass of 0.1 at 0.5, then two rising stretches
```

## Bellman-SYM counterparts

The stage files are written in Bellman-SYM. The checker's converter writes each law as the Bellman-SYM call that states
it, by the ontology's conversions; the cross-test
confirms that each call carries the ontology's coordinates of the law. A member whose law differs from the one a stage
file writes needs a stage file of its own.

| law | in Bellman-SYM |
|---|---|
| Degenerate | `LogNormal(0, 0)`, a point mass at one |
| LogNormal | `LogNormal(−σ²/2, σ)` |
| TruncatedLogNormal | `TruncatedLogNormal(μ, s, l, u)`, with s = sd_log/√v, μ = −ln E[exp(sZ) \| bot ≤ Z ≤ top], l = exp(μ + s·bot) and u = exp(μ + s·top), and 0 and `inf` for no bound; the family is in preparation in Bellman-SYM, and a stage file can write it once it is released |
| Uniform | `Uniform(1 − w, 1 + w)` |
| Discrete | `Mixture((p₁, v₁), …)`, point masses with weights; Bellman-SYM checks no mean |
| LogNormalMixture | `Mixture((w₁, LogNormal(c + m₁, s₁)), …)`, the common shift folded into each location |
| TruncatedLogNormalMixture | `Mixture((w₁, TruncatedLogNormal(μ₁, s₁, l₁, u₁)), …)`, each component as for `TruncatedLogNormal` with the common shift folded in, and a component with no bound written `LogNormal` |
| Tabulated | none |

Bellman-SYM's `Mixture` has no common shift and its grammar writes no Φ, so the mixtures reach a stage file only as the
numbers the converter computes. A family for a mixture in logarithms with a common shift may come to Bellman-SYM later.

## Reserved for a later version

Two more ways to supply a law are anticipated. Their shapes are defined in the validator so that they are visible, but
no list of accepted laws refers to them, so a parameter file that uses either one fails validation.

### Formula

The law as a mathematical expression for its quantile function, density or CDF.

```yaml
{Formula: {defines: quantile, language: content-mathml, expression: "<math>...</math>", support: [0.5, 2.0]}}
```

Candidate choices:

- **Content MathML**, which is how SBML states all of its math, and the basis of SBML's Distributions package.
- **A small text grammar** with a reference parser in each supported language.

In both cases the checker would verify mean one, and the regularity conditions, by numerical integration. This route
allows unbounded support and analytic laws not in the list above. Its cost is that every toolkit needs a parser and an
evaluator.

### Code

The law as compiled functions behind a fixed interface, for example C functions `quantile(u)`, `cdf(x)`, `pdf(x)` and
`support()`.

```yaml
{Code: {interface: shock-law-c, form: c-source, path: laws/my_law.c,
        sha256: "0000000000000000000000000000000000000000000000000000000000000000"}}   # the file's SHA-256
```

Candidate choices:

- **Form:** C source, or WebAssembly, which runs the same on every platform.
- **Identity:** the file's SHA-256.
- **Precedent:** the Functional Mock-up Interface, the Modelica Association's standard for exchanging model functions
  between tools as compiled code with a standard C interface.

Open questions before adopting it:

- running other people's code;
- reproducing results across platforms;
- toolkits that cannot easily call C;
- the hash, which would identify the file rather than the law, so that two programs for the same law would differ.
