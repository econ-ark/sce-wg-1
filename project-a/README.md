# Building Project A

Edit [`special-issue-proposal.md`](special-issue-proposal.md), not the
generated HTML or PDF.

```bash
cd ../tools
npm install
npm run build
```

The build writes `docs/project-a.html` and
`docs/special-issue-proposal.pdf`, paths from the repository root. Use
`npm run build:no-pdf` when LaTeX is unavailable. These outputs are not
committed; the deployment workflow builds them and attaches a
`site-preview` artifact to pull-request runs.

While writing, `./dev` from the repository root serves a live preview
and rebuilds the page as you save; it skips the PDF, so run
`npm run build` when you need one.
