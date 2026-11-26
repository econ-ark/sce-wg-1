# Changelog

Each entry says whether a change alters a measure (a family's definition), a chart (its coordinates or conversions), or
only labels and text.

## 0.1.0-draft.3 (unreleased)

A measure added, and with it an operator and a coordinate domain; no existing measure or chart changes.

- The jumpless truncated lognormal (`PD_0000065`), the law of exp(μ + σZ) where Z, on z ≥ b, has the standard normal
  density less its reflection in b, (φ(z) − φ(2b − z))/(Φ(−b) − Φ(b)): truncated below at l = exp(μ + σb) with no jump in
  the density, and no bound above. Its canonical chart (`PD_0000066`) is (μ, σ, l), as the truncated lognormal's.
- Its subfamily of mean one (`PD_0000067`), written by the parameter files' `JumplessTruncatedLogNormal`
  (`PD_0000068`): the standard deviation of the logarithm, and the bound in standard deviations below the center, an
  omitted bound meaning three.
- The thinning by a bound's reflection (`PD_0000064`), a case of conditioning, which builds it. An operator's `weight`,
  the probability of keeping a draw, enters the source's schema with it.
- The coordinate domain `negative`, (−∞, 0), for the bound.

## 0.1.0-draft.2 (unreleased)

Only labels and text: no measure or chart changes. Bellman-SYM's documentation is public, at bellman.io, so its page of
shock distributions, from which the `bellman-sym` written forms are read, is declared as a source, beside ProbOnto, and
the README links it.

## 0.1.0-draft.1 (unreleased)

The first draft. The design: the six kinds, the three primitive operators, the identity rule, the three settlements, the
formula syntax and the two written forms. The first rows, all new:

- the standard normal, the base of the normal-based families;
- the operators pushforward, conditioning and product with a kernel, with the affine and exponential maps as cases of the
  pushforward;
- the properties support, mean, moments, moments of the logarithm and atoms, and the constraint of mean one;
- the normal, with its charts of mean and standard deviation (canonical) and mean and variance;
- the lognormal, with its subfamily of mean one;
- the point mass, with its charts of a normal with variance zero and a lognormal with zero spread, and its subfamily at
  one;
- the truncated normal, conditioned on an interval in the variate's units, with the operator of truncation to an
  interval, and its reduction to the normal when neither bound binds;
- the truncated lognormal, conditioned on an interval in the draw's units, and its reduction to the lognormal when
  neither bound binds; its subfamily of mean one, written by the parameter files' chart: the standard deviation of the
  logarithm after truncation, and the bounds in standard deviations of the normal before truncation, with an omitted
  bound meaning three and `null` meaning none;
- the uniform on the unit interval, as a named measure, and the uniform, with its subfamily of mean one written by the
  parameter files' half-width;
- the standard Gumbel, as a named measure, and the type I extreme-value law, Bellman-SYM's `TypeIExtremeValue(μ, s)`;
- the finite mixture, a case of the product with a kernel, which Bellman-SYM writes `Mixture`;
- the finite discrete law on real points, and its subfamily of mean one, written by the parameter files' `Discrete`;
- the categorical law on labels, with the Bernoulli law as its chart for two labels;
- the finite Markov kernel, a family whose argument is the current state, which Bellman-SYM writes `DiscreteMarkov` or
  `MarkovChain`;
- the lognormal mixture and the truncated lognormal mixture, mixtures of their components, each with its subfamily of
  mean one, written by the parameter files' `LogNormalMixture` and `TruncatedLogNormalMixture`: each component's mean
  of the logarithm, stated relative to the others, and its standard deviation, after truncation where there is any, with
  one common shift making the mean one;
- the piecewise-linear map, a case of the pushforward, and the quantile table, the pushforward of the unit uniform under
  a piecewise-linear quantile function, with its subfamily of mean one, written by the parameter files' `Tabulated`.

Every coordinate that is an expectation under the law says so, and the tests check it by quadrature. Every named
measure states its density and support, and the tests integrate each from them. Coordinates may be vectors and matrices.
