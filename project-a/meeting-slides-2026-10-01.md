# Project A: four slides for the meeting of 1 October 2026

Draft. Five minutes. Speaker notes follow each slide in a `::: {.notes}` block,
the form used in `presentations/meeting-2026-10-01-project-a.qmd`, so that a
slide can be pasted into a Quarto deck unchanged. Sources for the two examples
are listed at the end of the file.

---

## Objectives of Project A

1. We propose and work on a journal special issue that develops semantic
   ontologies for economic models, to make AI-assisted modeling more
   transparent and verifiable.
2. We divide into subgroups, one for each modeling language, toolkit,
   empirical method or model class.
3. Each subgroup writes a semantic ontology for its domain.

::: {.notes}
*About 60 seconds.*

Project A responds to a change in how modeling code is produced. Language
models now write, modify and translate our code, and that code can compute a
model different from the one intended while nothing in the code shows it. To
check such code, and to move a model from one toolkit to another, we need a
statement of what the model is that does not depend on the code.

The project has three objectives. We will propose a journal special issue,
with the working title "AI-Assisted Modeling in Economics: Transparency and
Verification". We will divide into subgroups, one for each modeling language,
toolkit, empirical method or model class that members work on. Each subgroup
will write such a statement for its own domain, which we call a semantic
ontology, and report it in a paper for the issue. A final paper, written
jointly, will compare them.
:::

---

## What is a semantic ontology?

A semantic ontology is to model code what an estimand is to an estimator.

It is an explicit, machine-readable account, independent of code and solver, of

1. what exists (value functions, distributions, operators, agents, states,
   shocks, timing, the equilibrium concept),
2. what stands for what (the objects that each written form denotes, their
   types, and how they relate, for economic meaning and for computation),
3. what is written down (the model file or the toolkit calls), and
4. when this reading holds (domains, timing, information),

all stated in a formal structure, such as a typed algebra or a graph.

It can describe a toolkit, a model class, a solution method, data, or the
mathematical structures that organize these.

**Key point.** These are implicit in the field; we want to make them explicit
and machine-readable.

::: {.notes}
*About 75 seconds.*

Econometricians separate the estimand from the estimator. The estimand is
defined before any procedure, and an estimator is judged against it. A
semantic ontology does the same for a model: it states what the code is meant
to compute, apart from the code.

It has four parts. The first is what exists: value functions, distributions
and the operators that relate them, together with the agents, states, shocks,
timing and equilibrium concept of the theory. The second is what stands for
what: for each written form, the objects it denotes, their types and how they
relate, for economic meaning and for computation. The third is what is
written down: the model file or the toolkit calls. The fourth is the set of
conditions under which this reading holds. All four are stated in a formal
structure, such as a typed algebra or a graph.

Economists carry all of this in their heads and in the conventions of their
subfield. The aim is to make it explicit and machine-readable, so that code,
including code written by an AI, can be checked against it.
:::

---

## Two examples

**Economics: one period of a consumption-saving problem**

$$
k \;\xrightarrow{\ \text{income}\ }\; m \;\xrightarrow{\ \text{consumption}\ }\; a
$$

| What we write | Read forward | Read backward |
|---|---|---|
| a variable | a distribution | a value function |
| an arrow | a transition | an operator on value functions |
| the chain | the law of motion | the Bellman operator |

The ontology is a typed algebra: every symbol we write has a type, and is
assigned a mathematical object of that type.

**Materials science** (Rajamohan et al. 2025)

One beamline names a variable `load-cll`, another `ld-cell`. The ontology
attaches both names to one term, so that code written for one facility's data
also works on the other's.

::: {.notes}
*About 105 seconds.*

The first example is from economics. One period of a consumption-saving
problem has three variables and two arrows: assets on arrival, resources
after interest and income, and assets after consumption. A variable is only a
name. The ontology records what each name denotes, and it denotes a different
object in each of two readings. Read forward, each variable denotes a
distribution of households and each arrow a transition, so the chain is the
law of motion. Read backward, each variable denotes a value function and each
arrow an operator on value functions, so the chain is the Bellman operator.

In simple terms this is a typed algebra: every symbol we write has a type,
every symbol is assigned a mathematical object of that type, and symbols
compose only when their types match. The Bellman calculus does this for
recursive problems. The same can be done for the sequence-space Jacobian
approach, where a variable denotes a time path and a block a map between
paths, and for Dynare, where a variable denotes a stochastic process.
Choosing the formalism, whether an algebra, a graph or a formalization in
Lean, is part of the project.

The second example is from materials science. In the Materials Data Science
Ontology, two facilities may record one variable under different names, and
the ontology attaches both names to one term, so that a program written for
one facility's data works on the other's. There the objects are measured
quantities. In economics they are distributions, value functions and
operators, and so the types matter more.
:::

---

## The proposal goes to the editor within three weeks

| Week | Step |
|---|---|
| 1 | The group comments on the draft (round 1). |
| 2 | We redraft, and the group comments again (round 2). |
| 3 | We send the proposal to the editor. |

::: {.notes}
*About 40 seconds.*

The draft proposal is on the group site, on the Project A page. We ask for a
first round of comments from the group this week. We will then redraft and
ask for a second round, and we aim to send the proposal to the journal's
editor within three weeks of today. The most useful comments at this stage
are on the definition and on the domains the subgroups should cover. Please
also tell us which domain you would like to work on.
:::

---

## Sources for the examples (not a slide)

- Materials science. Rajamohan, B. P., A. C. H. Bradley, V. D. Tran, et al.
  (2025). "Materials Data Science Ontology (MDS-Onto): Unifying Domain
  Knowledge in Materials and Applied Data Science." *Scientific Data* 12, 628.
  <https://doi.org/10.1038/s41597-025-04938-5>. The example of one variable
  named `load-cll` at one beamline and `ld-cell` at another is on p. 4; the
  paper gives it as an illustration of what the ontology allows.
- Recursive problems. The forward reading (each variable to a state space and
  each relation to a transition) and the backward reading (each variable to a
  set of value functions and each relation to an operator) are the forward and
  backward models of Session B of the talks "Categorical types and AGI"; the
  chain of arrival, decision and continuation states is the illustrative
  example of the Bellman calculus (Carroll and Shanker).
- Sequence-space Jacobian. Auclert, Bardóczy, Rognlie and Straub (2021):
  Definition 2 of the appendix (a sequence-space model is a set of blocks,
  each mapping input sequences to output sequences, whose directed graph is
  acyclic), and equations (27) to (31) (the equilibrium system and its
  first-order solution by the implicit function theorem).
- Dynare. Villemot (2011), "Solving rational expectations models at first
  order: what Dynare does", Dynare Working Paper 2, section 2.1: the model
  $E_t f(y^{+}_{t+1}, y_t, y^{-}_{t-1}, u_t) = 0$, the convention that "a
  variable decided at date t should have a time subscript of t", and the
  policy function $y_t = g(y_{t-1}, u_t)$.
