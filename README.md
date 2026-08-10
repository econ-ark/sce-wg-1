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

## Writing with a live preview

```bash
./dev
```

That is the whole setup: it installs the build dependencies on first run, serves `docs/` the way GitHub Pages will, opens a browser, rebuilds the page a moment after you save `special-issue-proposal.md`, and reloads the open tab. Editing `docs/chrome.css`, `docs/proposal.css`, `docs/chrome.js` or `docs/index.html` reloads the tab without a rebuild.

It runs from any directory, and steps to the next free port if something already holds 8000, naming what holds it. Options: `--port 8080` to choose one, `--kill` to reclaim the port instead of stepping around it, `--no-open` to leave the browser alone. The underlying server is `tools/dev.mjs`, also reachable as `npm run dev` from `tools/`.

It skips the PDF, since LaTeX costs several seconds against a fraction of one for the page alone; run `npm run build` when you need the PDF. If a rebuild fails, the error appears in the terminal and the tab keeps the last version that built.

Prefer this over opening `docs/project-a.html` from the file system: over `file://` the "SCE · WG1" home link resolves to a directory listing rather than the landing page.

## Participation

The repository and issue tracker are public. Membership is by invitation. Use the issue tracker for questions or expressions of interest.

## Contacts

- Akshay Shanker
- Matt McKay
