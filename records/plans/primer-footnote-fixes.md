# Correct the primer's footnotes on Project Bellman

**Status: PROPOSED 2026-11-09 10:37:46 EST. Awaiting Chris's decision, with no answer as of 2026-11-12.**

The primer `project-a/slides/semantic-ontology-cases/deck.md` was written by Akshay Shanker and Matt McKay. It is
published through Actions as `docs/semantic-ontology-primer.pdf` and as HTML slides. The proposal is a pull request
to them that changes three footnotes and nothing else. The review behind it is in
[findings/2026-11-09_primer-against-bellman-dev](../findings/2026-11-09_primer-against-bellman-dev/README.md).

| slide | the footnote says | proposed |
|---|---|---|
| The ontology: one stage of the buffer-stock model | "Bellman calculus, Stages and perches §1, bellman-ddsl/docs" and "Bellman-SYM and bellman-ddsl are internal Project Bellman documentation, not yet public" | cite the pages on https://bellman.io and drop the "not yet public" clause |
| The stage file against the same three parts | "bellman-ddsl wiki (internal), Υ §1 (the elaborator) and judge §4 (the comparator)" | the wiki on bellman.io, which is public. The runs of `meaning_map_training.compare` stay "internal" |
| The AI reads from the ontology | "`meaning_map_training.compare`: bellman-ddsl (internal)" | "bellman-dev (internal)" |

- **Optional:** add to the run footnotes that the runs were repeated on 9 November 2026 against `bellman-dev`, with
  the same results.
- **Link to bellman.io, not GitHub:** `econ-ark/bellman` still answered 404 without a login on 2026-11-09.
- **Out of scope:** the 2026-10-01 meeting slides, which mention Project Bellman, are a record of that meeting and stay
  as they are.

**Two questions for the authors**, which predate the change of repository and are not part of the fix:
- **"Two judges":** the slide "The AI writes against the ontology" says Matsya "runs the first loop with the
  elaborator and two judges". Matsya's developer guide describes one judge role, applied to two comparisons. That
  page has not changed since 13 October.
- **A missing condition:** the slide "What the ontology checks and makes explicit" says `V[<] = E_{y}(V) + y` is
  refused under `shock-reintroduced`. That is so only when `y` is among the block's listed inputs. Otherwise the
  refusal is under `signature-complete`. The slide "The stage file against the same three parts" states the
  condition. This was equally true on 13 October.
