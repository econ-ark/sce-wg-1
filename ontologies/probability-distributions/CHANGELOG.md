# Changelog

Each entry says whether a change alters a measure (a family's definition), a chart (its coordinates or conversions), or
only labels and text.

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
