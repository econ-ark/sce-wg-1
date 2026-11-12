# Memory of the sce-wg-1 repository

Read this before working here. Each line points to one record; the record holds the substance. Kept in the
repository so that every clone has it. The repository is public, so nothing private goes in it: the pre-commit
guard (`git config core.hooksPath .githooks`) refuses `*.private.md` files and the confidentiality marker.

## Standing rules
- [Use bellman-dev, not bellman](memory/feedback_use-bellman-dev.md) — check anything here about Project Bellman against `econ-ark/bellman-dev`, after reviewing what changed since the last use (last: 9 November 2026)

## Current state
- [Clone reconciliation](plans/clone-reconciliation.md) — PROPOSED 2026-10-31, awaiting Chris: fast-forward jhu-dell (34 behind) and ccarroll (60 behind); m5 has no clone
- [Primer footnote fixes](plans/primer-footnote-fixes.md) — PROPOSED 2026-11-09, awaiting Chris: three footnotes that use `bellman-ddsl` and call public documentation internal; two questions for the authors
- [Deferred follow-ups](deferred.md) — what was put off and what brings it back

## References
- [Project Bellman's repositories](memory/reference_project-bellman-repositories.md) — `bellman-ddsl` → `econ-ark/bellman` → `econ-ark/bellman-dev` (private); `econ-ark/bellman` is now the public export; docs public at bellman.io
- [Clones across machines](memory/reference_clones-across-machines.md) — jhu-dell and ccarroll (one clone under two paths); none on ccarroll-m5; the fork `llorracc/sce-wg-1-dev` is a different repository

## Rulings
- [2026-11-09: use bellman-dev](rulings/2026-11-09_use-bellman-dev.md) — Chris's words, relayed and verified; what it supersedes here

## Findings
- [2026-11-09: the primer against bellman-dev](findings/2026-11-09_primer-against-bellman-dev/README.md) — all of the primer's claims about the elaborator and comparator hold on 13 Oct and 9 Nov; three outdated footnotes

## Journal
- [2026-10-31 to 2026-11-12](journal/2026-11-12_session-record.md) — the clone check, the bellman-dev review, the first memorial
