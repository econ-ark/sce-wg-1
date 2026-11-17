# Changelog

Each entry says whether a change alters a class (its axioms), a term's meaning (a definition or a formula), a written
form, or only labels and text.

## 0.1.0-draft.3 (unreleased)

Bellman-SYM's documentation is public, at bellman.io, so the ontology links its concepts. With them, two corrections
made on 2026-11-12 in the buffer-stock model's repository's copy of this ontology, which this copy lacked; this
repository's copy is the ontology's home, by the owner's decision of 2026-11-14. Then, on 2026-11-16, minimum human
wealth, which the natural family's stage file now takes in from the next period as a field. No class or axiom changes;
one term is added, and one term's meaning is corrected.

**New terms.**
- The row `BSM_0000232`, `minimum-human-wealth`, h_min: the present value of the least future noncapital income on the
  path of lowest permanent shocks, as a ratio to permanent income, excluding this period's; zero in the last period
  and (𝒢ψ_min/R)(ξ_min + the next period's) before it, with the limit ξ_min 𝒢ψ_min/(R − 𝒢ψ_min) where 𝒢ψ_min < R.
  Its written forms are BST's `\hNrmPes`, the notation registry's `human-wealth-pessimist`, and the natural family's
  stage file's `h_min[>]`, the field that bounds a. Its sources are the paper's appendix on a positive minimum income.
  A test checks that its formula is the limit of its recursion, and minus the natural limit's value.

**Meanings changed.**
- The row `BSM_0000081`, `natural-limit`, in its definition and its domain note; the formula is unchanged. The note
  said that there is no natural limit where ψ_min ≥ ℛ. The value is zero where the worst transitory income is zero,
  as with BST's zero-income event, at any growth of permanent income: the present value of nothing. Where the worst
  transitory income is positive and ψ_min ≥ ℛ, the limit is finite at every finite horizon and falls without bound as
  the horizon recedes, so the limiting model has none. The owner found the error, which had reached the schemas'
  natural family as a requirement its model does not need.

**Written forms.**
- The row `BSM_0000055`, `expectation`: its Bellman-SYM form is `E_{ψ,ξ}` in place of `E_{ψ,θ,j}`. Since the owner's
  decision of 2026-11-12 the families' stage files draw transitory income ξ whole, from a mixture, and no longer draw
  θ and the event j with a line defining ξ. The same change, in three rows' text and written forms:
  - `BSM_0000033`, `transitory-shock-all`, says the files draw ξ whole;
  - `BSM_0000034`, `transitory-shock-employed`, and `BSM_0000035`, `unemployment-event`, lose their Bellman-SYM
    forms, θ and j, which the files no longer draw, and say so;
  - the event's written form is now the parameter file's block, `income.unemployment`.

  None of these meanings changes.
- Each term and category that names a Bellman-SYM concept links to the concept's page,
  `https://bellman.io/wiki/<slug>/`: in the Turtle file as `rdfs:seeAlso`, in the table as `bellman_url`. Every
  pinned slug's page answered on 2026-11-14.
- The source `bellman-sym`, Bellman-SYM's documentation, is declared, with the address of its wiki, so the ontology
  names it as a source. The generator refuses a source that names a concept without it.

**Labels and text.**
- The row `BSM_0000057`, `borrowing-limit-natural`: its definition said that no stage file carries the natural
  constraint. Since 2026-11-16 the natural family's stage file takes it in from the next period as a field, minus
  minimum human wealth, h_min[>]; it is still no parameter. The definition says so and names h_min, and the row cites
  the appendix's lemma on the natural borrowing limit. Its meaning is unchanged.
- The row `BSM_0000081`, `natural-limit`, says that its value is −h_min in the limit of an infinite horizon.
- `bst-anchors.txt` was read again from BST's published page on 2026-11-16: its appendix on a positive minimum income
  added 80 anchors, and none had gone.
- The statement that Bellman-SYM's documentation is not public, in the README, `bellman-concepts.txt` and the
  definition of `bellmanConcept`, is corrected. The rule that a concept is named and never linked, which rested on
  it, is rescinded, on the owner's ruling of 2026-11-14.
- The README's section on Bellman-SYM's terms links the documentation's pages on the stage, its perches and the values
  at them.
- The README's links to Project A and to the Rosetta Stones are absolute addresses, so that they hold in a copy of this
  folder, such as the buffer-stock model's repository's.
- The README writes the end-of-period value and its marginal value, `V[>](a)` and `D_{a}V[>](a)`, as code. Written
  plainly, Markdown read `[>](a)` as a link, and GitHub showed a link labeled ">" in place of the perch mark and the
  argument.

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
