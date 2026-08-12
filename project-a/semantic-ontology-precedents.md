# Semantic Ontologies in Other Computational Sciences

Background notes for [`special-issue-proposal.md`](special-issue-proposal.md).
Not part of the special issue and not published to the site: this is the
evidence behind the proposal's claim that other fields have already solved the
problem we are describing, collected so the claim can be checked rather than
asserted.

The proposal originally supported that claim with a sentence stating that
computer scientists have reached a consensus that verification requires a
semantic ontology. No such consensus exists — verification in computer science
predominantly means model checking, type systems, proof assistants, and
testing, and a referee from that field would say so in a line. What *is* true,
and what these notes document, is narrower and more useful: several
computational sciences independently arrived at the same structural answer, and
each answer is a concrete artifact that can be pointed at.

## The pattern

Every case below separates two things that economics currently leaves fused:

- the **written form** a model takes — a file, a schema, a sequence of calls;
- the **meaning** of the things written in it, stated independently of any
  program that executes them.

The separation is not incidental. In the strongest case (systems biology) it is
institutional: the format and the ontology are maintained by different
processes, on purpose, so that meaning can evolve without breaking syntax. That
is the same split the proposal's research themes call *syntax* and *denotation*.

| Domain | Written form | Separated statement of meaning |
|---|---|---|
| Systems biology | SBML | Systems Biology Ontology (SBO) |
| Physiology | CellML | biophysical annotation, Physiome repository |
| Neuroscience | NeuroML | component-type definitions |
| Physical systems / engineering | Modelica | declarative equation semantics |
| Ecology, agent-based modeling | — | ODD protocol |
| Climate | netCDF | CF conventions' standard names |
| Materials | — | EMMO, in OWL |
| AI planning | PDDL | PDDL2.1 semantics |

## The cases

### Systems biology: SBML and SBO — the closest analogue we have

SBML is an XML-based exchange format for models of biochemical networks. The
Systems Biology Ontology is a set of controlled vocabularies giving the
semantics of model components, and it is **developed separately from SBML** so
the community can evolve the ontology independently of the format. Since SBML
Level 2 Version 2, SBML components carry SBO terms that mark their semantics
unambiguously.

This is not merely an analogue of what the proposal wants. It is the same
architecture, built for the same reason, and running for over twenty years —
including a curated repository of annotated models (BioModels) that stands in
roughly the relation to SBML that Project B's community library stands to our
toolkits. If the proposal cites one precedent in the abstract, this is the one.

### Physiology: CellML and the Physiome Model Repository

CellML is an XML language for representing and exchanging mathematical models
of physiological systems, developed within the Physiome Project. The Physiome
Model Repository hosts curated models with biophysical annotation. Same shape
as SBML/SBO, in an adjacent field, and useful as evidence that the pattern
generalizes rather than being one community's idiosyncrasy.

### Ecology and agent-based modeling: the ODD protocol

ODD (Overview, Design concepts, Details) is the standard protocol for
describing individual-based and agent-based models. It was introduced in 2006
explicitly because such models were difficult to understand and to duplicate
without one, reviewed and updated in 2010, and updated again in 2020, by which
point it had spread from ecology into social simulation.

ODD deserves particular attention for us. The proposal covers agent-based
models and promises to compare them against heterogeneous-agent models, and
ABMs are the class where the map from theory to code is loosest. ODD is a
neighbouring field having already standardized the description of exactly that
class — and it is a *protocol*, not a formal semantics, which makes it a useful
data point for the Methodology section's claim that a domain without a syntax
can still be pinned down.

### Climate: CF conventions and CMIP — the structural precedent

The CF conventions define standard names that fix what each physical quantity
in model output means, so that data from different sources can be identified as
comparable. That semantic layer is what makes CMIP — a recurring, many-team
model intercomparison — possible at all.

This is the closest structural precedent to the special issue itself, and it is
arguably a better one than den Haan, Judd and Juillard: many modeling groups, a
shared semantic standard, and a comparison exercise for which the standard is a
precondition rather than a by-product. Worth raising where the proposal
introduces the closing comparison paper, since it answers the obvious objection
that ontologies of different domains cannot be compared. In climate they are not
compared — they are *shared*, and that is what the comparison rests on.

### Materials: EMMO

The European Materials Modelling Ontology is a foundational ontology for
materials science, expressed in OWL, whose subject matter includes models
themselves. It is relevant less as a precedent for the proposal's argument than
as an example for the Methodology section: it sits at the description-logic rung
of the formalism ladder, and it is an ontology *of models*, not of the entities
a model describes.

### Already in the draft

- **NeuroML** (neuroscience) and **Modelica** (physical systems) — both already
  cited, both correctly placed. Modelica is the closest to Dynare in kind: a
  declarative language where a file states the model rather than a procedure for
  solving it.
- **PDDL2.1** (AI planning) — genuine academic work, worth keeping.
- **The Gene Ontology** — worth keeping, but note it is an ontology of
  biological entities, not of models. It supports "ontologies work in science,"
  not "models need separated semantics."

## What this displaces

Two citations in the current draft are carrying more weight than they can bear:

- **The Process Specification Language.** A NIST standard. Legitimate work,
  published in *AI Magazine*, but manufacturing process specification is not a
  model-exchange standard in the sense the others are, and "manufacturing's PSL"
  leading the list makes the argument look industrial rather than scientific.
  Demote rather than delete.
- **The AWS Database Blog.** Cited three times, including in support of the
  consensus claim. A vendor blog post cannot carry a load-bearing claim in an
  otherwise strong bibliography. It should survive in exactly one place: the
  annex's bottom-up point about reconstructing a conceptual model from a data
  catalog, which is a genuine contrast and for which a blog is adequate support.

## Where each belongs in the proposal

| Item | Destination |
|---|---|
| SBML + SBO | Abstract, and lead the annex's exemplar paragraph |
| CellML, NeuroML, Modelica | Abstract list; annex |
| ODD | Abstract list; annex, near the model-class discussion |
| CF conventions / CMIP | Main text, where the closing comparison is introduced |
| EMMO | Methodology, at the description-logic rung |
| PSL | Demote within the annex list |
| AWS blog | Annex bottom-up paragraph only |

## References

Verified against publisher records in August 2026, in the anchored style the
proposal's bibliography uses, ready to paste.

```
(ref-hucka2003)=
Hucka, M., A. Finney, H. M. Sauro, et al. (2003). "The systems biology markup
language (SBML): a medium for representation and exchange of biochemical
network models." *Bioinformatics* 19(4), 524–531.
[[link]](https://academic.oup.com/bioinformatics/article/19/4/524/218599)

(ref-courtot2011)=
Courtot, M., N. Juty, C. Knüpfer, et al. (2011). "Controlled vocabularies and
semantics in systems biology." *Molecular Systems Biology* 7, 543.
[[link]](https://hdl.handle.net/10.1038%2Fmsb.2011.77)

(ref-yu2011)=
Yu, T., C. M. Lloyd, D. P. Nickerson, et al. (2011). "The Physiome Model
Repository 2." *Bioinformatics* 27(5), 743–744.
[[link]](https://academic.oup.com/bioinformatics/article/27/5/743/262367)

(ref-grimm2006)=
Grimm, V., U. Berger, F. Bastiansen, et al. (2006). "A standard protocol for
describing individual-based and agent-based models." *Ecological Modelling*
198(1–2), 115–126.
[[link]](https://hdl.handle.net/10.1016%2Fj.ecolmodel.2006.04.023)

(ref-grimm2010)=
Grimm, V., U. Berger, D. L. DeAngelis, J. G. Polhill, J. Giske, and S. F.
Railsback (2010). "The ODD protocol: A review and first update." *Ecological
Modelling* 221(23), 2760–2768.
[[link]](https://www.sciencedirect.com/science/article/pii/S030438001000414X)

(ref-grimm2020)=
Grimm, V., S. F. Railsback, C. E. Vincenot, et al. (2020). "The ODD Protocol
for Describing Agent-Based and Other Simulation Models: A Second Update to
Improve Clarity, Replication, and Structural Realism." *Journal of Artificial
Societies and Social Simulation* 23(2), 7.
[[link]](https://www.jasss.org/23/2/7.html)

(ref-hassell2017)=
Hassell, D., J. Gregory, J. Blower, B. N. Lawrence, and K. E. Taylor (2017).
"A data model of the Climate and Forecast metadata conventions (CF-1.6) with a
software implementation (cf-python v2.1)." *Geoscientific Model Development*
10(12), 4619–4646.
[[link]](https://hdl.handle.net/10.5194%2Fgmd-10-4619-2017)
```

**Not yet verified**, and to be pinned down before use: the exact volume and
pages for CellML 2.0 (*Journal of Integrative Bioinformatics*, 2020), and a
citable reference for EMMO, which is a versioned specification rather than a
journal article.
