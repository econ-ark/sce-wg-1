/* Development server for the site in docs/.
 *
 * Serves docs/ the way GitHub Pages will, rebuilds the Project A page when its
 * markdown changes, and reloads the open tab when anything it serves changes.
 *
 *   cd tools && npm run dev            (then open http://localhost:8000/)
 *   npm run dev -- --port 8001         (if 8000 is taken)
 *
 * The live-reload script is injected into HTML *responses*, never written to
 * disk: docs/project-a.html on your machine stays byte-identical to the file
 * .github/workflows/publish.yml builds, so nothing dev-only can reach the
 * published site.
 *
 * The PDF is skipped here — xelatex costs ~3s against ~0.4s for the page alone,
 * which is the difference between a rebuild you don't notice and one you wait
 * for. Run `npm run build` when you need the PDF.
 *
 * This is a companion to build-project-a.mjs and inherits its provisionality:
 * whichever build system supersedes that script will bring its own dev server.
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = process.env.WG1_ROOT || path.resolve(HERE, '..');
const DOCS = path.join(ROOT, 'docs');
const SRC = path.join(ROOT, 'project-a');

const portFlag = process.argv.indexOf('--port');
const PORT = Number(portFlag > -1 ? process.argv[portFlag + 1] : process.env.PORT || 8000);

/* Editors save atomically — write a temp file, rename it over the original — so a
   single save arrives as two or three events. These collapse that burst into one
   build. The markdown wait is longer only to stay comfortable under editors
   configured to autosave while typing; under plain save-on-Cmd-S either value
   behaves the same, because the watcher sees writes, not keystrokes. */
const MD_DEBOUNCE = 400;
const ASSET_DEBOUNCE = 150;

/* Written by build-project-a.mjs into the directory we watch. Ignored here so the
   rebuild's own output can't retrigger a reload — the build notifies directly. */
const GENERATED = new Set(['project-a.html', 'special-issue-proposal.pdf']);

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/markdown; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.pdf': 'application/pdf',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
};

/* --- live reload --------------------------------------------------------- */
/* One EventSource per open tab. EventSource reconnects on its own, so restarting
   this server reconnects every tab without touching them. */
const clients = new Set();

/* A failed build leaves the last good page in place, which is the right thing to
   serve but means the tab silently goes stale — you keep reading a page that no
   longer reflects the file you are editing. The error is therefore pushed to the
   browser too, and held so that a tab opened after the failure still learns of
   it. Cleared by the next build that succeeds. */
let lastError = null;

const RELOAD_SNIPPET = `
<script>
/* injected by tools/dev.mjs — not present in the built file */
(function(){
  var ID = '__dev_build_error';
  function clear(){ var el = document.getElementById(ID); if (el) el.remove(); }
  function show(text){
    clear();
    var box = document.createElement('div');
    box.id = ID;
    box.setAttribute('style', [
      'position:fixed', 'inset:auto 0 0 0', 'z-index:2147483647',
      'max-height:55vh', 'overflow:auto', 'margin:0',
      'padding:14px 18px 18px', 'background:#2b0f12', 'color:#ffd7d7',
      'border-top:3px solid #d24b4b', 'font:13px/1.5 ui-monospace,Menlo,monospace',
      'white-space:pre-wrap', 'box-shadow:0 -8px 24px rgba(0,0,0,.35)'
    ].join(';'));
    var head = document.createElement('div');
    head.setAttribute('style', 'font-weight:600;color:#ff9c9c;margin-bottom:8px');
    head.textContent = 'build failed — showing the last page that built (click to dismiss)';
    box.appendChild(head);
    box.appendChild(document.createTextNode(text));
    box.addEventListener('click', clear);
    document.body.appendChild(box);
  }
  try {
    var es = new EventSource('/__dev/reload');
    es.onmessage = function(e){
      var msg; try { msg = JSON.parse(e.data); } catch (err) { return; }
      if (msg.type === 'reload') location.reload();
      else if (msg.type === 'error') show(msg.text);
    };
  } catch (e) {}
})();
</script>
`;

function push(payload) {
  const line = JSON.stringify(payload);
  for (const res of clients) res.write(`data: ${line}\n\n`);
}

function notify() {
  push({ type: 'reload' });
}

/* --- rebuild ------------------------------------------------------------- */
/* A save during a build queues exactly one rerun rather than a build per event,
   so holding down Cmd-S can't outrun the builder. */
let building = false;
let queued = false;

function rebuild() {
  if (building) {
    queued = true;
    return;
  }
  building = true;
  const started = Date.now();
  const child = spawn(process.execPath, [path.join(HERE, 'build-project-a.mjs'), '--no-pdf'], {
    cwd: HERE,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  let out = '';
  let err = '';
  child.stdout.on('data', (d) => { out += d; });
  child.stderr.on('data', (d) => { err += d; });

  child.on('close', (code) => {
    building = false;
    const ms = Date.now() - started;
    if (code === 0) {
      const summary = out.trim().split('\n')[0] || 'rebuilt';
      console.log(`  ${stamp()} ${summary}  (${ms}ms)`);
      lastError = null;
      notify();
    } else {
      /* Deliberately no reload on failure: the tab keeps showing the last page
         that built, which is more useful than a blank or half-written one — but
         it says so on the page, so a stale view is never mistaken for a fresh one. */
      const text = (err || out).trim();
      console.error(`  ${stamp()} build failed — page left at its last good version`);
      process.stderr.write(text + '\n');
      lastError = text;
      push({ type: 'error', text });
    }
    if (queued) {
      queued = false;
      rebuild();
    }
  });
}

function stamp() {
  return new Date().toTimeString().slice(0, 8);
}

function debounce(ms, fn) {
  let timer = null;
  return () => {
    clearTimeout(timer);
    timer = setTimeout(fn, ms);
  };
}

/* --- watchers ------------------------------------------------------------ */
/* Watch the directories, not the files. A watcher bound to a path holds that
   file's identity, and an editor's atomic save replaces it — so a file watcher
   fires once and then goes quiet for the rest of the session. */
const rebuildSoon = debounce(MD_DEBOUNCE, rebuild);
const reloadSoon = debounce(ASSET_DEBOUNCE, notify);

fs.watch(SRC, { recursive: true }, (_event, name) => {
  if (name && name.endsWith('.md')) rebuildSoon();
});

fs.watch(DOCS, { recursive: true }, (_event, name) => {
  if (!name || GENERATED.has(name)) return;
  if (/\.(css|js|html)$/.test(name)) reloadSoon();
});

/* --- static server ------------------------------------------------------- */
const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (url.pathname === '/__dev/reload') {
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-store',
      Connection: 'keep-alive',
    });
    res.write(': connected\n\n');
    res.socket.setTimeout(0);
    clients.add(res);
    /* A tab opened while the build is broken has missed the push that announced
       it, and would otherwise show a stale page with no indication of why. */
    if (lastError) res.write(`data: ${JSON.stringify({ type: 'error', text: lastError })}\n\n`);
    const ping = setInterval(() => res.write(': ping\n\n'), 30000);
    req.on('close', () => {
      clearInterval(ping);
      clients.delete(res);
    });
    return;
  }

  let rel;
  try {
    rel = decodeURIComponent(url.pathname);
  } catch {
    res.writeHead(400).end('bad request');
    return;
  }

  let file = path.resolve(DOCS, '.' + rel);
  if (file !== DOCS && !file.startsWith(DOCS + path.sep)) {
    res.writeHead(403).end('forbidden');
    return;
  }

  let stat = null;
  try {
    stat = fs.statSync(file);
  } catch {
    /* falls through to the 404 below */
  }

  /* `<a href="./">` on every page resolves to the directory — the case that
     silently degrades to a file listing when docs/ is opened over file://. */
  if (stat?.isDirectory()) {
    if (!rel.endsWith('/')) {
      res.writeHead(301, { Location: rel + '/' }).end();
      return;
    }
    file = path.join(file, 'index.html');
    try {
      stat = fs.statSync(file);
    } catch {
      stat = null;
    }
  }

  if (!stat?.isFile()) {
    /* docs/ is this server's root, so the repo-relative path of a file is not its
       URL — and typing the path you edit is the obvious first guess. Catch that
       case by name instead of answering it with a bare "not found". */
    const stripped = rel.replace(/^\/docs\//, '/');
    const misled = stripped !== rel && fs.existsSync(path.resolve(DOCS, '.' + stripped));
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end(`404  ${rel}\n\n` + (misled
      ? `docs/ is this server's root, so it is not part of the URL.\n\n  http://localhost:${PORT}${stripped}\n`
      : `Not in ${path.relative(ROOT, DOCS)}/.\n` +
        (rel.includes('project-a') ? 'Run `npm run build` if the page has never been built here.\n' : '')));
    return;
  }

  const ext = path.extname(file).toLowerCase();
  /* no-store throughout: the stylesheets carry `?v=N` cache busters for the
     published site, and in dev that would hide the edit you just made. */
  const headers = { 'Content-Type': TYPES[ext] || 'application/octet-stream', 'Cache-Control': 'no-store' };

  if (ext === '.html') {
    let html = fs.readFileSync(file, 'utf8');
    html = html.includes('</body>')
      ? html.replace('</body>', `${RELOAD_SNIPPET}</body>`)
      : html + RELOAD_SNIPPET;
    const body = Buffer.from(html, 'utf8');
    res.writeHead(200, { ...headers, 'Content-Length': body.length });
    res.end(req.method === 'HEAD' ? undefined : body);
    return;
  }

  res.writeHead(200, { ...headers, 'Content-Length': stat.size });
  if (req.method === 'HEAD') {
    res.end();
    return;
  }
  fs.createReadStream(file).pipe(res);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`port ${PORT} is already in use.\n` +
      `  See what holds it:  lsof -nP -iTCP:${PORT} -sTCP:LISTEN\n` +
      `  Or use another:     npm run dev -- --port ${PORT + 1}`);
    process.exit(1);
  }
  throw err;
});

server.listen(PORT, () => {
  console.log(`sce-wg-1 dev server`);
  console.log(`  http://localhost:${PORT}/                 the landing page`);
  console.log(`  http://localhost:${PORT}/project-a.html   the proposal`);
  console.log(`\nwatching project-a/*.md and docs/*.{css,js,html} — ^C to stop\n`);
  /* Build once at startup so a fresh clone serves a page rather than a 404. */
  rebuild();
});
