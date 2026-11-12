---
name: reference_project-bellman-repositories
description: "Project Bellman's names and repositories: bellman-ddsl (older name) became econ-ark/bellman, renamed econ-ark/bellman-dev (private) on 2026-10-31; econ-ark/bellman is now the public export; docs public at bellman.io"
metadata:
  type: reference
---

As checked on 2026-11-09, from the changelog at https://bellman.io and anonymous requests:

| name | what it is | anonymous access on 2026-11-09 |
|---|---|---|
| `bellman-ddsl` | the project's older name, still used in the primer's footnotes | n/a |
| `econ-ark/bellman-dev` | the original repository, renamed on 2026-10-31: the toolkit, the internal folder, Matsya, the comparator package `meaning-map-training`, the team's history | 404 (private) |
| `econ-ark/bellman` | since 2026-10-31, the public export: `packages/bellman`, `asva`, the Workbench, the applications, `docs/`. No internal folder, and no `meaning-map-training` or Matsya | 404 (not yet open) |
| https://bellman.io | the documentation site, including the Bellman-SYM guide, the refusals reference and the wiki | 200 (public) |

- **The jhu-dell clone:** `/home/shared/github/econ-ark/bellman-dev`. Its `public` remote is `econ-ark/bellman`.
- **The 9 November review** ran against `bellman-dev` at `5c82c1a20`, whose parent is `origin/main` `2f11e0ddc`.
  It compared that with `b84a6934d`, the last `main` commit of 13 October 2026.
- **The clone's own `venv/`** could not import `bellman` on 2026-11-09. The review ran in a separate environment,
  with the pinned dependencies listed in the findings README.

Related: [[feedback_use-bellman-dev]].
