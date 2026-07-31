---
title: Semantic Ontologies in Economics
subtitle: Special Issue Proposal
authors:
  - name: Christopher Carroll
  - name: Akshay Shanker
exports:
  - format: pdf
    template: templates/plain_latex_wide
    output: JEDC-special-issue-proposal.pdf
  - format: tex
    template: templates/plain_latex_wide
    output: JEDC-special-issue-proposal.tex
downloads:
  - file: JEDC-special-issue-proposal.pdf
    title: Proposal (PDF)
---

## The Challenge: AI and the Meaning of Economic Models

When economists compute a model, its precise *meaning* is
distributed, much of it implicitly, across prose, notation, calibration, and
code.
The paper says "we solve the following model", but its equations
underdetermine both what its code computes and what the computations mean.
Only an informed reader can fill the gaps, one who knows the surrounding
literature and has absorbed, through their professional networks, the conventions and
traditions the paper leaves unstated.
The same gaps confront anyone who attempts to interpret the model's findings,
rebuild the model, or extend it.
As a result, without a concrete statement of the model's meaning to check against,
computational results are hard to cross-verify, and interoperability between
implementations becomes difficult.

Relying on implicit professional convention alone is costly even amongst humans,
but it fails completely when AI is used to write, modify, and
translate modeling code.
To interpret or verify AI output, we
need a statement, independent of the code, of which economic objects are
computed and which relations among them are enforced; these statements are called
*semantic ontologies*.
Outside economics, the use of semantic ontologies has grown rapidly,
because without them, AI outputs remain probabilistic, and prone to error and misunderstanding 
([Grüninger and Menzel 2003](#ref-gruninger2003);
[Modelica Association 2023](#ref-modelica2023);
[Gleeson et al. 2010](#ref-gleeson2010);
[AWS Database Blog 2026](#ref-aws2026); see
[Semantic Ontologies](#semantic-ontologies) below).
With semantic ontologies, translating models between toolkits, and even
generating new modeling research, become operations a language model can
carry out and be checked on cheaply, rather than manual recoding.

## The Proposed Special Issue

We propose a special issue that constructs semantic ontologies for the
domains of computational economics: domain-specific modeling languages (for
example, Dynare), toolkits (for example, HARK and SSJ), empirical methods
(for example, structural modeling and estimation), and model classes (for
example, life-cycle, real-business-cycle, and agent-based models).
Each paper takes one domain of study, proposes a semantic ontology, and
demonstrates it on worked examples of the team's own choosing.
In addition to the semantic ontologies, the working group will author a
paper and a community resource of canonical models and their
ontologies.[^mmb]
<!-- Matt: this is a key passage, please put it in your words. -->
The special issue will also include related contributions by the working
group that use the stated ontologies to compare different modeling
strategies for the same problem, for instance agent-based models against
heterogeneous-agent models.

The SCE working group will submit a subset of the papers, an open call will
invite the rest, and a comparison paper, written jointly by the participating
teams, will close the issue.

The semantic ontologies we develop will be kept in an open-source
[GitHub repository](https://github.com/econ-ark/sce-wg1), to which members of the community can contribute improvements
and modifications.
<!-- needs to be something here about challenges for economics, i.e. application diversity. -->
<!--
The format is familiar at the journal, whose scope includes computational
methods: in two earlier special issues, several teams computed the same models
and a closing comparison drew the results together (den Haan, Judd and
Juillard 2010, 2011).
We keep the many teams and the closing comparison, but instead of solving
common models the teams state what their models and code mean.
When a model written for one toolkit can be read, checked, and re-solved in
another, the semantic ontologies that make this possible are research
infrastructure.
-->

## Organization

Papers pass an internal review within the working group [process TBC] and then
the journal's ordinary external refereeing.
We expect six to eight papers, with a session at the Society's conference
between submission and revision.

### Teams and Editors

The working group's members include developers of Dynare, HARK, and the VFI
Toolkit.
Committed teams: [to be listed; only teams that have agreed in writing].
The working group's papers will come from its subgroups.
Akshay Shanker and Matthew McKay chair the working group and coordinate the
teams and the internal review.
The guest editors (a lead editor and at least one co-editor, neither
submitting to the issue) are drawn from outside the working group [names,
institutions; TBC].
Papers are submitted through the journal's editorial system, marked for this
special issue, and are refereed under the journal's ordinary standards; the
guest editors handle every paper, including the comparison paper, subject to
the journal's final editorial authority.

### Timeline

Calendar dates TBC on acceptance.

- Call for papers [on acceptance]
- Submissions [+9 months]
- Internal review completed [+12 months; process TBC]
- Referee reports [+15 months]
- Revisions and the comparison paper [+24 months]

<!--
[^example]: For example, the sentence "a policy shock raises entrants at date
$t$" is satisfied by two different models, since the shock may reach the
cross-sectional distribution at $t$ or at $t+1$, and the impulse response
differs before any grid or solver is chosen.
The code computes one of the two models, and nothing on the page records
which.
The documented counterpart: Su and Judd (2012) recast one estimator in two
computational formulations and return identical estimates, while Dubé, Fox and
Su (2012) show a loose inner-loop tolerance changing estimated own-price
elasticities by roughly a factor of two.
-->

[^cg]: Whichever domain a paper addresses, its theory and mathematics are
taken as pre-existing: the Bellman equation is not in question, while what
a given Dynare file or HARK model means is. A language, toolkit, or empirical-method
paper therefore emphasizes the map from representations to the mathematical
objects they stand for, while a model-class paper emphasizes the objects and relations
implied by its mathematical and theoretical framework. Differences among the stated ontologies
are results for the closing comparison to report.

[^ha]: In a heterogeneous-agent model, for instance, the ontology contains the
response of decision rules to prices, the cross-sectional distribution
decisions induce, and the feedback of that distribution into prices, both
as relations of the theory and as their computational counterparts.

[^mmb]: The nearest precedent in economics, the Macroeconomic Model Data Base
([Wieland et al. 2012](#ref-wieland2012)), compares models under common variables, common shocks,
and a menu of common policy rules while each model keeps its own equations; it
standardizes comparison, not meaning.

```{raw:tex}
\clearpage
\setcounter{secnumdepth}{-1}
```

## Annex: Guidelines for Papers

### Semantic Ontologies

The goal of the semantic ontologies we propose is to codify formally the
meaning of computational models.
For our purposes, a semantic ontology consists of the objects and
relations within the domain of study, the meaning of those objects and relations, and
the written forms that record them (syntax: a file, a model write-up, a
specification).[^ha]
Theory supplies part of the semantic ontology (a general-equilibrium
model's objects are precisely defined), but the semantic ontology must
collect these definitions, map them concretely to computational and written
counterparts, and state the assumptions under which the mapping holds.
Without a written semantic ontology, nothing says which of the theory's
objects a given file or function call stands for, and ordinary solver code
gives one executable realization, not a solver-independent statement of what
the representation denotes.

The importance of semantic ontologies for interpreting and working with
AI-generated code and output is now broadly recognized across research
fields and in industry.
Manufacturing's Process Specification Language ([Grüninger and Menzel 2003](#ref-gruninger2003); [Bock and Grüninger 2005](#ref-bock2005)), Modelica for physical systems ([Fritzson and Engelson 1998](#ref-fritzson1998); [Modelica Association 2023](#ref-modelica2023)), planning's PDDL2.1 ([Fox and Long 2003](#ref-fox2003)), and neuroscience's
NeuroML ([Gleeson et al. 2010](#ref-gleeson2010)) each attach an explicit, solver-independent
meaning to a model representation.
Industry has met the same need from the opposite direction, reconstructing
never-written conceptual models of the business from its data and business
processes ([AWS Database Blog 2026](#ref-aws2026)).
Compared with all of these, economics is well placed: the relations among a
domain of study's objects are the theory itself, which is well-defined in economics.
What remains unstated is the map from the representations economists compute
with (model files, toolkit calls, estimation specifications) to that
theory, and the conditions under which the map holds.
Stating these maps, domain by domain, is the work this issue proposes.


### Research Domains and Themes

**Domains of study.**
Each paper in the special issue will address one *domain of study*.
Domains of study can include a modeling language, a toolkit, an empirical
method, a model class, or a combination of these.[^cg]

```{raw:tex}
\begin{displaybox}[breakable]{Domains of study}
```

::::{div}
:class: displaybox displaybox-domains

- **Modeling languages.**
  A modeling language is a fixed grammar in which a complete model is written
  as a file, as in Dynare's model language or Dolo's YAML model files.
- **Toolkits.**
  A toolkit is a collection of construction calls and classes from which a
  model is assembled in a programming language, as in HARK's agent classes,
  the sequence-space Jacobian toolkit ([Auclert et al. 2021](#ref-auclert2021)), or the VFI
  Toolkit.
- **Estimation and empirical methods.**
  An empirical method takes a model to data.
  It states which measured objects stand for the model's quantities (for
  example, prices and shocks), which classifications organize those objects,
  and which transformations construct the inputs to estimation or
  calibration.
  The simulated method of moments and indirect inference are examples of
  empirical methods, and so is the calibration of a computable
  general-equilibrium model to a social accounting matrix or input-output
  table.
- **Model classes.**
  A model class is a family of models built from the same kinds of objects, as
  in heterogeneous-agent macroeconomies or overlapping-generations economies.

::::

```{raw:tex}
\end{displaybox}
```

<!--
AAS to AAS: I am not sure about the model-class emphasis sentence (now in
the domain-of-study footnote), for review.
-->

**Research themes.**
The research themes of the issue are two of the core research questions
each paper will answer: first, constructing a semantic ontology for its
domain of study, and second, establishing the ontology's *metatheory*,
statements about the ontology rather than components of it.
There are three components to each semantic ontology: what is assumed to exist
(the *ontology*), what stands for and relates to what (the *denotation*), and
what is written down (the *syntax*).
Domains of study will differ in how important these components are, and some,
such as a model class, may not have certain components, such as syntax.
The metatheory states when the interpretation holds (*well-posedness*) and
what preserves it (*equivalence*, *adequacy*, and *convergence*).
Details of these research themes are given in the Research Themes
section at the end of this annex.

### Methodology

**Formalizing the semantic ontology.**
A requirement for each paper will be that it presents a *formal* account of
the semantic ontology of its domain of study.
However, the researchers choose the formalism in which they state these
components.

The available formalisms differ in how much meaning they fix, and they can
be ordered from least to most ([Uschold and Grüninger 1996](#ref-uschold1996)).

At one end, a team records which entities exist and which relations connect
them, as boxes and arrows: an entity-relationship diagram
([Chen 1976](#ref-chen1976)), a UML class diagram
([Berardi, Calvanese and De Giacomo 2005](#ref-berardi2005)), or a knowledge
graph ([Hogan et al. 2021](#ref-hogan2021)).
These *graphs and diagrams* name the model's objects but place few
restrictions on what they mean.

Writing the ontology as *logical axioms* fixes more: the axioms rule out
interpretations of the objects much as parameter restrictions rule out
models.
The axioms can be stated in any formal logic.
In the older tradition this meant first-order logic
([Gruber 1993](#ref-gruber1993)), and in much current practice it means a
description logic such as the Semantic Web's Web Ontology Language (OWL)
([Baader et al. 2017](#ref-baader2017);
[W3C OWL Working Group 2012](#ref-owl2012)).

The most is fixed by the *mathematical semantics* developed for programming
languages, which attach an explicit mathematical meaning to every written
form.
Denotational semantics assigns each form an object in the ordered
structures of domain theory ([Scott and Strachey 1971](#ref-scott1971)).
Initial-algebra semantics takes meaning to be the unique homomorphism from
a many-sorted algebra of terms
([Goguen, Thatcher, Wagner and Wright 1977](#ref-goguen1977)).
Typed categories interpret a typed syntax in a category with matching
structure ([Lambek and Scott 1986](#ref-lambek1986)).
Operational semantics gives rules for execution on an abstract machine
([Plotkin 1981](#ref-plotkin1981)), and axiomatic semantics gives the
assertions that hold before and after execution
([Hoare 1969](#ref-hoare1969)).

Practice differs by field.
Google and other technology firms record knowledge graphs from observed
data, without axioms ([Noy et al. 2019](#ref-noy2019)).
The Gene Ontology Consortium states its ontology of gene functions in
description logic ([Ashburner et al. 2000](#ref-ashburner2000)).
A few programming languages, such as Standard ML and WebAssembly, have been
given complete formal semantics
([Milner, Tofte, Harper and MacQueen 1997](#ref-milner1997);
[Haas et al. 2017](#ref-haas2017)), though most languages in use have not.

How far along this scale a paper goes depends on whether its domain of
study has a syntax.
A team whose domain has one (a modeling language or a toolkit) can use any
of the mathematical semantics; a team whose ontology has no syntax (a model
class, or an empirical method before its specification is constructed) can
axiomatize the ontology in a logic or record it as a graph.
Declarative languages make the mathematical route easiest: a Dynare or Dolo
file states the model itself rather than a procedure for solving it, so the
file is already the kind of written form a semantic map can interpret.
A team seeking machine-checked guarantees can go further and formalize its
domain in a proof assistant such as Lean, defining the model objects as
types and the file-to-object map as a function inside the system, so that
well-posedness and equivalence become theorems the machine verifies ([de Moura and Ullrich 2021](#ref-demoura2021)).


**Top-down vs. bottom-up approaches.**
A team can also build its semantic ontology top-down or bottom-up.
Building top-down, it starts from the theory and formalizes the theory's
objects; building bottom-up, it starts from observed data and relations and
abstracts the ontology from them, as industry does when it reconstructs a
conceptual model from a data catalog ([AWS Database Blog 2026](#ref-aws2026)).
In this issue we expect economic theory to supply the structure, so most
papers will work top-down; a bottom-up construction may suit agent-based
modeling or policy research, where observed relations precede a settled
theory.

## Research Themes

A paper addresses those of the following five research themes relevant to its
domain of study.
The first three are the components of the domain's semantic ontology; the
last two are statements about it (when the interpretation holds, and what
preserves it under changes of representation and computation):

```{raw:tex}
\begin{displaybox}[breakable]{The research themes}
```

::::{div}
:class: displaybox displaybox-themes

1. **Ontology: what is assumed to exist.**
The economic and mathematical entities and relations within the domain
(agents, states, shocks, timing, the equilibrium concept, operators,
functions, and which objects determine which), together with the criteria
for when two of them are the same ([Gruber 1993](#ref-gruber1993); [Guarino, Oberle and Staab 2009](#ref-guarino2009)).
The ontology is stated in its own terms, without reference to the syntax.
2. **Denotation: what stands for what.**
The meaning of the ontology's objects.
The meaning takes the form of relationships between the mathematical, economic
and computational representations, for instance value functions as economic
concepts, instantiated on a mathematical space, and approximated on the
computer.
Typically the denotations will also include relationships between these
representations and the written forms: each written form stands for its
mathematical or economic object under an explicit map ([Harel and Rumpe 2004](#ref-harel2004)).
3. **Syntax: what is written down.**
The set of legal written forms: the model file, the sequence of construction
calls, or the specification of an estimation exercise.
For instance, a language has a full grammar; a toolkit may expose construction
calls or classes.
A domain (such as an empirical method) may have no syntactic written form at
all, in which case much of the role of syntax is played by the denotation.

*The next two research themes are not components of the semantic ontology;
they are statements about it:*

4. **Well-posedness: when the interpretation holds.**
The conditions under which the denotation is well defined: domains, units,
timing, information structure, and the parameter restrictions assumed.
5. **Equivalence, adequacy, convergence: what preserves it.**
Denotational equivalence: two written forms, one denotation.
Adequacy: an implementation computes exactly the object denoted.
Convergence: a numerical approximation approaches it as grids and tolerances
are refined.

::::

```{raw:tex}
\end{displaybox}
```

## References

(ref-ashburner2000)=
Ashburner, M., C. A. Ball, J. A. Blake, et al. (2000). "Gene Ontology: tool
for the unification of biology." *Nature Genetics* 25(1), 25–29.
[[link]](https://www.nature.com/articles/ng0500_25)

(ref-auclert2021)=
Auclert, A., B. Bardóczy, M. Rognlie, and L. Straub (2021). "Using the
Sequence-Space Jacobian to Solve and Estimate Heterogeneous-Agent Models."
*Econometrica* 89(5), 2375–2408.
[[link]](https://mrognlie.github.io/papers/sequence_space_jacobian.pdf)

(ref-aws2026)=
AWS Database Blog (2026). "Build a semantic ontology to power AI assistants on
AWS — Part 1." 14 July 2026. Accessed 29 July 2026.
[[link]](https://aws.amazon.com/blogs/database/build-a-semantic-ontology-to-power-ai-assistants-on-aws-part-1/)

(ref-baader2017)=
Baader, F., I. Horrocks, C. Lutz, and U. Sattler (2017). *An Introduction to
Description Logic*. Cambridge University Press.
[[link]](https://www.cambridge.org/core/books/an-introduction-to-description-logic/6D329698AFC2E6C6C5C15801ED9B6D07)

(ref-berardi2005)=
Berardi, D., D. Calvanese, and G. De Giacomo (2005). "Reasoning on UML Class
Diagrams." *Artificial Intelligence* 168(1–2), 70–118.
[[link]](https://www.inf.unibz.it/~calvanese/papers/bera-calv-degi-AIJ-2005.pdf)

(ref-bock2005)=
Bock, C., and M. Grüninger (2005). "PSL: A Semantic Domain for Flow Models."
*Software and Systems Modeling* 4(2), 209–231.
[[link]](https://www.nist.gov/publications/psl-semantic-domain-flow-models)

(ref-chen1976)=
Chen, P. P. (1976). "The Entity-Relationship Model — Toward a Unified View of
Data." *ACM Transactions on Database Systems* 1(1), 9–36.
[[link]](https://dl.acm.org/doi/10%2E1145/320434.320440)

(ref-demoura2021)=
de Moura, L., and S. Ullrich (2021). "The Lean 4 Theorem Prover and
Programming Language." In *Automated Deduction — CADE 28*, Lecture Notes in
Artificial Intelligence 12699. Springer, 625–635.
[[link]](https://link.springer.com/chapter/10%2E1007/978-3-030-79876-5_37)

(ref-fox2003)=
Fox, M., and D. Long (2003). "PDDL2.1: An Extension to PDDL for Expressing
Temporal Planning Domains." *Journal of Artificial Intelligence Research* 20,
61–124.
[[link]](https://jair.org/index.php/jair/article/view/10352)

(ref-fritzson1998)=
Fritzson, P., and V. Engelson (1998). "Modelica — A Unified Object-Oriented
Language for System Modeling and Simulation." In *ECOOP '98 — Object-Oriented
Programming*, Lecture Notes in Computer Science 1445. Springer, 67–90.
[[link]](https://link.springer.com/chapter/10%2E1007/BFb0054087)

(ref-gleeson2010)=
Gleeson, P., S. Crook, R. C. Cannon, M. L. Hines, G. O. Billings, et al.
(2010). "NeuroML: A Language for Describing Data Driven Models of Neurons and
Networks with a High Degree of Biological Detail." *PLoS Computational
Biology* 6(6), e1000815.
[[link]](https://hdl.handle.net/10%2E1371/journal.pcbi.1000815)

(ref-goguen1977)=
Goguen, J. A., J. W. Thatcher, E. G. Wagner, and J. B. Wright (1977).
"Initial Algebra Semantics and Continuous Algebras." *Journal of the ACM*
24(1), 68–95.
[[link]](https://dl.acm.org/doi/10%2E1145/321992.321997)

(ref-gruber1993)=
Gruber, T. R. (1993). "A translation approach to portable ontology
specifications." *Knowledge Acquisition* 5(2), 199–220.
[[link]](https://tomgruber.org/writing/ontolingua-kaj-1993.pdf)

(ref-guarino2009)=
Guarino, N., D. Oberle, and S. Staab (2009). "What Is an Ontology?" In S.
Staab and R. Studer (eds.), *Handbook on Ontologies*, 2nd ed. Springer, 1–17.
[[link]](https://iaoa.org/isc2012/docs/Guarino2009_What_is_an_Ontology.pdf)

(ref-gruninger2003)=
Grüninger, M., and C. Menzel (2003). "The Process Specification Language
(PSL): Theory and Applications." *AI Magazine* 24(3), 63–74.
[[link]](https://hdl.handle.net/10%2E1609/aimag.v24i3.1719)

(ref-haas2017)=
Haas, A., A. Rossberg, D. L. Schuff, B. L. Titzer, D. Gohman, L. Wagner,
A. Zakai, J. F. Bastien, and M. Holman (2017). "Bringing the Web up to
Speed with WebAssembly." In *PLDI 2017*. ACM, 185–200.
[[link]](https://people.mpi-sws.org/~rossberg/papers/Haas,%20Rossberg,%20Schuff,%20Titzer,%20Gohman,%20Wagner,%20Zakai,%20Bastien,%20Holman%20-%20Bringing%20the%20Web%20up%20to%20Speed%20with%20WebAssembly%20%5BDraft%5D.pdf)

(ref-harel2004)=
Harel, D., and B. Rumpe (2004). "Meaningful modeling: what's the semantics of
'semantics'?" *Computer* 37(10), 64–72.
[[link]](https://www.se-rwth.de/staff/rumpe/publications20042008/Meaningful-Modeling-Whats-the-Semantics-of-Semantics.pdf)

(ref-hoare1969)=
Hoare, C. A. R. (1969). "An axiomatic basis for computer programming."
*Communications of the ACM* 12(10), 576–580.
[[link]](https://dl.acm.org/doi/10%2E1145/363235.363259)

(ref-hogan2021)=
Hogan, A., E. Blomqvist, M. Cochez, C. d'Amato, G. de Melo, et al. (2021).
"Knowledge Graphs." *ACM Computing Surveys* 54(4), article 71.
[[link]](https://dl.acm.org/doi/10%2E1145/3447772)

(ref-lambek1986)=
Lambek, J., and P. J. Scott (1986). *Introduction to Higher Order Categorical
Logic*. Cambridge University Press.
[[link]](https://www.cambridge.org/us/universitypress/subjects/mathematics/logic-categories-and-sets/introduction-higher-order-categorical-logic)

(ref-milner1997)=
Milner, R., M. Tofte, R. Harper, and D. MacQueen (1997). *The Definition
of Standard ML (Revised)*. MIT Press.

(ref-modelica2023)=
Modelica Association (2023). *Modelica Language Specification*, version 3.6.
[[link]](https://specification.modelica.org/maint/3.6/.)

(ref-noy2019)=
Noy, N., Y. Gao, A. Jain, A. Narayanan, A. Patterson, and J. Taylor (2019).
"Industry-scale knowledge graphs: lessons and challenges." *Communications of
the ACM* 62(8), 36–43.
[[link]](https://cacm.acm.org/practice/industry-scale-knowledge-graphs/)

(ref-plotkin1981)=
Plotkin, G. D. (1981). *A Structural Approach to Operational Semantics*.
Report DAIMI FN-19, Computer Science Department, Aarhus University.

(ref-scott1971)=
Scott, D., and C. Strachey (1971). "Toward a mathematical semantics for
computer languages." *Proceedings of the Symposium on Computers and Automata*,
Polytechnic Institute of Brooklyn, 19–46.
[[link]](https://ncatlab.org/nlab/files/ScottStrachey-MathematicalSemantics.pdf)

(ref-uschold1996)=
Uschold, M., and M. Grüninger (1996). "Ontologies: principles, methods and
applications." *The Knowledge Engineering Review* 11(2), 93–136.
[[link]](https://www.aiai.ed.ac.uk/project/oplan/documents/1996/96-ker-intro-ontologies.pdf)

(ref-owl2012)=
W3C OWL Working Group (2012). *OWL 2 Web Ontology Language Document
Overview*, 2nd ed. W3C Recommendation.
[[link]](https://www.w3.org/TR/owl2-overview/)

(ref-wieland2012)=
Wieland, V., T. Cwik, G. J. Müller, S. Schmidt, and M. Wolters (2012). "A new
comparative approach to macroeconomic modeling and policy analysis." *Journal
of Economic Behavior & Organization* 83(3), 523–541.
[[link]](https://hdl.handle.net/10%2E1016/j.jebo.2012.01.006)
