/* Builds the Project A page and PDF from project-a/special-issue-proposal.md.
 *
 * The markdown is the source of truth. Akshay edits it; this regenerates both
 * outputs so the published page and the downloadable PDF never drift from it.
 *
 *   cd tools && npm install     (once)
 *   npm run build               (from tools/, or `node tools/build-project-a.mjs` from the root)
 *
 * Produces:
 *   docs/project-a.html               the page, in the shared site chrome
 *   docs/special-issue-proposal.pdf   the same document, typeset via the vendored jtex template
 *
 * This is deliberately a small, replaceable script: it exists so the page can
 * track the markdown while the site's build system is still being chosen, and
 * it is expected to be superseded by that build system.
 */
import { mystParse } from 'myst-parser';
import { mystToHtml } from 'myst-to-html';
import * as yaml from 'js-yaml';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = process.env.WG1_ROOT || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(ROOT, 'project-a/special-issue-proposal.md');
const OUT = path.join(ROOT, 'docs/project-a.html');
const PDF_SRC = path.join(ROOT, 'project-a/special-issue-proposal.pdf');
const PDF_OUT = path.join(ROOT, 'docs/special-issue-proposal.pdf');

/* --- PDF ---------------------------------------------------------------- */
/* myst reads the `exports:` block in the markdown's own frontmatter, which
   points at templates/plain_latex_wide. Skipped with --no-pdf when LaTeX is
   unavailable; the previously built PDF is then copied through unchanged. */
const skipPdf = process.argv.includes('--no-pdf');
if (!skipPdf) {
  /* mystmd is a dependency of this package, so `npm run build` finds it on PATH
     without a global install. A failure here is fatal: letting it through would
     publish a page whose download link points at a stale or missing PDF. */
  try {
    execFileSync('myst', ['build', 'special-issue-proposal.md', '--pdf'],
      { cwd: path.join(ROOT, 'project-a'), stdio: 'inherit' });
  } catch (err) {
    console.error(`\n${SRC}: \`myst build --pdf\` failed — ${err.message}\n` +
      'The PDF needs mystmd (installed with this package) and a LaTeX distribution\n' +
      'providing xelatex with newtx, tcolorbox, nowidow, titlesec, titling, xurl and\n' +
      'enumitem. Use `npm run build:no-pdf` to regenerate only the page.');
    process.exit(1);
  }
}
/* The PDF is generated rather than committed, so on a fresh clone it is absent
   until a full build has run. Under --no-pdf that is expected and the page is
   still worth generating; otherwise the build above should have produced it. */
if (fs.existsSync(PDF_SRC)) {
  fs.copyFileSync(PDF_SRC, PDF_OUT);
} else if (skipPdf) {
  console.warn(`! no PDF at ${path.relative(ROOT, PDF_SRC)} — generating the page without it.\n` +
    '  Run `npm run build` to produce it; CI builds it on every deploy.');
} else {
  console.error(`${SRC}: myst reported success but produced no PDF at ${path.relative(ROOT, PDF_SRC)}.`);
  process.exit(1);
}

/* --- Page --------------------------------------------------------------- */
const raw = fs.readFileSync(SRC, 'utf8');

/* The page's title, subtitle, authors and abstract all come from the frontmatter,
   so a missing or malformed block should say so rather than fail somewhere later. */
const fmBlock = raw.match(/^---\n([\s\S]*?)\n---\n/);
if (!fmBlock) {
  console.error(`${SRC}: no YAML frontmatter block found.\n` +
    'The page needs `title`, `authors` and `abstract` from it. Expected the file to open with:\n' +
    '  ---\n  title: ...\n  ---');
  process.exit(1);
}
let fm;
try {
  fm = yaml.load(fmBlock[1]);
} catch (err) {
  /* A colon-space inside an unquoted scalar is the frontmatter error worth naming,
     because "Main title: Subtitle" is the ordinary shape of a paper's title and
     YAML reads the second colon as a second key. The parser's own message points
     at the column without saying what to do about it. */
  const culprit = fmBlock[1].split('\n')
    .find((l) => /^[a-z_]+:\s+[^"'>|\s][^\n]*:\s/i.test(l));
  console.error(`${SRC}: could not parse the YAML frontmatter — ${err.message}` +
    (culprit
      ? `\n\nThis line contains a second ": ", which YAML reads as another key:\n\n` +
        `  ${culprit.trim()}\n\nQuote the value:\n\n` +
        `  ${culprit.replace(/^([a-z_]+):\s+(.*)$/i, (_, k, v) => `${k}: "${v.replace(/"/g, '\\"')}"`).trim()}\n`
      : ''));
  process.exit(1);
}
for (const key of ['title', 'abstract']) {
  if (!fm?.[key]) { console.error(`${SRC}: frontmatter is missing \`${key}\`.`); process.exit(1); }
}
/* `authors` is already required by the jtex template, so the PDF export fails
   without it; checking here means the page fails the same way rather than
   silently rendering an empty byline. */
if (!Array.isArray(fm.authors) || fm.authors.length === 0 ||
    !fm.authors.every((a) => a && typeof a.name === 'string' && a.name.trim())) {
  console.error(`${SRC}: frontmatter \`authors\` must be a non-empty list of entries with a \`name\`, e.g.\n` +
    '  authors:\n    - name: Ada Lovelace');
  process.exit(1);
}
const ast = mystParse(raw.replace(/^---\n[\s\S]*?\n---\n/, ''));

/* The source is MyST, and three of its constructs have no direct HTML meaning:
   `{raw:tex}` blocks are for the PDF only, `<!-- -->` notes are internal, and
   `(ref-x)=` targets have to become real anchors for the citation links to
   resolve. `:class:` is carried onto the element so the display boxes keep
   their styling. */
(function walk(node) {
  const kids = node.children || [];
  for (let i = 0; i < kids.length; i++) {
    const c = kids[i];
    if (c.type === 'raw' || c.type === 'comment' ||
        (c.type === 'html' && /^\s*<!--/.test(c.value || ''))) { kids.splice(i--, 1); continue; }
    if (c.class) {
      c.data = { ...(c.data || {}),
                 hProperties: { ...(c.data?.hProperties || {}), className: c.class } };
    }
    if (c.type === 'mystTarget' && c.label) {
      kids[i] = { type: 'span', children: [], data: { hProperties: { id: c.label } } };
    }
    walk(c);
  }
})(ast);

/* Raw HTML is deliberately not passed through. It would not survive the LaTeX
   path to the PDF, so allowing it on the web would let the two outputs diverge
   silently; escaped instead, it shows up as visible text and gets noticed. */
const body = mystToHtml(ast);

/* Section nav is derived from the document's own headings, so adding or
   renaming a section in the markdown updates the nav without touching this file. */
const slug = (s) => s.toLowerCase().replace(/[^\w]+/g, '-').replace(/^-|-$/g, '');
const headings = [...body.matchAll(/<h2>([^<]+)<\/h2>/g)].map((m) => m[1]);
const article = body.replace(/<h2>([^<]+)<\/h2>/g, (_, t) => `<h2 id="${slug(t)}">${t}</h2>`);

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const nav = headings.map((h) => `<a href="#${slug(h)}" class="nav-link">${esc(h)}</a>`).join('\n        ');
const authors = (fm.authors || [])
  .map((a) => `<strong style="font-weight:600;">${esc(a.name)}</strong>`)
  .join(' and ');
const abstract = String(fm.abstract || '').trim().replace(/\s*\n\s*/g, ' ');
const summary = abstract.slice(0, 200);

fs.writeFileSync(OUT, `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Project A · ${esc(fm.title)} — SCE WG1</title>
<meta name="description" content="${esc(summary)}">
<meta property="og:title" content="Project A · ${esc(fm.title)}">
<meta property="og:description" content="${esc(summary)}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://econ-ark.github.io/sce-wg-1/project-a.html">
<link rel="canonical" href="https://econ-ark.github.io/sce-wg-1/project-a.html">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='20' fill='%231F476B'/%3E%3Ctext x='50' y='70' font-family='monospace' font-size='48' font-weight='600' fill='%23FFFFFF' text-anchor='middle'%3EW1%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="chrome.css?v=2">
<link rel="stylesheet" href="proposal.css?v=2">
<script>
/* Apply a saved theme override before first paint to avoid a flash of the wrong theme. */
(function(){try{var t=localStorage.getItem('wg1-theme');if(t==='light'||t==='dark')document.documentElement.dataset.omTheme=t;}catch(e){}})();
</script>
<script src="chrome.js" defer></script>
</head>
<body>
<!-- Generated from project-a/special-issue-proposal.md by tools/build-project-a.mjs.
     Edit the markdown, then re-run the script; do not edit this file. -->
<div style="min-height:100vh; background:var(--bg); color:var(--ink);">
  <div style="max-width:1000px; margin:0 auto; padding:0 24px;">

    <nav style="display:flex; align-items:baseline; justify-content:space-between; gap:24px; flex-wrap:wrap; padding:28px 0; border-bottom:1px solid var(--line);">
      <a href="./" class="nav-home">SCE&nbsp;·&nbsp;WG1</a>
      <div style="display:flex; gap:28px; flex-wrap:wrap; align-items:center;">
        ${nav}
        <a href="special-issue-proposal.pdf" class="nav-link-join">PDF</a>
        <button type="button" id="theme-toggle" class="theme-toggle" title="Switch between light and dark" aria-label="Switch between light and dark">
          <svg class="i-light" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.9 1.9M19.1 4.9l-1.8 1.8M6.7 17.3l-1.9 1.9"/></svg>
          <svg class="i-dark" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>
          <span class="sr-only" id="theme-state" aria-live="polite"></span>
        </button>
      </div>
    </nav>

    <header style="padding:72px 0 40px;">
      <p style="margin:0 0 20px; font-family:'IBM Plex Mono',monospace; font-size:13px; letter-spacing:0.08em; text-transform:uppercase; color:var(--accent);">Project A · SCE WG1</p>
      <h1 style="margin:0; font-family:'Newsreader',serif; font-weight:500; font-size:clamp(38px, 5.5vw, 58px); line-height:1.08; letter-spacing:-0.01em; max-width:20ch; text-wrap:pretty;">${esc(fm.title)}</h1>
      <p style="margin:18px 0 0; font-family:'Newsreader',serif; font-size:23px; line-height:1.3; color:var(--muted); text-wrap:pretty;">${esc(fm.subtitle || '')}</p>
      <p style="margin:26px 0 0; font-size:15px;">${authors}</p>
      <p style="margin:10px 0 0; font-family:'IBM Plex Mono',monospace; font-size:12.5px; line-height:1.7; color:var(--muted); text-wrap:pretty;">Working draft · the target journal, guest editors, committed teams and all dates are still being settled</p>
      <div style="display:flex; flex-wrap:wrap; gap:14px 18px; align-items:center; margin-top:28px;">
        <a class="doc-link" href="special-issue-proposal.pdf">Download the proposal (PDF)</a>
        <a href="https://github.com/econ-ark/sce-wg-1/blob/main/project-a/special-issue-proposal.md" class="card-more">Markdown source →</a>
      </div>
    </header>

    <section class="doc-row abstract">
      <div class="doc-label"><h2>Abstract</h2></div>
      <div class="doc-body"><p>${esc(abstract)}</p></div>
    </section>

    <div class="doc-row">
      <aside class="doc-label doc-aside">
        <p class="doc-aside-label" id="contents-label">Contents</p>
        <!-- Labelled so this landmark is distinguishable from the site nav above;
             aria-labelledby reuses the visible heading rather than repeating it. -->
        <nav aria-labelledby="contents-label">
${headings.map((h) => `          <a href="#${slug(h)}">${esc(h)}</a>`).join('\n')}
        </nav>
      </aside>
      <article class="doc-body proposal">
${article}
      </article>
    </div>

    <footer style="display:flex; flex-wrap:wrap; gap:12px 40px; justify-content:space-between; align-items:baseline; padding:44px 0 56px; border-top:1px solid var(--line);">
      <p style="margin:0; font-family:'IBM Plex Mono',monospace; font-size:12.5px; color:var(--muted);">SCE Working Group 1 · Language and Formal Semantics</p>
      <div style="display:flex; flex-wrap:wrap; gap:12px 28px;">
        <a href="./" class="foot-link">Working group</a>
        <a href="https://quantecon.github.io/community-library/" class="foot-link">Project B</a>
        <a href="https://github.com/econ-ark/sce-wg-1" class="foot-link">Group repository</a>
      </div>
    </footer>

  </div>
</div>
</body>
</html>
`);

const refs = (article.match(/id="ref-/g) || []).length;
const links = (article.match(/href="#ref-/g) || []).length;
console.log(`docs/project-a.html      ${headings.length} sections, ${refs} references, ${links} citation links`);
console.log(fs.existsSync(PDF_OUT)
  ? `docs/special-issue-proposal.pdf   ${fs.statSync(PDF_OUT).size} bytes`
  : 'docs/special-issue-proposal.pdf   not built');
