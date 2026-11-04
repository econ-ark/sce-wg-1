# Changelog

Each entry says whether a change alters a class (its axioms), a term's meaning (a definition or a formula), a written
form, or only labels and text.

## 0.1.0-draft.2 (unreleased)

The ontology stated in Bellman-SYM's terms, after consultation on Bellman-SYM's concepts on 2026-10-31. It names no
toolkit.

**New terms.** Rows `BSM_0000160` to `BSM_0000231`:
- the three perches, the stage and the trellis;
- the arrival and continuation values;
- the three derivative terms of the values;
- the end-of-period value and its marginal value;
- the arrival and decision laws of motion and the connector;
- the backward stage operator and the forward distribution operator;
- the feasible set;
- two divergences: 𝕄 in two senses, and the schemas' stage files still writing a retired role word;
- the natural and the artificial constraint: the constrained perfect-foresight benchmark and its axiom; four
  properties, among them that the constraint in force binds; and eleven results:
  - the constrained benchmark's taxonomy, and a vanishing MPC without the RIC;
  - the natural constraint never binding, and an artificial one binding (deduced);
  - the WRIC needing no artificial constraint (stated);
  - the problem with ℘ = 0 as a case of Ma, Stachurski and Toda, and the compact feasible set;
  - among the conditions alone, that the RIC without the GIC means finite human wealth;
- Ma, Stachurski and Toda's conditions:
  - the liquidity-constrained class, a ≥ 0 with a positive lowest income, and its axiom;
  - the moment E[ψ^(−ϱ)], the discounted-return factor and their condition, MST-βR;
  - four results: existence under the FVAC and MST-βR; a stationary distribution, adding the RIC; MST-βR implying
    the GIC-Mod, tested on sampled models; and, from their 2022 paper, existence with no condition on the return when
    there are no permanent shocks;
- the four borrowing-constraint scenarios (the buffer-stock model's `schemas/constraint-scenarios.md`):
  - the classes `natural-constraint`, with `natural-with-point-mass` and `natural-without-point-mass` under it, and
    `zero-infima`; `with-artificial-constraint` is the fourth;
  - their axioms: the natural constraint in force, the joint worst income with and without a point mass, an artificial
    constraint tighter than the natural one, positive floors, a zero infimum, no zero-income event, finite negative
    moments, and, for the whole class, membership in one of the four;
  - the bounds ψ_max, θ_min and θ_max;
  - two remarks: without a point mass, the natural limit is reached only when ϱ < k; and with zero infima, a ≥ 0 binds;
  - six family rows, one for each family the schemas now write.

**Meanings changed.**
- The value function is the decision value, `value-decision`.
- The consumption function is the policy.
- The dynamic budget constraint is a law of motion, the composite of the decision law, the connector and the next
  period's arrival law.
- The Euler equation is a relation, and its clause covers the natural constraint too.
- The expectation and the cross-sectional mean are operations.
- BST's T is related to the stage operator.
- The life-cycle class binds each primitive to the stage occurrence that reads it.
- The bounds are properties of the laws.
- The unemployment and survival events are shocks on two-point sets; the category of event is removed.
- The measures' perches are stated, and the income measure is a second forward problem.
- The constrained perfect-foresight results are stated within the new constrained benchmark. That benchmark, and the
  paper's limit as ℘ ↓ 0, are limits of the liquidity-constrained class.
- The WRIC's necessity without an artificial constraint is treated as true until the paper proves it.
- The deduction that an artificial constraint binds is stated for a borrowing limit, a_Art ≤ 0.
- The point-mass axiom names the joint worst income and belongs to the natural scenario with a point mass, not to the
  whole class; the model without one is a scenario of its own. Bounded support is a membership axiom of the natural
  scenarios, no longer a hypothesis of BST's class. BST's class lies inside the natural scenario with a point mass.
- The edge case, a ≥ 0 under laws with infima zero and no point mass, is a member: the zero-infima
  scenario. `toy-untruncated` is a member.
- The liquidity-constrained class is a ≥ 0 binding, across the artificial scenario at a_Art = 0 and the zero-infima one,
  with no zero-income event in place of a positive lowest income.
- HAFiscal's cap on β is no longer a divergence. It is an implementation detail of
  HAFiscal's code, which keeps parameters away from the boundary where the solution slows drastically, and not a
  feature of the model class. `BSM_0000152` is retired.

**Written forms.**
- The ontology names no toolkit. HARK's names for the terms, its sources and its ten divergences moved to HARK's Rosetta
  Stone in the schemas, among them the cyclical index, with the requirement that the solver and the
  simulation be consistent. Their identifiers are retired. The realization role and the approximation kind of divergence are
  removed.
- Each format has a role: notation or calibration.
- Objects carry their perch, their state, the set a state takes values in, and Bellman-SYM's concept where it has one.
- A result can name the class its limit lies in (`limit_in`), and a benchmark can be a subclass of another class.
- Every divergence has a kind: meaning, notation, convention or absence.
- The perfect-foresight FVAC is `fvac-pf`, written FVAC-PF, with its factor `value-of-autarky-factor-pf`. A modified
  condition's signifier follows its base name, as in GIC-Mod, by rule. The three results
  named for it are renamed to match, with their identifiers unchanged.
- Two papers are sources, cited by their own numbering: Ma, Stachurski and Toda (2020) and (2022), in their arXiv
  versions. A condition's short name may carry Greek letters.
- The schemas' families bst/1 and bst-markov_ui-and-agg/1 gave way to six, one for each scenario the members fall in.
  Their rows `BSM_0000136` and `BSM_0000137` are retired, as is `BSM_0000179`, the stage files' retired role word,
  which the stage files' rewrite resolved. The natural limit and the stage have no stage-file spelling, since no stage
  file carries the first as a parameter and each family names its own stage.

52 tests.

**2026-11-03.** The family rows `BSM_0000225`, `bst-natural-no-point-mass/1`, and `BSM_0000227`, `bst-zero-infima/1`,
are retired: both families were withdrawn as uninteresting cases. The scenario classes
`natural-without-point-mass` and `zero-infima` stay, written by no family; the members `toy-natural` and
`toy-untruncated` left the schemas. Labels and text only: no class or term changes.

## 0.1.0-draft.1 (unreleased)

The first draft, with rows `BSM_0000001` to `BSM_0000159`, of which `BSM_0000151`, a divergence withdrawn on checking,
is retired. The design: the eleven kinds; membership axioms and hypotheses as two tiers; buffer-stock saving as a
property of the solution; the perfect-foresight model as the class's benchmark, outside it; formulas in the ontology of
probability distributions' syntax; written forms in five formats; and citations pinned to BST's published page,
econ-ark's registry 8.0.0, HARK at `4c285e86` and HAFiscal-QE at `1afdf80`.

The rows:
- **classes:** the class, BST's own, the benchmark, and nine extensions;
- **axioms:** seven membership axioms of the class, the atom at the worst transitory shock among
  them; seven hypotheses of BST's class; and the benchmark's one;
- **terms:** forty objects, the four moments of the permanent shock, and sixteen quantities;
- **conditions and results:** eleven conditions, twelve properties, and twenty-five results, eleven of them
  implications among the conditions;
- **identities, families and divergences:** seven identities, the schemas' two families, and fourteen divergences, ten
  in HARK and four in the published HAFiscal paper and code.
