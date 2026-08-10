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
[AWS Database Blog 2026](#ref-aws2026); see the *Semantic Ontologies*
section of the annex).
With semantic ontologies, translating models between toolkits, and even
generating new modeling research, become operations a language model can
carry out and be checked on cheaply, rather than manual recoding.


<!--
Part 1) relate to existing semantic ontologies in economics (ie, bELLMAN project)
Part 2) describe semantic ontologies have been developed, a lot of commonalities, but also some differences. Could lead toa synthesized ontologies for domains of overlap.
-->



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
[GitHub repository](https://github.com/econ-ark/sce-wg-1), to which members of the community can contribute improvements
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

[^mmb]: The nearest precedent in economics, the Macroeconomic Model Data Base
([Wieland et al. 2012](#ref-wieland2012)), compares models under common variables, common shocks,
and a menu of common policy rules while each model keeps its own equations; it
standardizes comparison, not meaning.

```{raw:tex}
\setcounter{secnumdepth}{-1}
```

## References

(ref-aws2026)=
AWS Database Blog (2026). "Build a semantic ontology to power AI assistants on
AWS — Part 1." 14 July 2026. Accessed 29 July 2026.
[[link]](https://aws.amazon.com/blogs/database/build-a-semantic-ontology-to-power-ai-assistants-on-aws-part-1/)

(ref-gleeson2010)=
Gleeson, P., S. Crook, R. C. Cannon, M. L. Hines, G. O. Billings, et al.
(2010). "NeuroML: A Language for Describing Data Driven Models of Neurons and
Networks with a High Degree of Biological Detail." *PLoS Computational
Biology* 6(6), e1000815.
[[link]](https://hdl.handle.net/10%2E1371/journal.pcbi.1000815)

(ref-gruninger2003)=
Grüninger, M., and C. Menzel (2003). "The Process Specification Language
(PSL): Theory and Applications." *AI Magazine* 24(3), 63–74.
[[link]](https://hdl.handle.net/10%2E1609/aimag.v24i3.1719)

(ref-modelica2023)=
Modelica Association (2023). *Modelica Language Specification*, version 3.6.
[[link]](https://specification.modelica.org/maint/3.6/.)

(ref-wieland2012)=
Wieland, V., T. Cwik, G. J. Müller, S. Schmidt, and M. Wolters (2012). "A new
comparative approach to macroeconomic modeling and policy analysis." *Journal
of Economic Behavior & Organization* 83(3), 523–541.
[[link]](https://hdl.handle.net/10%2E1016/j.jebo.2012.01.006)
