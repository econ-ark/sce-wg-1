# The primer against bellman-dev, 13 October and 9 November 2026

**Question.** Chris ruled on 2026-11-09 that work here should use `bellman-dev`, after checking what changed in it
since its last use ([rulings/2026-11-09_use-bellman-dev.md](../../rulings/2026-11-09_use-bellman-dev.md)). Does
anything in this repository need revising as a result?

**Answer.** The primer needs no substantive revision. Every claim it makes about the elaborator (the program that
checks a stage file and builds its typed object) and the comparator still holds, with the same outcome on both
dates. Three footnotes are out of date: they use the old name `bellman-ddsl` and call documentation "internal" that
is now public. The proposed fix is in [plans/primer-footnote-fixes.md](../../plans/primer-footnote-fixes.md).

## What uses Project Bellman here

No code here imports or installs `bellman`. The ties are all text:
- **The primer:** `project-a/slides/semantic-ontology-cases/deck.md` (case study 3, "Project Bellman"). It cites
  Bellman-SYM's documentation and the internal runs of 13 October 2026 of `elaborate_text`
  (`bellman.factory.elaboration`) and `compare` (`meaning_map_training.compare`).
- **The 2026-10-01 meeting slides and their page:** these mention Project Bellman as a record of that meeting.
- **`project-a/special-issue-proposal.md`:** mentions "the Bellman equation", which has nothing to do with the
  repository.

## Versions compared

- **Baseline:** `b84a6934d`, the last commit on `bellman-dev`'s `main` dated 13 October 2026 (Sydney time). The
  primer records the date of its runs but not the commit, so the baseline is inferred from the date.
- **Current:** `5c82c1a20` on jhu-dell, whose parent is `origin/main` `2f11e0ddc` of 9 November.
- **The gap:** 176 commits on `main` between the two, 860 in all.

## The behavioral check

The primer's stage file appears only as a figure (`assets/stage-file-form.svg`). `deck_check.py` rebuilds it from
Bellman-SYM's documentation example ("A complete stage file", Stages §4) with b and w renamed k and m, as the
primer's footnote describes. It then runs each of the primer's claims against the elaborator, and runs the
comparator on the file and the example. The documentation example is the same at both versions.

| the primer's claim | 13 Oct | 9 Nov |
|---|---|---|
| the stage file constructs | accept | accept |
| `V[<] = E_{y}(V) + y`, with `y` among the block's inputs, is refused under `shock-reintroduced` | refuse, `shock-reintroduced` | the same |
| the same line without `y` among the inputs | refuse, `signature-complete` | the same |
| a continuation value at the decision perch is refused under `field-perch` (two ways of writing it) | refuse, `field-perch` | the same |
| the shock's mean in the transition, `m = R*k + exp(μ_y + σ_y^2/2)`, is accepted | accept | accept |
| a second `β` in the expectation block is accepted | accept | accept |
| the comparator reads the file and the example as one object | `equal`, share 1.0, b→k and w→m | the same |

The output is in [results-2026-11-09.txt](results-2026-11-09.txt). Only the refusal messages' wording changed: the
baseline cites internal design records (for example "AMD-SG-008 §4"), and the current messages do not.

**How it was run** (jhu-dell). `bellman-dev`'s own `venv/` could not import `bellman`, so a separate environment
was used:

```bash
uv venv --python 3.12 venv
uv pip install --python venv/bin/python discopy==1.2.2 jsonschema==4.26.0 lark==1.3.1 numpy==2.3.5 \
    PyYAML==6.0.3 networkx==3.6.1 sympy==1.14.0
D=/home/shared/github/econ-ark/bellman-dev/packages
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$D/bellman:$D/meaning-map-training venv/bin/python -B deck_check.py out/now
git -C /home/shared/github/econ-ark/bellman-dev archive b84a6934d packages | tar -x -C baseline
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=baseline/packages/bellman:baseline/packages/meaning-map-training \
    venv/bin/python -B deck_check.py out/then
```

`git status` in `bellman-dev` was clean before and after the runs.

## The documentation the primer cites

Every section the primer cites still exists under the same heading on both dates:
- Bellman-SYM's Stages (§§1–5), Field equations §5, Perch tagging rules §3, Periods §§2–3 and Trellises §2;
- the refusals reference;
- the wiki's Υ §1 and judge §4;
- the Bellman calculus's Introduction and Stages and perches.

Three of those are unchanged: the Perch tagging rules, the wiki pages and the Bellman calculus pages.
"Shock distributions" (`reference/laws.md`) still states the convention the primer relies on: `LogNormal(μ, σ)`
takes the mean and standard deviation of the logarithm.

The language did change in three ways, none of which the primer uses:
- a marginal value is no longer a field (`!mrgnvl` was retired for derivative terms such as `D_{a}V[>]`);
- the methods file is now a `.bl` file beside the stage file;
- a numerical grid is now a tagged setting.

**Public status on 2026-11-09:**
- https://bellman.io answered 200, including `/Bellman-Sym/reference/refusals/` and `/wiki/judge/`. An unknown path
  answered 404, so those pages are real, not a catch-all.
- `github.com/econ-ark/bellman` and `github.com/econ-ark/bellman-dev` both answered 404 without a login.

## What this establishes, and what it does not

- **It establishes** that the primer's claims about refusals, acceptances and the comparator hold today, with the same
  rules as on 13 October, and that its citations still point at existing sections.
- **Two limits on the evidence:** the stage file was rebuilt from the documentation example rather than taken from the
  primer's source, and the baseline is inferred from the date.
- **Not checked:** the claims in the primer that do not concern Project Bellman, and the rendered PDF and HTML.
- **Pending:** the footnote fix and the two questions for the authors, in
  [plans/primer-footnote-fixes.md](../../plans/primer-footnote-fixes.md).
