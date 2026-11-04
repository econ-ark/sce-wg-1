# Probability distributions

An ontology of the probability distributions that the working group's schemas and toolkits write. Every law a parameter
file or a Bellman-SYM stage file states is a point of a chart of a family defined here. So two written laws can be
compared, a toolkit's laws can be checked against one standard, and the provenance of a spelling can be checked.

The ontology gives definitions, charts and conversion formulas. It provides no routines for sampling or evaluating a
distribution.

**Status: draft, version 0.1.0-draft.1.** The design below is settled, and [the catalog](#the-catalog) holds every
family the schemas' parameter files and Bellman-SYM's stage files write.

## The kinds

Everything in the ontology is one of six kinds.

- A **measure** is the object: a probability measure on a stated set. A few measures are named because families are built
  from them, such as the standard normal N(0, 1); each states its density and support, from which the tests integrate.
- A **family** is a named map from a parameter space into measures. A kernel, such as a Markov transition, is a family one
  of whose arguments is a state.
- A **chart** is a coordinate system on a family's parameters: the normal's mean and standard deviation, or its mean and
  variance. A chart changes no measure. Each family has one **canonical chart**, in which two laws are compared; every
  other chart carries formulas converting to the canonical chart and back.
- An **operator** maps measures to measures.
- A **property** maps a measure to a value: its support, mean, moments, the moments of its logarithm, its atoms.
- A **constraint** is a property set equal to, or bounded by, a value. A constraint on a family defines a **subfamily**,
  whose charts are the reduced parameterizations the constraint induces.

A written law, in either kind of file, is a point of one chart of one family.

## The operators

Three operators are primitive:

- the **pushforward** f∗μ under a measurable map f, the law of f(X) when X has law μ;
- **conditioning** μ|A on a set A of positive measure, the law of X given X ∈ A; truncation is conditioning on an interval;
- the **product with a kernel** μ ⊗ κ: draw X from μ, then Y from κ(X, ·).

The rest are cases of these. The affine map aff(a, b), z ↦ a + b·z, and the exponential map are pushforwards. A finite
mixture is the product of a law on labels with the kernel sending each label to its component, followed by the projection
onto the component's value. The product of independent laws is the product with a constant kernel. A Markov chain iterates
the product with its transition kernel. Censoring is the pushforward under a clamp. A named case enters the ontology when a
family is built from it; this release has the affine and the exponential maps.

Conditioning commutes with an injective pushforward, since f⁻¹(f(A)) = A. So a lognormal truncated to [l, u] is the
exponential of a normal truncated to [ln l, ln u], and bounds stated in standard deviations of the normal convert exactly
to bounds in the draw's own units.

## Identity

Two written laws are the same law when they agree after four steps. First, fill the written form's defaults. Second,
reduce the operator expression to its normal form, where a vacuous conditioning disappears: a family's `reductions`
record where a point of its canonical chart is a member of another family, as `TruncatedNormal(μ, σ, -inf, inf)` is the
normal `N(μ, σ)`; and a mixture's components are taken as a set, ordered and with equal components merged, since the
same components in another order, or one component split in two, write the same law. Third, convert to the family's
canonical chart. Last, compare the canonical coordinates. They must be equal when every conversion is exact.
Where a conversion is irrational, such as a square root or a conditional moment, they must agree to a relative tolerance
of 10⁻¹².

The schemas' parameter-file hash is not this comparison. The hash is taken over the filled written form, and it binds the
schema's version alone; no conversion formula enters it, so a revised formula here changes no hash.

## Settlements

Three questions are settled one way throughout:

- **A pinned mean is a constraint.** It defines a subfamily, and the reduced parameterization it induces is that
  subfamily's chart. The lognormal with mean one is written by σ alone, and its chart sends σ to (−σ²/2, σ) in the
  lognormal's canonical chart.
- **The relative means of a mixture restrict a chart's domain.** In the schemas' mixtures in logarithms, a shift of every
  component's mean is absorbed by the common shift, so the condition Σ wⱼ·meanⱼ = 0 makes each law's written form unique.
  It is no property of the law. (It arrives with the mixtures.)
- **The point mass is a family of its own.** The normal with zero variance, `N(μ, 0)`, the lognormal with zero spread,
  `LogNormal(μ, 0)`, and the parameter files' `{Degenerate: {}}` are charts of it, not members of the normal and lognormal
  families, whose canonical charts require a positive spread. Each family's `boundaries` record where its domain meets
  the point mass.

## Canonical charts

A family's canonical chart is the chart ProbOnto lists first for that family, where ProbOnto has the family. That is also
the chart of the family's constructor in Distributions.jl: the normal's mean and standard deviation, and the mean and
standard deviation of the lognormal's logarithm. For a family ProbOnto lacks, the canonical chart is the one the family's
sources share. The charts of the parameter files and of Bellman-SYM get no special status: they are charts like the
others, each with its conversions. Bellman-SYM's `N(μ, v)`, for instance, takes the variance, and is the normal's
mean-and-variance chart.

## Written forms and defaults

Two formats are declared: `parameter-file`, the YAML parameter files of the working group's schemas, and `bellman-sym`,
Bellman-SYM stage files. A chart's `written_as` gives each format's spellings of a point of the chart, more than one where
a format has synonyms. Each spelling is given twice: as a reader sees it (`spelling`), and as a writer builds it, by its
`head` (a stage file's family call, a parameter file's key) and its `arguments` (positional, or by field), each a formula
in the chart's coordinates. A keyed form may give `defaults` for fields left out, and `none`: the token for an
absent bound with the value it stands for in each field, as the parameter files' `null` is −∞ in `bot` and ∞ in `top`; and a mixture's form may write its fields once per component (`per_component`), each field's formula then a vector
over the components.

A default belongs to a written form, not to the law. The parameter files' rule that an omitted truncation bound means
three standard deviations is one. Defaults are filled before two laws are compared and before a file is hashed. A
parameter file writes `null` for no bound on a side, as Distributions.jl writes `nothing` and PyMC and NumPyro write
`None`. A stage file writes `inf`. (These arrive with the truncated laws.)

## The files

| file | what it is |
|---|---|
| `source.yaml` | the one source: every row, by kind |
| `source.schema.json` | the JSON Schema the source must satisfy |
| `formulas.py` | the formula syntax, and an evaluator for the generator's checks and the tests |
| `generate.py` | writes the two files below from the source, or checks that they are current |
| `probability-distributions.ttl` | the ontology in OWL 2, Turtle syntax (generated) |
| `probability-distributions.json` | a flat table, one row per measure, operator, property, constraint, family and chart (generated) |
| `test_ontology.py` | the tests |
| `CHANGELOG.md` | what each version changed |
| `LICENSE` | Creative Commons Attribution 4.0 International |

Never edit a generated file; edit the source and run the generator. The tests fail when a generated file is out of date.

Everything runs with `uv`, from this folder:

```bash
uv run --with pyyaml --with jsonschema python generate.py            # write the Turtle file and the table
uv run --with pyyaml --with jsonschema python generate.py --check    # exit 1 if either is out of date
uv run --with pyyaml --with jsonschema --with numpy --with rdflib --with pytest pytest -q
```

## How a row reads

In the table, every row has an `id`, a `kind`, a `name` (unique within its kind; a chart's is unique within its family,
and its `qualified_name` is `family/chart`), a `label` and, except for charts, a `definition`. References between rows are
by identifier.

- A **family** gives its `stated_set`; its `measure` in the operator notation above; `built_from`, its measure as operators
  applied in order to a named measure, with the arguments as formulas in the canonical coordinates; `where`, auxiliary
  quantities those formulas may use; its `canonical_chart`; its `charts`; its `properties`, as formulas in the canonical
  coordinates; its `boundaries`, where its domain meets another family; and its `reductions`, where a point of its domain
  is a member of another family. A subfamily gives instead the family it is a `subfamily_of` and its `constraints`.
- A **chart** gives its `family`, whether it is `canonical`, its `coordinates`, each with a name, a symbol, a meaning and a
  domain, and its `domain_conditions` on the coordinates jointly. A coordinate that is an expectation under the law says
  so in `as_expectation`, so that its meaning can be checked: the standard deviation of the logarithm after truncation
  is `sqrt(E(log(X)**2) - E(log(X))**2)`, which no chart before truncation satisfies. A mixture's chart may state a
  vector coordinate's meaning component by component, in `as_component_expectation`. A chart other than the canonical one also gives
  `to_canonical` and `from_canonical`, one formula per coordinate, with auxiliary quantities in `to_canonical_where` and
  `from_canonical_where`; `conversion`, `exact` when every formula is rational and `irrational` otherwise; and `covers`,
  when it reaches only part of the canonical domain. Then come `written_as`, per format, and `cross_references`.

The source is the same, organized by kind, with charts inside their families and references by name.

## The formula syntax

A formula is an arithmetic expression in Python's syntax over a chart's coordinates. It may use numbers, the coordinate
names, `+ - * / **`, comparisons (`< <= > >= == !=`), `and` and `or`, the functions `sqrt`, `exp`, `log` (with log 0 = −∞), `Phi` (the
standard normal distribution function), `phi` (its density) and `xphi` (x·φ(x), zero at an infinite x), and the constants
`inf` and `pi`. Infinite values follow IEEE arithmetic, so a bound of `inf` passes through exp and log. In a moment's
formula `k` is the order; in an operator's map or set `z` is the variable; in a coordinate's `as_expectation`, `E(·)` is
the expectation under the law and `X` the draw. The constant `euler_gamma` is Euler's γ = 0.5772156649015329.

A coordinate may be a vector or a matrix. Arithmetic and comparisons on vectors are elementwise, and a condition holds
when it holds at every entry; `x[j]` is entry j, counted from one; `[a, b]` is a vector; and `sum`, `min`, `max`,
`count`, `first`, `last`, `index` (1, 2, …, n), `increasing` (strictly), `lex_increasing`, `any`, `all`, `diff`
(successive differences), `heads` and `tails` (all entries but the last, or the first), `row(M, i)` and `interp` (the
piecewise-linear function through given points) act on vectors and matrices. In
a mixture's construction `j` is the component; in a kernel's properties the state's name is the current position. Nothing else parses, so any consumer can read a formula without running code
from the source.

## Identifiers and the namespace

Every row has an opaque identifier, `PD_` and seven digits, assigned in order as rows are added and kept for life. Labels
and names may be corrected; identifiers never change. An identifier that leaves the ontology is listed under `retired` and
is never used again.

The namespace is provisional, `https://example.org/provisional/ontologies/probability-distributions/`, until a permanent
namespace is registered at w3id.org. It is set in one place, the source's `namespace`.

## Versions and releases

Versions are semantic. Each release's entry in the changelog says whether a change alters a measure (a family's
definition), a chart (its coordinates or conversions), or only labels and text. A consumer pins a release. A toolkit
records, for each of its families, the identifiers of the family and chart here and the release it was checked against,
and tests that record against a copy of `probability-distributions.json`. The schemas' parameter files name their schema
version, which names the release the schema follows.

## ProbOnto

[ProbOnto](https://github.com/probonto/ontology) is the one existing ontology whose content has the shape needed here:
families with several named parameterizations, and conversion formulas between them. But it has been dormant since 2017,
and it gives nothing for a law as a measure or for operators. So this ontology does not import it. It copies what it needs, audits it, and links each
chart to ProbOnto's parameterization: `skos:exactMatch` for the same chart of the same family, `skos:closeMatch`
otherwise. It does not use `owl:sameAs`, which would merge every statement made about the two identifiers.

This ontology contains material from ProbOnto 2.5, © 2016 Maciej J Swat, Pierre Grenon and Sarala M Wimalaratne, licensed
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): the identifiers of its parameterizations, as
cross-references, and the parameterizations and conversion formulas a chart's `provenance` names, rewritten in this
ontology's notation. ProbOnto is described in Swat, Grenon and Wimalaratne (2016), "ProbOnto: ontology and knowledge base
of probability distributions", *Bioinformatics* 32(17):2719–2721, doi:10.1093/bioinformatics/btw170.

## The catalog

| family | status |
|---|---|
| normal, with charts mean and standard deviation (canonical) and mean and variance | in this release |
| lognormal, with its subfamily of mean one | in this release |
| point mass, with its subfamily at one | in this release |
| truncated normal, with Bellman-SYM's `TruncatedNormal(μ, σ, l, u)` as its canonical chart | in this release |
| truncated lognormal, with Bellman-SYM's `TruncatedLogNormal(μ, σ, l, u)` as its canonical chart, and its subfamily of mean one, written by the parameter files' chart (the standard deviation of the logarithm after truncation, bounds in standard deviations, an omitted bound meaning three and `null` none) | in this release |
| uniform, with Bellman-SYM's `Uniform(a, b)` as its canonical chart, and its subfamily of mean one, written by the parameter files' `{Uniform: {half_width: w}}` | in this release |
| type I extreme value (Gumbel), with Bellman-SYM's `TypeIExtremeValue(μ, s)` as its canonical chart | in this release |
| finite discrete law on real points, written by Bellman-SYM as a `Mixture` of numbers, and its subfamily of mean one, written by the parameter files' `Discrete` | in this release |
| categorical law on labels, Bellman-SYM's `Categorical`, with `Bernoulli(p)` as its chart for two labels | in this release |
| finite Markov kernel, Bellman-SYM's `DiscreteMarkov` and `MarkovChain`, two spellings of one chart | in this release |
| finite mixture, an operator, Bellman-SYM's `Mixture` | in this release |
| lognormal mixture, Bellman-SYM's `Mixture` of `LogNormal` components, and its subfamily of mean one, written by the parameter files' `LogNormalMixture` | in this release |
| truncated lognormal mixture, Bellman-SYM's `Mixture` of `TruncatedLogNormal` components, and its subfamily of mean one, written by the parameter files' `TruncatedLogNormalMixture` | in this release |
| quantile table, the pushforward of the unit uniform under a piecewise-linear quantile function, and its subfamily of mean one, written by the parameter files' `Tabulated` | in this release |

Families outside this list, such as the gamma, Weibull and beta, enter when a schema or a toolkit needs them.

## License

[CC BY 4.0](LICENSE). Cite this ontology by its title, version and namespace.
