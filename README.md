# SCE Working Group 1: Language and Formal Semantics

Working Group 1 of the Society for Computational Economics develops formal descriptions of dynamic economic models and the methods used to solve and estimate them. The group was formed at CEF 2026 in Venice and works with [Econ-ARK](https://econ-ark.org) and [QuantEcon](https://quantecon.org).

[Working group website](https://econ-ark.github.io/sce-wg-1/)

## Projects

- **[Project A: The Semantics of Economic Models](https://econ-ark.github.io/sce-wg-1/project-a.html).** Authors write papers developing semantic ontologies for toolkits, methods, and model classes. The papers are intended for a proposed journal special issue.
- **[Project B: A Community Library of Baseline Models](https://quantecon.github.io/community-library/).** The library collects documented implementations of baseline economic models in several toolkits.

Project B is coordinated by Matt McKay and hosted by [QuantEcon](https://quantecon.org).

## Website

GitHub Pages publishes the site through [`.github/workflows/publish.yml`](.github/workflows/publish.yml) after each push to `main`.

- The [landing page](https://econ-ark.github.io/sce-wg-1/) comes from [`docs/index.html`](docs/index.html).
- The [Project A page](https://econ-ark.github.io/sce-wg-1/project-a.html) and [PDF](https://econ-ark.github.io/sce-wg-1/special-issue-proposal.pdf) are generated from [`project-a/special-issue-proposal.md`](project-a/special-issue-proposal.md).

## Building Project A

Edit [`project-a/special-issue-proposal.md`](project-a/special-issue-proposal.md), not the generated HTML or PDF.

```bash
cd tools
npm install
npm run build
```

The build writes `docs/project-a.html` and `docs/special-issue-proposal.pdf`. Use `npm run build:no-pdf` when LaTeX is unavailable.

These outputs are not committed. The deployment workflow builds them and attaches a `site-preview` artifact to pull-request runs.

## Participation

The repository and issue tracker are public. Membership is by invitation. Use the issue tracker for questions or expressions of interest.

## Contacts

- Akshay Shanker
- Matt McKay
