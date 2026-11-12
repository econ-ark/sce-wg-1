# Bring the clones on jhu-dell, ccarroll and ccarroll-m5 up to date

**Status: PROPOSED 2026-10-31 14:24:55 EDT. Awaiting Chris's decision, with no answer as of 2026-11-12.**

**The request.** Chris, 2026-10-31 14:22:01 EDT: "make sure this repo is up to date with the corresponding repos on
ccarroll and m5; if not, make a plan for econcilation".

**What the check found.** No clone has local commits, a stash or uncommitted work. Each is an ancestor of GitHub
`main`, so every step below is a fast-forward and cannot conflict. The numbers are as of 2026-11-12; see
[[reference_clones-across-machines]].

1. **jhu-dell** (34 behind): `git switch main && git pull --ff-only`. This repository's session made the branch
   `records-first-memorial` from `origin/main` for the 2026-11-12 memorial, so the checkout is on that branch, not
   on `main`.
2. **ccarroll** (60 behind, last fetched 2025-08-12), over ssh:
   `cd ~/GitHub/econ-ark/sce-wg-1 && git fetch --prune && git merge --ff-only origin/main`. The repository is public,
   so the fetch needs no credentials.
3. **ccarroll-m5** (no clone): Chris's choice between cloning to `~/GitHub/econ-ark/sce-wg-1` and leaving m5
   without one.
