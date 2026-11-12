---
name: feedback_use-bellman-dev
description: "Check anything this repository says about Project Bellman against econ-ark/bellman-dev, not econ-ark/bellman (now only the public export), and on each new use review what changed in bellman-dev since the last one"
metadata:
  type: feedback
---

When this repository's text depends on Project Bellman, check it against `econ-ark/bellman-dev`. Since 2026-10-31,
`econ-ark/bellman` has held only a public export of the toolkit. Before relying on Bellman again, review what changed
in `bellman-dev` since the last use, and decide whether anything here needs revising.

**Why:** Chris's ruling of 2026-11-09 ([rulings/2026-11-09_use-bellman-dev.md](../rulings/2026-11-09_use-bellman-dev.md)).
`bellman-dev` is the old repository, renamed. It keeps the elaborator, the comparator (`meaning-map-training`) and
Matsya, which the primer cites, and the public export leaves out the comparator and Matsya.

**How to apply:**
- Start from the last recorded use. The latest is the review of 9 November 2026, at `bellman-dev` `5c82c1a20`
  ([[reference_project-bellman-repositories]]).
- Rerun `deck_check.py` from that review's findings folder against both versions, and diff the documentation pages
  the primer cites.
- Cite documentation by its page on https://bellman.io, which is public. Cite code by its module, and mark it as
  internal to `bellman-dev`.
