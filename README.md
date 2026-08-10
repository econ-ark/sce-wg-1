# SCE WG1 — Language and Formal Semantics

Public coordination space for **Working Group 1 (Language and Formal Semantics)** of the Society for Computational Economics, formed at CEF 2026 in Venice. Sponsored by SCE and partnered with [Econ-ARK](https://econ-ark.org) and [QuantEcon](https://quantecon.org).

**Website:** https://econ-ark.github.io/sce-wg-1/

**Co-chairs:** Akshay Shanker and Matt McKay

## What the group does

Structural economics has no standard, shareable representation of a dynamic model together with its computational solution. WG1 works toward economic models that machines can read, manipulate, and verify — a formal account of what a model file *means*, stated by the people who build the toolkits.

The group runs two complementary projects:

| Project | Description |
| --- | --- |
| **A — The Semantics of Economic Models** | Each toolkit team states formally what its model files mean, publishing a per-toolkit paper; building toward a journal special issue. [Project page](https://econ-ark.github.io/sce-wg-1/project-a.html) |
| **B — A Community Library of Baseline Models** | A standardized repository of the community's baseline models in existing notation, with each toolkit's treatment documented side by side. [Community library](https://quantecon.github.io/community-library/) |

Project B grew out of a proposal put to the CEF 2026 pre-conference. It is coordinated by Matt McKay, with QuantEcon hosting and publishing the collection, so its work happens in the community library rather than in this repository.

## The site

GitHub Pages serves the whole site from this repository, built and deployed by [`.github/workflows/publish.yml`](.github/workflows/publish.yml) on every push to `main`:

| Page | What it is | Source |
| --- | --- | --- |
| [`/`](https://econ-ark.github.io/sce-wg-1/) | Working group landing page | [`docs/index.html`](docs/index.html) |
| [`/project-a.html`](https://econ-ark.github.io/sce-wg-1/project-a.html) | The Project A special-issue proposal, as a page | generated from [`project-a/special-issue-proposal.md`](project-a/special-issue-proposal.md) |
| [`/special-issue-proposal.pdf`](https://econ-ark.github.io/sce-wg-1/special-issue-proposal.pdf) | The same proposal, typeset | generated from the same markdown |
| [`/jedc/`](https://econ-ark.github.io/sce-wg-1/jedc/) | The draft JEDC special-issue proposal, as a MyST site | [`jedc-prop/`](jedc-prop/) |

The shared page chrome — [`docs/chrome.css`](docs/chrome.css), [`docs/chrome.js`](docs/chrome.js) (the light/dark toggle) and [`docs/proposal.css`](docs/proposal.css) — is hand-written and published as-is. The MyST site at `/jedc/` has its own theme and its own toggle.

## Project A — one source, two outputs

[`project-a/special-issue-proposal.md`](project-a/special-issue-proposal.md) is the **single source** for both the Project A page and the downloadable PDF. Edit the markdown, never the generated HTML:

```
cd tools && npm install     # once
npm run build               # regenerates the page and the PDF
```

This writes `docs/project-a.html` (the page, in the shared site chrome) and `docs/special-issue-proposal.pdf` (typeset via the vendored jtex template in [`templates/plain_latex_wide/`](templates/plain_latex_wide/)). Use `npm run build:no-pdf` if you don't have a LaTeX distribution installed; the previously built PDF is then reused.

You don't have to run any of this to change the proposal. Both outputs are generated in CI on every deploy, so they are **not committed** — edit the markdown and open a pull request, and the workflow attaches the whole rendered site to the run as a `site-preview` artifact. Building locally is only for a faster preview.

Note that [`templates/plain_latex_wide/`](templates/plain_latex_wide/) and [`jedc-prop/templates/plain_latex_wide/`](jedc-prop/templates/plain_latex_wide/) are two separate vendored copies of the same upstream jtex template, and they have diverged in margins and spacing. A typesetting fix applied to one does not reach the other, and merging them would reflow both PDFs.

## The JEDC proposal

*Semantic Ontologies in Economics* by Christopher Carroll and Akshay Shanker is a MyST project in [`jedc-prop/`](jedc-prop/), published at [`/jedc/`](https://econ-ark.github.io/sce-wg-1/jedc/):

- [Read online](https://econ-ark.github.io/sce-wg-1/jedc/)
- [Proposal (PDF)](https://econ-ark.github.io/sce-wg-1/jedc/JEDC-special-issue-proposal.pdf)
- [Annex: Guidelines for Papers (PDF)](https://econ-ark.github.io/sce-wg-1/jedc/JEDC-annex.pdf)

The prose lives in [`jedc-prop/parts/proposal.md`](jedc-prop/parts/proposal.md) and [`jedc-prop/parts/annex.md`](jedc-prop/parts/annex.md). Unlike Project A's outputs, the two PDFs are committed alongside them and are copied to the site rather than rebuilt.

> **Two copies, for now.** `jedc-prop/` and `project-a/special-issue-proposal.md` are the same document by the same two authors, but they have diverged — different section headings and different prose, and neither is a superset of the other. `jedc-prop/` is the more recently edited copy. Both are published while the co-chairs decide which one is canonical.

## This repository

- Hosts the working group website, built and deployed to GitHub Pages from `main`.
- Acts as the group's public coordination space — use the issue tracker for questions, suggestions, and discussion.

## Joining

The group works in the open, but membership is by invitation from the co-chairs — this keeps the author set coherent across Project A. If you work on the language and semantics of economic models, register your interest via the issue tracker or email the co-chairs.

You do not need to be a member to follow along: this repository and its issue tracker are open to everyone.
