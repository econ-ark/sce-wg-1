# Ruling of 2026-11-09: use bellman-dev, not bellman

**Chris's words**, typed at 2026-11-09 10:33:44 EST in another Claude session on jhu-dell (`jd_econ-ark-tools`), which
passed them on to this repository's session at 10:34:05 EST:

> there's been an update: They need to start using bellman-dev instead of bellman, and they need to examine the
> changes to bellman-dev since the last time they used it (as bellman) to determine whether there are implications
> that require revision.

The message went to the sessions for this repository, for the fork `llorracc/sce-wg-1-dev`, for `wg1-buffer-stock`
and for `sce-wg-1_perfforesightcrra`. Before acting on it, this session checked with `claude-relay-check` that he
typed those words himself rather than the relaying session writing them. The check reported "TYPED BY THE USER".

**The background.** On 2026-10-31 the repository `econ-ark/bellman` was renamed `econ-ark/bellman-dev`. It stays
private and keeps everything: the toolkit, its internal folder, the Matsya service (the project's assistant service)
and the team's history. A new `econ-ark/bellman` now holds a public export of the toolkit alone. The documentation
site, https://bellman.io, is public. See [[reference_project-bellman-repositories]].

**What it supersedes, for this repository.** This repository has no code that imports or installs `bellman`. Its one
tie to Project Bellman is the semantic ontology primer (`project-a/slides/semantic-ontology-cases/deck.md`). The
primer cites Bellman-SYM's documentation and reports runs of the elaborator and the comparator on 13 October 2026,
and it names the repository by an older name still, `bellman-ddsl`. From now on, a check of the primer against
Project Bellman reads `bellman-dev`.

**What was done.** This session compared the primer with `bellman-dev` on 9 November against 13 October. Every
behavioral claim still holds. Three footnotes are out of date. See
[findings/2026-11-09_primer-against-bellman-dev](../findings/2026-11-09_primer-against-bellman-dev/README.md).

**What stays open.** Whether to correct the three footnotes, in a pull request to the primer's authors
([plans/primer-footnote-fixes.md](../plans/primer-footnote-fixes.md)).
