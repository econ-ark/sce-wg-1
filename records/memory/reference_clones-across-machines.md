---
name: reference_clones-across-machines
description: "Where this repository is cloned on Chris's machines (jhu-dell, ccarroll; none on ccarroll-m5), the symlinked paths that make one clone look like two, and how far behind each was when last checked"
metadata:
  type: reference
---

Checked 2026-10-31 and again 2026-11-12. "Behind" is measured against GitHub `main`.

| machine | clone | paths that reach it | state when last checked |
|---|---|---|---|
| jhu-dell | `/home/shared/github/econ-ark/sce-wg-1` | also `/home/econ-ark/github/econ-ark/sce-wg-1`, since `/home/econ-ark/github` resolves to `/home/shared/github` | clean. Local `main` at `268cd73`, 34 behind `b6c8578` (2026-11-12) |
| ccarroll | `/Volumes/Sync/GitHub/econ-ark/sce-wg-1` | `~/GitHub/econ-ark/sce-wg-1`, and `~/GitHub/ARK/econ-ark/sce-wg-1`, since `ARK/econ-ark` links to `../econ-ark` | clean. `main` at `6d6e3c2`, last fetched 2025-08-12, 60 behind (2026-11-12) |
| ccarroll-m5 | none | none | no clone anywhere under `/Volumes/Sync/GitHub` names `sce-wg` in its remote (2026-11-12) |

- **Same name, different repository:** `/home/shared/github/llorracc/sce-wg-1-dev` on jhu-dell is the fork
  `llorracc/sce-wg-1-dev`. It is public and has its own Claude session and its own records
  (`schemas/records/`). Its `upstream` remote is this repository.
- **Comparing clones:** ccarroll's two paths are one clone. Resolve symlinks (`pwd -P`) before counting.
- **The open plan for bringing them up to date:** [plans/clone-reconciliation.md](../plans/clone-reconciliation.md).
