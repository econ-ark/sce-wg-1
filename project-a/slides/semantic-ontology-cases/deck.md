---
marp: true
title: 'Semantic ontologies: primer and case studies'
theme: default
paginate: true
math: katex
footer: 'SCE · WG1'
style: |-
  @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600&family=Newsreader:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

  :root {
    --ark-blue:    #1f476b;
    --ark-gun:     #2c4053;
    --ark-red:     #c41230;
    --ark-orng:    #f05a28;
    --ark-cyan:    #00aeef;
    --ark-fuchsia: #ed217c;
    --ark-green:   #39b54a;
    --ark-yellow:  #fcb040;
    --ark-grey:    #676470;
    --ark-body:    #495057;
    --ark-head:    #212529;
    --ark-bg:      #ffffff;
    --ark-soft:    #f8f9fa;
    --ark-line:    #e9ecef;
    --ark-line-2:  #ced4da;
  }

  section {
    font-family: 'Roboto', system-ui, sans-serif;
    font-weight: 400;
    font-size: 22px;
    line-height: 1.6;
    color: var(--ark-body);
    background: var(--ark-bg);
    padding: 58px 84px 88px 84px;
    justify-content: flex-start;
    place-content: start;
    text-rendering: optimizeLegibility;
    -webkit-font-smoothing: antialiased;
  }
  section::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: var(--ark-blue);
    z-index: 0;
  }
  footer {
    position: absolute;
    bottom: 18px !important;
    left: 76px !important;
    font-size: 11px;
    line-height: 1;
    color: transparent !important;
  }
  footer img.ark-logo-mark {
    height: 32px;
    width: auto;
    opacity: 0.85;
    display: block;
  }
  section::after {
    color: var(--ark-blue);
    font-family: 'Roboto', sans-serif;
    font-size: 12px;
    font-weight: 500;
    bottom: 22px !important;
    right: 84px !important;
    opacity: 0.55;
  }
  h1 {
    font-weight: 500;
    font-size: 38px;
    color: var(--ark-blue);
    margin: 0 0 0.6em 0;
    letter-spacing: -0.01em;
  }
  h2 {
    font-weight: 500;
    font-size: 30px;
    color: var(--ark-blue);
    margin: 0 0 0.8em 0;
    letter-spacing: -0.01em;
    line-height: 1.2;
  }
  h3 {
    font-weight: 500;
    font-size: 22px;
    color: var(--ark-head);
    margin: 0.5em 0 0.55em 0;
  }
  strong { color: var(--ark-head); font-weight: 500; }
  em { color: var(--ark-body); }
  p  { margin: 0 0 0.85em 0; }
  ul, ol { margin: 0.45em 0 1em 0; padding-left: 1.5em; }
  li { margin: 0 0 0.5em 0; }
  li::marker { color: var(--ark-blue); }
  blockquote {
    margin: 1em 0 0.4em 0;
    padding: 0.15em 0 0.15em 0.85em;
    background: transparent;
    border-left: 2px solid var(--ark-line-2);
    color: var(--ark-grey);
    font-style: italic;
    font-size: 18px;
    line-height: 1.55;
  }
  .callout {
    margin: 1em 0;
    padding: 0.75em 1.1em;
    background: var(--ark-soft);
    border-left: 4px solid var(--ark-blue);
    color: var(--ark-body);
    font-style: normal;
    font-size: 20px;
    line-height: 1.5;
  }
  .callout strong { color: var(--ark-blue); font-weight: 500; }
  .alert {
    margin: 1em 0;
    padding: 0.75em 1.1em;
    background: #fdecea;
    border-left: 4px solid var(--ark-red);
    color: var(--ark-body);
    font-style: normal;
    font-size: 20px;
    line-height: 1.5;
  }
  .alert strong { color: var(--ark-red); font-weight: 600; }
  table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    font-size: 18px;
    line-height: 1.45;
    margin: 0.85em 0 1em 0;
    background: transparent;
  }
  th, td {
    padding: 0.45em 0.85em 0.45em 0;
    vertical-align: top;
    border: none;
    border-bottom: 1px solid var(--ark-line);
    color: var(--ark-body) !important;
    background: transparent !important;
    overflow-wrap: break-word;
    text-align: left;
  }
  th {
    color: var(--ark-blue) !important;
    font-weight: 500;
    font-size: 15px;
    letter-spacing: 0;
    text-transform: none;
    border-bottom: 2px solid var(--ark-blue);
  }
  tbody tr:last-child td { border-bottom: none; }
  pre, code {
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: 15px;
  }
  pre {
    background: var(--ark-soft);
    border: none;
    border-left: 3px solid var(--ark-blue);
    color: var(--ark-body);
    margin: 0.6em 0 0.9em 0;
    padding: 0.75em 1em;
    line-height: 1.45;
    border-radius: 0;
  }
  code { color: var(--ark-blue); background: transparent; }
  pre code { color: var(--ark-body); }
  .katex-display { margin: 0.65em 0 !important; }
  .small { font-size: 17px; line-height: 1.55; }
  .tiny  { font-size: 14px; line-height: 1.45; }
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5em; align-items: start; }
  .cols > div { min-width: 0; }
  .meaning-key {
    display: grid;
    grid-template-columns: 40% 20% 40%;
    width: 1000px;
    max-width: 100%;
    margin: 0.35em auto 0;
    font-size: 16px;
    line-height: 1.3;
    font-weight: 500;
    color: var(--ark-blue);
    text-align: center;
  }
  .cols pre { font-size: 13px; }
  .cols .katex-display { margin: 0.4em 0 !important; }
  .footnote, .footnote p, .footnote span {
    font-size: 11px !important;
    font-weight: 400 !important;
    color: var(--ark-grey) !important;
    line-height: 1.5 !important;
  }
  .footnote code { font-size: 11px !important; }
  .footnote {
    position: absolute;
    bottom: 22px;
    left: 130px;
    right: 110px;
    text-align: left;
  }
  .center { text-align: center; }
  .hl-pink { background: #fde7f0; border: 1px solid #f48fb1; border-radius: 3px; padding: 0 4px; color: #c2185b; font-weight: 500; }
  .bn { font-family: 'Varela Round', 'Roboto', system-ui, sans-serif; color: #176f78; font-weight: 400; letter-spacing: 0; text-transform: none; }
  section.title .bn { color: #9adbd9; }
  .cmt { color: #9aa0a6; }
  .c-red, .c-red strong, .callout strong.c-red, .alert strong.c-red { color: var(--ark-red); }
  .c-orng, .c-orng strong, .callout strong.c-orng, .alert strong.c-orng { color: var(--ark-orng); }
  .c-cyan, .c-cyan strong, .callout strong.c-cyan, .alert strong.c-cyan { color: var(--ark-cyan); }
  .c-green, .c-green strong, .callout strong.c-green, .alert strong.c-green { color: var(--ark-green); }
  .callout.green { border-left-color: var(--ark-green); }
  .callout.green strong { color: var(--ark-green); }
  .ladder.lg { font-size: 16.5px; }
  .ladder.xl { font-size: 18px; }
  .ladder.wf { font-size: 18px; }
  .ladder.wf .rung .rrole { font-size: 13px; }
  .vis-line { border: 0; border-top: 3px dotted var(--ark-red); margin: 0.9em -40px 0.55em; }
  .sp-s { height: 12px; }
  .sp-m { height: 28px; }
  .sp-l { height: 56px; }
  .sp-xl { height: 120px; }
  .callout.lg { font-size: 22px; }
  .callout.sm { font-size: 16px; line-height: 1.4; }
  pre.sm, .cols pre.sm { font-size: 12px; line-height: 1.38; }
  .eq-legend {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px 14px;
    margin-top: 0.8em;
    font-size: 16px;
  }
  .tag {
    display: inline-block;
    padding: 0.15em 0.55em;
    border-radius: 4px;
    font-weight: 500;
    background: var(--ark-soft);
    border-left: 4px solid var(--ark-blue);
  }
  .choice { border-color: var(--ark-red); color: var(--ark-red); }
  .reward { border-color: var(--ark-orng); color: var(--ark-orng); }
  .expect { border-color: var(--ark-cyan); color: var(--ark-cyan); }
  .trans { border-color: var(--ark-green); color: var(--ark-green); }
  .cont { border-color: var(--ark-fuchsia); color: var(--ark-fuchsia); }
  .disc { border-color: var(--ark-yellow); color: #9b6b00; }
  .val { border-color: var(--ark-blue); color: var(--ark-blue); }
  .flow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 1.1em 0 0.8em 0;
    font-size: 18px;
  }
  .node {
    padding: 0.4em 0.7em;
    border-radius: 6px;
    background: #ffffff;
    border: 2px solid var(--ark-line-2);
    color: var(--ark-head);
    white-space: nowrap;
    line-height: 1.3;
    text-align: center;
    font-size: 16px;
  }
  .node .role { display: block; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ark-grey); margin-bottom: 1px; }
  .node sub { font-size: 0.72em; line-height: 0; }
  .node-cont   { border-color: var(--ark-fuchsia); }
  .node-trans  { border-color: var(--ark-green); }
  .node-expect { border-color: var(--ark-cyan); }
  .node-reward { border-color: var(--ark-orng); }
  .node-choice { border-color: var(--ark-red); }
  .node-val    { border-color: var(--ark-blue); }
  .arrow { color: var(--ark-grey); font-size: 22px; }
  .reasons { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 1.1em 0 0.4em; }
  .reason { position: relative; overflow: hidden; background: #ffffff; border: 1.5px solid var(--ark-blue); border-top: 5px solid var(--ark-blue); border-radius: 0; padding: 0.8em 1.15em 0.9em; box-shadow: 0 2px 0 rgba(31,71,107,0.08); }
  .reason .rn { position: absolute; top: -6px; right: 14px; font-size: 58px; font-weight: 700; line-height: 1; opacity: 0.11; color: var(--ark-blue); }
  .reason .rt { font-size: 20px; font-weight: 500; letter-spacing: 0; margin-bottom: 0.18em; color: var(--ark-blue); }
  .reason .rb { font-size: 17.5px; color: var(--ark-body); line-height: 1.45; }
  .reason.r-blue { border-color: var(--ark-blue); border-top-color: var(--ark-blue); } .reason.r-blue .rn, .reason.r-blue .rt { color: var(--ark-blue); }
  .reason.r-red { border-color: var(--ark-red); border-top-color: var(--ark-red); } .reason.r-red .rn, .reason.r-red .rt { color: var(--ark-red); }
  .reason.r-orng { border-color: var(--ark-orng); border-top-color: var(--ark-orng); } .reason.r-orng .rn, .reason.r-orng .rt { color: var(--ark-orng); }
  .reason.r-cyan { border-color: var(--ark-cyan); border-top-color: var(--ark-cyan); } .reason.r-cyan .rn, .reason.r-cyan .rt { color: var(--ark-cyan); }
  .reason.r-fuchsia { border-color: var(--ark-fuchsia); border-top-color: var(--ark-fuchsia); } .reason.r-fuchsia .rn, .reason.r-fuchsia .rt { color: var(--ark-fuchsia); }
  .reason.r-green { border-color: var(--ark-green); border-top-color: var(--ark-green); } .reason.r-green .rn, .reason.r-green .rt { color: var(--ark-green); }
  .reason.r-yellow { border-color: var(--ark-yellow); border-top-color: var(--ark-yellow); } .reason.r-yellow .rn, .reason.r-yellow .rt { color: #9b6b00; }
  .kicker { font-size: 13px; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--ark-grey); margin: 0 0 0.4em; }
  .sub { font-size: 20px; line-height: 1.4; color: var(--ark-grey); margin: -0.55em 0 1em 0; }
  .sub em { color: var(--ark-grey); }
  .kicker.p1 { color: var(--ark-red); } .kicker.p2 { color: var(--ark-orng); } .kicker.p3 { color: var(--ark-cyan); }
  .ladder { font-size: 15px; }
  .rung { background: var(--ark-soft); border-left: 5px solid var(--ark-line-2); border-radius: 0 4px 4px 0; padding: 0.32em 0.7em; margin: 0 0 6px; line-height: 1.2; color: var(--ark-body); }
  .rung .rrole { display: block; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ark-grey); margin-bottom: 1px; }
  .rung.r-iface { border-left-color: var(--ark-green); }
  .rung.r-impl { border-left-color: var(--ark-orng); }
  .rung.r-artifact { border-left-color: var(--ark-cyan); }
  .rung.r-meaning { border-left-color: var(--ark-blue); } .rung.r-meaning .rrole { color: var(--ark-blue); }
  .rung.r-proof { border-left-color: var(--ark-red); } .rung.r-proof .rrole { color: var(--ark-red); }
  .rrole .pkgname { font-size: 23px; }
  .rung .rrole { margin-bottom: 3px; }
  /* TITLE slide — dark navy gradient, oversized white type (from Slides-intro-17042026). Apply with a local _class: title directive. */
  section.title {
    background: linear-gradient(135deg, #1f476b 0%, #2c4053 100%);
    color: #ffffff;
    padding: 60px 84px 88px 84px;
    justify-content: center;
    place-content: center;
  }
  section.title::before { background: var(--ark-yellow); height: 8px; }
  section.title::after { display: none; }
  section.title h1 {
    color: #ffffff;
    font-family: 'Varela Round', 'Roboto', sans-serif;
    font-size: 64px;
    font-weight: 400;
    line-height: 1.1;
    letter-spacing: -0.015em;
    margin: 0 0 0.4em 0;
    max-width: 86%;
  }
  section.title h2 { color: #cfd8e2; font-weight: 400; font-size: 26px; max-width: 86%; }
  section.title h3 { color: #cfd8e2; font-weight: 400; font-size: 22px; max-width: 86%; }
  section.title strong { color: #ffffff; }
  section.title em { color: #cfd8e2; }
  section.title p, section.title li { color: #cfd8e2; }
  section.title .footnote, section.title .footnote p, section.title .footnote span { color: rgba(255,255,255,0.65) !important; }
  section.title footer img.ark-logo-mark { display: none; }
  /* Title-slide hero logo — color Econ-ARK arrows mark anchored bottom-right (from Slides-intro). */
  .title-hero-logo { position: absolute; bottom: 84px; right: 84px; width: 196px; opacity: 1.0; }
  /* Title-slide eyebrow — orange uppercase kicker echoing the orange top rule; sharp accent on the navy field. */
  section.title .title-eyebrow { font-size: 14px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ark-yellow); margin: 0 0 0.7em 0; }
  section.title .title-authors { font-size: 23px; font-weight: 400; color: #cfe0ee; margin: 0.8em 0 0 0; }
  section.title .title-authors u { text-decoration-thickness: 1px; text-underline-offset: 3px; }
  /* Section divider (_class: divider): navy field, white heading. Subsection divider (_class: divider sub): soft grey field, blue heading, grey line naming the section. */
  section.divider { background: var(--ark-blue); place-content: center; }
  section.roomy { padding-top: 72px; }
  section.roomy h2 { margin-bottom: 1.15em; }
  section.roomy p { margin-bottom: 1.2em; }
  section.roomy li { margin-bottom: 0.75em; }
  section.roomy ul, section.roomy ol { margin: 0.6em 0 1.2em 0; }
  section.roomy table { margin: 1.1em 0 1.2em 0; }
  section.roomy .callout, section.roomy .alert { margin: 1.3em 0; }
  section.roomy .stack > div { padding-bottom: 1.2em !important; }
  section.roomy .sp-m { height: 40px; }
  section.airy { padding-top: 92px; }
  section.airy h2 { margin-bottom: 1.6em; }
  section.airy p { margin-bottom: 1.6em; }
  section.airy li { margin-bottom: 1em; }
  section.airy ul, section.airy ol { margin: 0.8em 0 1.6em 0; }
  section.airy table { margin: 1.4em 0 1.5em 0; }
  section.airy .callout, section.airy .alert { margin: 1.6em 0; }
  section.airy .stack > div { padding-bottom: 1.6em !important; }
  section.airy .sp-m { height: 56px; }
  section.airy2 { padding-top: 112px; }
  section.airy2 h2 { margin-bottom: 2em; }
  section.airy2 p { margin-bottom: 2.1em; }
  section.airy2 li { margin-bottom: 1.3em; }
  section.airy2 ul, section.airy2 ol { margin: 1em 0 2em 0; }
  section.airy2 table { margin: 1.8em 0 1.9em 0; }
  section.airy2 .callout, section.airy2 .alert { margin: 2em 0; }
  section.airy2 .stack > div { padding-bottom: 2.1em !important; }
  section.airy2 .sp-m { height: 72px; }
  section.airy table { font-size: 19px !important; }
  section.airy th, section.airy td { padding-top: 0.6em !important; padding-bottom: 0.6em !important; }
  section.airy2 table { font-size: 20px !important; }
  section.airy2 th, section.airy2 td { padding-top: 0.8em !important; padding-bottom: 0.8em !important; }
  section.divider::before { background: var(--ark-yellow); }
  section.divider::after { color: #ffffff; opacity: 0.7; }
  section.divider h1 { font-size: 44px; line-height: 1.2; max-width: 82%; margin: 0; color: #ffffff; }
  section.divider footer img.ark-logo-mark { display: none; }
  section.divider.sub { background: var(--ark-soft); }
  section.divider.sub::before { background: var(--ark-blue); }
  section.divider.sub::after { color: var(--ark-blue); opacity: 0.55; }
  section.divider.sub h1 { color: var(--ark-blue); }
  section.divider.sub footer img.ark-logo-mark { display: block; }
  section.divider.sub .eyebrow { font-size: 22px; color: var(--ark-grey); margin: 0 0 0.5em 0; }
  /* WG1 brand, from docs/chrome.css and presentations/wg-theme.scss: the site's palette, Source Sans 3 for text, Newsreader for headings, IBM Plex Mono for labels and code, and the SCE · WG1 wordmark in the footer in place of the Econ-ARK logo. These rules follow the ones above and override them. */
  :root { --ark-blue: #1F476B; --ark-body: #57545E; --ark-head: #20262E; --ark-grey: #676470; --ark-bg: #FFFFFF; --ark-soft: #F5F8FA; --ark-line: #E2E8EC; --ark-line-2: #CFD6DC; }
  section { font-family: 'Source Sans 3', system-ui, sans-serif; color: var(--ark-body); }
  section::before { top: 40px; left: 84px; right: 84px; height: 1px; background: var(--ark-blue); }
  h1, h2, h3 { font-family: 'Newsreader', Georgia, serif; color: var(--ark-head); font-weight: 500; }
  h2 { font-size: 34px; line-height: 1.15; }
  strong { font-weight: 600; }
  code, pre, kbd { font-family: 'IBM Plex Mono', ui-monospace, Menlo, monospace; }
  footer { color: var(--ark-blue) !important; font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 12px; font-weight: 500; letter-spacing: 0.06em; bottom: 22px !important; left: 84px !important; }
  section::after { font-family: 'IBM Plex Mono', ui-monospace, monospace; font-weight: 400; opacity: 0.9; color: var(--ark-grey); }
  header { font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 12px; letter-spacing: 0.04em; color: var(--ark-grey); }
  th { font-family: 'IBM Plex Mono', ui-monospace, monospace; font-size: 12px; font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ark-blue) !important; border-bottom: 1px solid var(--ark-blue) !important; }
  td { border-bottom: 1px solid var(--ark-line); }
  .lbl { color: var(--ark-blue); font-weight: 600; }
  .footnote { left: 196px; right: 110px; }
  a, a.c-red, header a { text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 4px; }
  section.title { background: var(--ark-bg); color: var(--ark-head); }
  section.title::before { background: var(--ark-blue); height: 1px; top: 40px; }
  section.title h1 { font-family: 'Newsreader', Georgia, serif; color: var(--ark-head); font-size: 78px; font-weight: 500; line-height: 1.02; letter-spacing: -0.015em; }
  .bn, section.title .bn { font-family: 'Newsreader', Georgia, serif; color: var(--ark-head); }
  section.title h2 { font-family: 'Source Sans 3', system-ui, sans-serif; color: var(--ark-grey); font-size: 30px; }
  section.title .title-eyebrow { font-family: 'Source Sans 3', system-ui, sans-serif; font-size: 20px; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--ark-blue); }
  section.title .title-authors { font-family: 'Newsreader', Georgia, serif; font-size: 30px; color: var(--ark-head); }
  section.title p, section.title li, section.title em { color: var(--ark-body); }
  section.title .footnote, section.title .footnote p, section.title .footnote span { color: var(--ark-grey) !important; }
  section.divider::before { background: rgba(255,255,255,0.4); }
  section.divider h1 { font-family: 'Newsreader', Georgia, serif; font-size: 60px; font-weight: 500; color: #ffffff; }
  section.divider footer { color: rgba(255,255,255,0.85) !important; }
  section.divider.sub::before { background: var(--ark-blue); }
  section.divider.sub h1 { color: var(--ark-blue); }
  section.divider.sub footer { color: var(--ark-blue) !important; }
  section.divider.sub .eyebrow { font-family: 'Source Sans 3', system-ui, sans-serif; font-size: 22px; font-weight: 600; letter-spacing: 0; text-transform: none; color: var(--ark-blue); margin: 0 0 0.7em 0; }
---

<!-- slide 1 · Semantic ontologies -->

<!-- _class: title -->
<!-- _paginate: false -->

<p class="title-eyebrow">SCE Working Group 1 &middot; Project A &middot; October 2026</p>

# <span class="bn">Semantic ontologies</span>

## Primer for SCE WG1

<p class="title-authors"><u> Matt McKay & Akshay Shanker</u></p>


---

<!-- slide 2 · Communicating with AI -->
<!-- _class: airy2 -->

## Communicating with AI

<span class="lbl">AI.</span> AI can now write code, solve hard mathematical problems and translate papers into code.

<span class="lbl">Humans.</span> We need a shared structure for what an AI "understands", in order to:
1. **agree on the meaning** of a paper, a model or a model description;
2. **inspect and verify** what the AI produces;
3. **extend** the set of problems the AI can solve.

---

<!-- slide 3 · Semantics ≠ text -->
<!-- _class: airy -->

## Meaning as a relation to a domain

<span class="lbl">Semantics.</span> Meaning is a relation between a piece of text and <span class="c-red">something outside language</span>, its domain.
 
<span class="lbl">Missing meaning.</span> A system trained only on form, such as text, has no way to learn the relation between the text and its meaning (Bender and Koller 2020).

<div class="sp-m"></div>

A large language model fills in the meaning statistically, from regularities in its training text, with no explicit structure that a reader can inspect.

<div class="footnote">Bender and Koller (2020), <a href="https://aclanthology.org/2020.acl-main.463/">“Climbing towards NLU”</a>, ACL.</div>


---

<!-- slide 4 · Semantic ontology -->
<!-- _class: airy2 -->

## Semantic ontology

Knowing what each symbol refers to is not enough.

<span class="lbl">Ontology.</span> To understand a statement, we also need the relations between objects of different kinds.

<span class="lbl">Semantic ontology.</span> **A semantic ontology is a machine-readable account of <span class="c-red">objects</span>, the <span class="c-red">kinds</span> they belong to and the valid relations between them.**

<span class="c-red">Signatures</span> state the types of a relation's arguments and the input and output types of an operation.

---

<!-- slide 5 · Three parts to a semantic ontology -->
<!-- _class: roomy -->

<style scoped>
.stack > div { padding: 0 0 0.8em 0; font-size: 21px; line-height: 1.5; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.katex-display { margin: 0.2em 0 1em 0 !important; font-size: 1.05em; }
</style>

## Three parts to a semantic ontology

$$
\text{written form}\ \xrightarrow{\quad\Upsilon\quad}\ \text{domain of meaning}
$$

<div class="stack">
<div>

<span class="lbl">1. The written form.</span> The written form consists of machine-readable symbols, each with a <span class="c-red">type</span> and a <span class="c-red">signature</span>, such as $v : X \to \mathbb{R}$. In this deck a type labels a symbol in the written form, whereas a kind sorts the objects in the domain.

</div>
<div>

<span class="lbl">2. The domain of meaning.</span> The objects we model, such as state spaces, probability laws, value functions and operators, are sorted into <span class="c-red">kinds</span> with relations between them.

</div>
<div>

<span class="lbl">3. The map Υ (upsilon).</span> Υ maps each typed symbol to an object of the matching kind. A program, called the checker in this deck, <span class="c-red">checks</span> that the assigned object has the required kind. For a stage file the checker is the elaborator (slide 24), for an OWL ontology a reasoner (slide 6).

</div>
</div>

<style scoped>
.callout.ai-example {
  max-width: 100%;
  font-size: 18px;
  line-height: 1.4;
  padding: 0.55em 0.8em;
  margin: 0.7em 0 0;
}
</style>

<div class="callout ai-example"><strong>Example from AI training.</strong> Under NVIDIA’s TensorFloat-32 (TF32) mode, a matrix of 32-bit floating-point numbers (<code>float32</code>) can change when multiplied by the identity, because the inputs are rounded before the multiplication. An ontology of the arithmetic would state the <strong>written form</strong> (the declared type and the arithmetic setting), the <strong>domain of meaning</strong> (the machine values and the rounded operations) and <strong>Υ</strong> (which setting the symbols are read under), so that humans and AI tools compute under the same arithmetic assumptions.</div>

<div class="footnote">Harel and Rumpe (2004), "Meaningful modeling: what's the semantics of 'semantics'?", <em>Computer</em> 37(10), 64–72, for the three parts &middot; Bellman calculus, Introduction §1 (bellman-ddsl/docs) &middot; in this deck a type belongs to the written form and a kind to the domain; Guizzardi and Guarino (2024) write "type" for what the deck calls a kind, and keep "kind" for a narrower notion. &middot; <a href="https://docs.pytorch.org/docs/2.14/notes/numerical_accuracy.html">PyTorch, “Numerical accuracy”, TF32 section</a> &middot; Stosic and Micikevicius (NVIDIA, 2021), <a href="https://developer.nvidia.com/blog/accelerating-ai-training-with-tf32-tensor-cores/">“Accelerating AI Training with NVIDIA TF32 Tensor Cores”</a>.</div>


---

<!-- slide 6 · Ways to represent and use an ontology -->

## Ways to represent and use an ontology

Formal mathematics is one way to write an ontology down, though the mathematics as usually written leaves its conventions implicit (slides 19–21). The table lists the forms in use.

<style scoped>
table { font-size: 17px; line-height: 1.35; margin: 0.35em 0 0.5em; }
th:first-child { width: 27%; }
th:nth-child(2) { width: 39%; }
th:nth-child(3) { width: 34%; }
th, td { padding: 0.38em 0.7em 0.38em 0; }
.callout { font-size: 17px; line-height: 1.4; margin: 0.5em 0 0; padding: 0.5em 0.8em; }
table code, .callout code { font-size: 16px; white-space: nowrap; }
.form-note { font-size: 16px; line-height: 1.35; margin: 0.45em 0 0; }
</style>

| Form or use | What it makes explicit | Examples in this deck |
|:---|:---|:---|
| **Typed mathematical theory** | Types, the signatures of operations and the laws they satisfy. | Math-in-the-Middle (slide 9); the Bellman calculus, which Bellman-SYM writes down (slide 23); mathlib, the library of the proof assistant Lean. |
| **Ontology axioms, in OWL** | A checkable statement about classes (OWL’s word for kinds) or named individuals. In OWL, the ontology language of the W3C, the web standards body, `SubClassOf(:Bond :TradableDebtInstrument)` states that every bond is a tradable debt instrument. | FIBO, the finance ontology (slide 43); OntoPlan (slide 13). |
| **Graph** | Object identifiers, their types and the relations between them, each statement a triple of subject, predicate and object, as in RDF, the W3C’s graph model. | OntoPlan’s world model, the facts about a simulated environment stored as RDF triples (slide 13). |
| **Annotations on models or data** | Links from variables or objects to the terms of an ontology. | SemGen’s biological models (slide 9); NVIDIA’s scene objects (slide 8). |

<div class="callout"><strong>What an axiom does.</strong> Given the axiom above and <code>ClassAssertion(:Bond :b)</code>, that b is a bond, a reasoner, the program that draws consequences from axioms, infers <code>ClassAssertion(:TradableDebtInstrument :b)</code>.</div>

<p class="form-note">The forms combine, since OWL axioms and annotations can both be stored as RDF graphs. In every form, Υ interprets the written symbols in the domain of meaning.</p>

<div class="footnote"><a href="https://kwarc.info/people/frabe/Research/ODK_interop_17.pdf">Kohlhase et al. (2017), §§2–3</a> &middot; <a href="https://leanprover-community.github.io/mathlib-overview.html">Lean/mathlib overview</a> &middot; W3C: <a href="https://www.w3.org/TR/owl2-overview/#Ontologies">OWL 2 overview</a> and <a href="https://www.w3.org/TR/rdf11-concepts/#data-model">RDF graph model</a>; <a href="https://www.w3.org/TR/owl2-primer/">OWL 2 Primer, §§3, 4.1–4.2</a> (syntax and inference) &middot; <a href="https://arxiv.org/html/2610.07649v1">Nam et al. (2026), §3.1</a> &middot; <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6499248/">Neal et al. (2019), §2</a> &middot; <a href="https://nvidia-omniverse.github.io/usd-validation-nvidia/specs/capabilities/semantic_labels/capability-semantic_labels.html">NVIDIA, semantic labels</a>. RDF represents statements as subject–predicate–object triples, the predicate naming a relation. The OWL snippets use Functional-Style Syntax, with “:” abbreviating FIBO’s namespace.</div>


---

<!-- slide 7 · The scope depends on the field and the task -->

## The scope depends on the field and the task

<style scoped>
.stack > div { padding: 0 0 0.8em 0; font-size: 21px; line-height: 1.5; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.callout { font-size: 21px; line-height: 1.45; margin-top: 0.9em; }
</style>

<div class="stack">
<div>

**Domains of meaning vary by field.** Examples include genes and biological processes, objects and actions in robotics, and different economic models, methods, data and problems.

</div>
<div>

**One domain can support several ontologies.** In computational economics, separate ontologies may describe Bellman problems, specify the data inputs to estimation, state numerical assumptions in solvers, or define relations among countries, goods and trade flows.

</div>
<div>

**For an economics project.** An ontology can specify value functions and valid compositions of operators; specify the parameter space, data requirements and identifying assumptions of an estimation problem; or link a dataset column to a shared definition of annual consumption per household and its units.

</div>
</div>

<div class="callout"><strong>WG1’s task.</strong> Define the scope for computational economics by deciding which objects, relations and operations our ontologies should describe and which tasks they should support.</div>

<div class="footnote">On choosing an ontology’s domain, purpose and scope: Noy and McGuinness (2001), <a href="https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html"><em>Ontology Development 101</em></a>, §3, Step 1. The computational-economics uses above are illustrative.</div>


---

<!-- slide 8 · Semantic ontologies and formal methods in AI -->

## Semantic ontologies and formal methods in AI

<style scoped>
table { width: 100% !important; table-layout: fixed; font-size: 18px; margin: 0.4em 0 0; }
th:first-child { width: 23%; }
th:nth-child(2) { width: 61%; }
th:nth-child(3) { width: 16%; }
th, td { padding: 0.4em 0.7em 0.4em 0; }
td:last-child { font-size: 14px; line-height: 1.4; }
</style>

| Use | Published finding | Source |
|:---|:---|:---|
| AI training data (NVIDIA) | NVIDIA’s Omniverse simulation platform labels scene objects with identifiers from Wikidata, a public knowledge base, through the semantic-label schema of the OpenUSD scene format. The labels give AI training data its object categories. | <a href="https://nvidia-omniverse.github.io/usd-validation-nvidia/specs/capabilities/semantic_labels/capability-semantic_labels.html">NVIDIA specification</a><br><a href="https://openusd.org/dev/api/usd_semantics_overview.html">OpenUSD schema</a> |
| Robot planning (OntoPlan) | OntoPlan achieved **89% task success**, against **27%** for SayPlan, a comparison system given the same scene facts. | <a href="https://arxiv.org/html/2610.07649v1">Nam et al. (2026)</a><br>NeurIPS (accepted) |
| Robot experience (KnowRob) | The KnowRob knowledge system used an ontology to retrieve grasp poses and forces from recorded robot actions. | <a href="https://www.open-ease.org/papers/beetz18knowrob.pdf">Beetz et al. (2018)</a><br>ICRA |
| AI program translation | Training a code model to emit symbolic expressions for numeric constants, which a rule-based interpreter converts to IEEE-754 values, raised the share of C functions whose generated assembly passed input–output tests from **3.8% to 92.6% on 21,104 functions**. | <a href="https://aclanthology.org/2024.findings-emnlp.55/">Zhang et al. (2024)</a><br>EMNLP Findings |
| AI theorem proving (LeanDojo) | Retrieving existing Lean library results raised proof success from **23.2% to 26.3% on 2,000 theorems** requiring results not used in training. | <a href="https://proceedings.neurips.cc/paper_files/paper/2023/hash/4441469427094f8873d0fecb0c4e1cee-Abstract-Datasets_and_Benchmarks.html">Yang et al. (2023)</a><br>NeurIPS |
| Numerical checking (SMT-LIB) | SMT-LIB, a standard input language for automated reasoners, defines floating-point types, operations and rounding modes, so that a reasoner can check a floating-point computation. | <a href="https://smt-lib.org/papers/BTRW15.pdf">Brain et al. (2015)</a><br>IEEE ARITH |

<div class="footnote">Reported AI gains concern the combined systems described in each paper.</div>


---

<!-- slide 9 · Evidence – shared models and operational uses -->

## Evidence: shared models and operational uses

<style scoped>
table { width: 100% !important; table-layout: fixed; font-size: 17px; margin: 0.4em 0 0; }
th:first-child { width: 23%; }
th:nth-child(2) { width: 61%; }
th:nth-child(3) { width: 16%; }
th, td { padding: 0.34em 0.7em 0.34em 0; }
td:last-child { font-size: 14px; line-height: 1.4; }
</style>

| Use | Published finding | Source |
|:---|:---|:---|
| Factory planning | Software converted an existing factory ontology and machine-operation descriptions into **267 planning actions in about 15 seconds**. | <a href="https://doi.org/10.1016/j.engappai.2023.106727">Malburg et al. (2023)</a><br>Eng. Appl. AI |
| Assembly planning (Ford) | Ford’s deployed assembly-planning AI used an ontology to interpret vehicle-build instructions and to share that knowledge with other applications. | <a href="https://ojs.aaai.org/index.php/AAAI/article/view/19071">Rychtyckyj et al. (2016)</a><br>IAAI |
| Materials data (MDS-Onto) | MDS-Onto defines terms for X-ray and solar-energy measurements, which software uses to generate data templates and machine-readable datasets. | <a href="https://doi.org/10.1038/s41597-025-04938-5">Rajamohan et al. (2025)</a><br>Scientific Data |
| Model composition (SemGen) | SemGen used ontology terms to match variables by biological meaning and combine models in different formats. | <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6499248/">Neal et al. (2019)</a><br>Bioinformatics |
| Arterial-model assembly | SemGen merged semantically annotated bond-graph modules, whose junction laws conserve mass and energy, into an **86-vessel arterial model from three templates**. | <a href="https://doi.org/10.1371/journal.pcbi.1008859">Shahidi et al. (2021)</a><br>PLOS Comput. Biol. |
| Biological inference (GO-CAM) | Gene Ontology uses logical rules to infer additional labels for gene functions and distributes them in standard releases. | <a href="https://doi.org/10.1038/s41588-019-0500-1">Thomas et al. (2019)</a><br>Nature Genetics |
| Mathematical software | A shared mathematical ontology, Math-in-the-Middle, let three computer-algebra systems, SageMath, GAP and Singular, each perform a step of one polynomial calculation. | <a href="https://doi.org/10.1007/978-3-319-72453-9_14">Kohlhase et al. (2017)</a><br>MACIS |

<div class="footnote">Factory conversion reuses an existing ontology. Arterial-model assembly combines semantic annotations with physical constraints.</div>


---

<!-- slide 10 · Case studies (divider) -->

<!-- _class: divider -->

# Case studies


---

<!-- slide 11 · OntoPlan – robot task planning (divider) -->

<!-- _class: divider sub -->

<p class="eyebrow">Case study 1 of 3</p>

# OntoPlan: robot task planning


---

<!-- slide 12 · Motivating example from robotics -->

## Motivating example from robotics

<p class="small">Nam et al. (2026), accepted at NeurIPS 2026.</p>

OntoPlan combines a language model with planning software for indoor robot tasks in symbolic simulation. Its ontology defines object types, relations and inference rules, while a matching action model specifies what each action changes.

<span class="lbl">Illustrative task.</span> Move a toothbrush from a cabinet to another room.

<style scoped>
th:first-child { width: 25%; }
</style>

| Model component | Toothbrush example |
|:---|:---|
| Objects and types | The toothbrush and the cabinet have type **Artifact** (physical object), while the room has type **Space**. |
| Relation | The toothbrush is inside the cabinet. |
| Action effect | After pickup, the toothbrush is held by the robot’s hand and is no longer inside the cabinet. |
| Inference rule | A carried object is in the same room as the robot. |

<div class="callout">The language model and the planning software work from the same objects, types and updated relations.</div>

<div class="footnote">Nam et al. (2026), <a href="https://arxiv.org/html/2610.07649v1">OntoPlan</a>, §3.1 and Appendix A, Table 7. The task illustrates the paper’s state updates.</div>


---

<!-- slide 13 · OntoPlan’s ontology defines object types and rules -->

## OntoPlan’s ontology defines object types and rules

<style scoped>
.ontology-figure { margin: 0; }
.ontology-figure img {
  display: block;
  width: 100%;
  height: 390px;
  object-fit: contain;
}
.ontology-figure figcaption {
  margin-top: 12px;
  font-size: 20px;
  line-height: 1.45;
}
</style>

<figure class="ontology-figure">
<img src="assets/ontoplan-figure2-ontology.png" alt="OntoPlan Figure 2, upper ontology panel: object types at left and symmetry, inverse, transitivity and property-chain rules at right.">
<figcaption><strong>Written form.</strong> The diagram shows type names and logical rules. <strong>Domain of meaning.</strong> The names and rules describe the simulated rooms, robots, objects and relations. <strong>Υ.</strong> It interprets <code>Space</code> as the set of spaces and <code>carries</code> as the relation between a robot and the objects it carries.</figcaption>
</figure>

<div class="footnote">Nam et al. (2026), <a href="https://arxiv.org/html/2610.07649v1">OntoPlan</a>, Figure 2, ontology layer (cropped). The <a href="https://github.com/namhyeongwoo/OntoPlan/blob/main/figures/world_model.png">full figure</a> also shows rooms, objects and their states. Υ is this deck’s notation for interpretation.</div>


---

<!-- slide 14 · Ontology-based planning achieved 89% task success -->
<!-- _class: airy -->

## Ontology-based planning achieved 89% task success

The same study compared three AI planning systems on 150 simulated robot tasks. All used GPT-4o, the same scene facts and the same 16 primitive actions, and their plans were checked against the same preconditions and effects.

| System | Success rate |
|:---|:---|
| OntoPlan | **88.7% (133/150)** |
| SayPlan | 27% |
| DELTA | 13% |

OntoPlan retrieves the relevant facts, constructs the plan and records the consequences of each action. DELTA also had formal action rules and plan-constructing software, which means that formal rules alone do not account for OntoPlan's gain.

<div class="footnote">Nam et al. (2026), <a href="https://arxiv.org/html/2610.07649v1">OntoPlan</a>, §§4–5 and Appendix E. Results evaluate the ontology together with fact retrieval and planning software.</div>


---

<!-- slide 15 · OntoPlan kept AI inputs small as scenes grew -->
<!-- _class: airy2 -->

## OntoPlan kept AI inputs small as scenes grew

Within OntoPlan, the authors compared selecting relevant facts with supplying all scene facts as text.

| Facts supplied to AI | Growth in the largest input |
|:---|:---|
| Relevant facts selected from the ontology | **1.06×** |
| All scene facts supplied as text | **8.13×** |

Task success was 89% with selected facts and 87% with all facts, a difference that was not statistically significant.

<div class="footnote">Nam et al. (2026), <a href="https://arxiv.org/html/2610.07649v1">OntoPlan</a>, Table 6. Ratios compare large with small scenes. Input size counts tokens (text units) in the largest single call per task.</div>


---

<!-- slide 16 · Buffer-stock saving (divider) -->

<!-- _class: divider sub -->

<p class="eyebrow">Case study 2 of 3</p>

# Buffer-stock saving


---

<!-- slide 17 · A mathematical description of a model -->
<!-- _class: roomy -->

## A mathematical description of a model

This case shows that a machine reading a mathematical description of a model misses part of its meaning. Consider an excerpt from a written statement of the buffer-stock saving model:

> Each period the household arrives with assets $k_t$, receives income $y_t$ and earns the gross return $R\,k_t$ on those assets, where $R$ is the gross interest factor. Market resources are then $m_t=R\,k_t+y_t$. Income is i.i.d. with $\log y_t\sim N(\mu_y,\sigma_y^2)$. The household chooses consumption $c_t\in(0,m_t]$, leaving $k_{t+1}=m_t-c_t$, to solve the Bellman equation
> $$v_t(m_t)=\max_{0<c_t\le m_t}\;\Big\{u(c_t)+\beta\,\mathbb{E}_t\,v_{t+1}\big(R\,(m_t-c_t)+y_{t+1}\big)\Big\}.$$
> The right-hand side defines an operator $\mathbb{T}$ with $v_t=\mathbb{T}\,v_{t+1}$, which sends the function $v_{t+1}$ to the function $v_t$, backward from a given terminal value over a finite horizon.

<div class="sp-s"></div>


---

<!-- slide 18 · Context -->
<!-- _class: roomy -->

## Context

<span class="lbl">Implicit context.</span> Economists write code that implements $\mathbb{T}$ from their own understanding of dynamic programming, which the statement leaves implicit.

<div class="sp-m"></div>

By itself, machine reading the statement does not give enough information to build $\mathbb{T}$.
- The difficulty is not one of parsing. A machine parses the statement, that is, splits it by grammar rules alone into a parse tree of its symbols, whereas the tree, with no structure added to its symbols, records nothing of the model's meaning. <a href="#the-parse-tree-of-a-written-statement" class="c-red">See the appendix on parse trees.</a>

- A semantic ontology makes that <span class="c-red">implicit understanding explicit</span>.


---

<!-- slide 19 · The missing-meaning problem -->
<!-- _class: roomy -->

<style scoped>
table { font-size: 16.5px; margin: 0.4em 0 0 0; width: 100% !important; }
th, td { padding: 0.5em 0.8em 0.5em 0; vertical-align: top; }
th:first-child, td:first-child { width: 24%; }
th:nth-child(2), td:nth-child(2) { width: 76%; }
td code { font-size: 14px; }
</style>

## The missing-meaning problem

The tables on this slide and the next two list some of the meaning that a parse of the buffer-stock statement misses.

| Missing meaning | In the buffer-stock statement |
|---|---|
| Variable bindings | The maximisation binds $c_t$, while the expectation binds $y_{t+1}$. The left-hand side binds $m_t$ by defining $v_t$ as a function of $m_t$, which leaves $m_t$ free inside the right-hand side. |
| Parameters | The paper defines $u$, $R$, $\beta$ and the law of $y_{t+1}$ elsewhere, in no fixed place. Of these, only $\beta$ and $R$ are numbers, while $u$ is a function and the law is a probability measure, a difference the statement does not show. |
| Symbol types | The value function $v_t$ maps $\mathbb{R}_{++}$ to $\mathbb{R}$, with $m_t$ a point of its domain. The tree records both symbols but not that $v_{t}(m_{t})$ evaluates a function at a point of a particular type. |
| An equation between functions | For each $m_t$ the Bellman equation equates two numbers. Over all $m_t$ it is one equation between functions, $v_t=\mathbb{T}\,v_{t+1}$, in which $\mathbb{T}$ maps $v_{t+1}$ to $v_t$. |


---

<!-- slide 20 · The missing-meaning problem -->
<!-- _class: airy2 -->

<style scoped>
table { font-size: 16.5px; margin: 0.4em 0 0 0; width: 100% !important; }
th, td { padding: 0.5em 0.8em 0.5em 0; vertical-align: top; }
th:first-child, td:first-child { width: 24%; }
th:nth-child(2), td:nth-child(2) { width: 76%; }
td code { font-size: 14px; }
</style>

## The missing-meaning problem

| Missing meaning | In the buffer-stock statement |
|---|---|
| Whether a symbol is a variable, a function, or a random variable | The symbol $m_t$, defined by $m_t=R\,k_t+y_t$, is i) the path of one household's resources, ii) the function $(k,y)\mapsto Rk+y$ composed inside the operator, and iii) the random variable whose law is the cross-sectional distribution. A paper writes one symbol for all three meanings, whereas code must represent them as three objects of different types with different uses. |
| Shock law | The statement fixes $\log y_t\sim N(\mu_y,\sigma_y^2)$. In the shorter form $y\sim\mathrm{LogNormal}(\mu_y,\sigma_y)$, $\mu_y$ denotes the mean of $\log y$ under one convention and the mean of $y$ under another. |

<div class="footnote">The LogNormal convention: Project Bellman (the authors' project, slide 23), reference page "Shock distributions".</div>


---

<!-- slide 21 · The missing-meaning problem -->
<!-- _class: airy2 -->

<style scoped>
table { font-size: 16.5px; margin: 0.4em 0 0 0; width: 100% !important; }
th, td { padding: 0.5em 0.8em 0.5em 0; vertical-align: top; }
th:first-child, td:first-child { width: 24%; }
th:nth-child(2), td:nth-child(2) { width: 76%; }
td code { font-size: 14px; }
</style>

## The missing-meaning problem

| Missing meaning |In the buffer-stock statement  |
|---|---|
| Implications of timing stated in words | In a model with entry, beyond the excerpt of slide 17, the sentence "A policy shock raises entrants at date $t$" is satisfied by two different models, because the shock may reach the cross-sectional distribution at $t$ or at $t+1$, while nothing in the paper records which one the code computes. |
| What the household knows when it decides | If the return $R_t$ is random, persistent and drawn before the decision, the household's expectation of $R_{t+1}$ depends on whether it observes $R_t$ or only $m_t=R_t\,k_t+y_t$ when it decides. |

<div class="footnote">The timing example: Project A proposal, footnote 1.</div>


---

<!-- slide 22 · Multiple possible parsed meanings -->
<!-- _class: airy -->

<style scoped>
.stack > div { padding: 0 0 0.8em 0; font-size: 21px; line-height: 1.5; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
</style>

## Multiple possible parsed meanings

<div class="stack">
<div>

<span class="lbl">Several readings.</span> One well-formed statement admits two or more readings of its parse tree. <a href="#what-the-expectation-integrates" class="c-red">The appendix</a> gives examples of false agreement, in which two readers accept the same statement and compute different models.

</div>
<div>

<span class="lbl">Human readers.</span> False agreement rarely arises when an economist reads the model. An economist has been taught that $m_t$ in $v(m_t)$ is the point at which $v$ is evaluated, not a path of assets across a population.

</div>
<div>

<span class="lbl">Timing and information.</span> Even so, the timing of events and what the household knows at each decision confuse economists themselves.

</div>
<div>

<span class="lbl">AI readers.</span> When we rely on an AI's statistical reading of the text, we <span class="c-red">cannot be sure</span> that it has read the model correctly, even when its reading appears correct most of the time.

</div>
</div>


---

<!-- slide 23 · The ontology – one stage of the buffer-stock model -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.terms { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.6em; margin: 0.9em 0 0 0; font-size: 18px; line-height: 1.42; }
.terms p { margin: 0; }
.terms code { font-size: 14.5px; }
</style>

## The ontology: one stage of the buffer-stock model

<div class="sub">The stage file, which writes one stage (the decision problem of one period) in Bellman-SYM, the model language of Project Bellman (the authors’ project), is the <strong>written form</strong>. Its <strong>domain of meaning</strong> contains state spaces, probability laws, value functions and operators. <strong>Υ</strong> maps each declaration and block to the mathematical object it denotes.</div>

<div class="center">

![w:1060](assets/stage-file-form.svg)

</div>

<div class="terms">
<div>

<span class="lbl">Perches.</span> A perch is one of the three information sets of the stage: <span class="c-red">arrival</span> `!arvl`, <span class="c-red">decision</span> `!dcsn` and <span class="c-red">continuation</span> `!cntn`.

</div>
<div>

<span class="lbl">Fields.</span> A field is a state or a value declared at a perch together with its set, as in `m : ℝ₊₊ @ !dcsn`. The role tags `!ctrl` and `!vlu` mark a chosen variable and a value.

</div>
<div>

<span class="lbl">Blocks.</span> A block holds the equations between two perches: the transition with the shock, whose law line `y ~ LogNormal(μ_y, σ_y)` declares its distribution, the choice in the `[id=policy]` block, and the expectation.

</div>
</div>

<div class="footnote">Bellman-SYM, Stages §§1–4: the documentation example, whose b and w are written here as the calculus’s k and m (Bellman calculus, Stages and perches §1, bellman-ddsl/docs) &middot; the law line fixes the convention that slide 20 left to a subfield.</div>


---

<!-- slide 24 · What the ontology checks and makes explicit -->

<style scoped>
table { font-size: 16.5px; margin: 0.3em 0 0.9em 0; width: 100% !important; }
th, td { padding: 0.38em 0.8em 0.38em 0; vertical-align: top; }
th:first-child, td:first-child { width: 52%; }
td code { font-size: 13.5px; }
.link { font-size: 18px; line-height: 1.42; margin: 0.6em 0 0 0; }
</style>

## What the ontology checks and makes explicit

<div class="sub">Under Υ (upsilon), each field and block of the file denotes a typed object. The role tag `!vlu` marks a value. The marks `[>]` and `[<]` give the continuation and arrival values, written $v_\succ$ and $v_\prec$ below. $\mathsf{V}$, $\mathsf{V}_\succ$ and $\mathsf{V}_\prec$ denote the spaces of value functions at the decision, continuation and arrival perches. The elaborator, the program that constructs those objects, refuses a line that the types do not admit and names the rule.</div>

| Line in the file | Under Υ it denotes |
|---|---|
| `V[>] : ℝ @ !vlu` at the continuation perch | $v_\succ:\mathbb{R}_+\to\mathbb{R}$, a function of savings, never a number |
| the choice block `[id=cntn_to_dcsn]` with its `[id=policy]` block | $\mathbb{T}_\succ:\mathsf{V}_\succ\to\mathsf{V}$, the choice operator |
| the expectation block `[id=dcsn_to_arvl]` | $\mathbb{T}_\prec:\mathsf{V}\to\mathsf{V}_\prec$, the expectation operator |

| A line that | The elaborator |
|---|---|
| adds the shock outside its own expectation, `V[<] = E_{y}(V) + y` | <span class="c-red">refuses</span> it under `shock-reintroduced`, since $y$ is not known at arrival |
| lists a continuation value at the decision perch | <span class="c-red">refuses</span> it under `field-perch`, since the value is a function of savings |
| puts the mean of the shock in the transition, `m = R*k + exp(μ_y + σ_y^2/2)` | <span class="c-green">accepts</span> it, leaving the different model visible on that line |
| writes a second `β` in the expectation block | <span class="c-green">accepts</span> it, leaving the second `β` visible on its own line |
| would impose a stationary closure $v_{t+1}=v_t$ | has no line for it, since `V[>]` comes from the next period or the terminal value |

<div class="footnote">The reference on refusals, rules shock-reintroduced and field-perch; Bellman-SYM, Field equations §5, Perch tagging rules §3, Periods §§2–3, Trellises §2; the runs of <code>elaborate_text</code> of 13 October 2026.</div>


---

<!-- slide 25 · Pig goes to the library (divider) -->

<!-- _class: divider sub -->

<p class="eyebrow">Case study 3 of 3</p>

# Pig goes to the library


---

<!-- slide 26 · What the pig learned in the library -->

<style scoped>
section { padding-top: 48px; }
h2 { margin-bottom: 0.5em; }
</style>

## What the pig learned in the library

<div class="center">

![h:440](assets/gauld-pigs-guizzardi-guarino-2024-fig1.jpeg)

</div>

<div class="footnote">&copy; Tom Gauld, reproduced in Guizzardi and Guarino (2024), "Explanation, semantics, and ontology", <em>Data &amp; Knowledge Engineering</em> 153, 102325, Figure 1; shown here for discussion within the working group.</div>


---

<!-- slide 27 · The set-theoretic semantics is not enough -->

## The set-theoretic semantics is not enough

What must a reader know to understand the joke?

<span class="lbl">Set-theoretic semantics.</span> A function from each word to a subset of a set $D$ of individuals gives the denotations $\llbracket\mathit{ham}\rrbracket,\ \llbracket\mathit{bacon}\rrbracket,\ \llbracket\mathit{sausages}\rrbracket\subseteq D$, the sets of things each word applies to. Such a mapping, Guizzardi and Guarino (2024) say, "would not do Maurice here any good".

<span class="lbl">Ontology.</span> The kinds and relations the words are about form a separate system, which the paper states as three facts. Ham, bacon and sausage are food products constituted by pork. Pork comes from a pig. Maurice is a pig.
- In the deck's notation: $\mathit{Maurice}:\mathsf{Pig}$, $\ \mathsf{Ham}\sqsubseteq\exists\mathit{constitutedBy}.\mathsf{Pork}$ (every ham is constituted by some pork), $\ \mathsf{Pork}\sqsubseteq\exists\mathit{dependsOn}.\mathsf{Pig}$ (every quantity of pork comes from some pig).
- The library holds these three facts, which a dictionary does not.

<div class="sp-m"></div>

The joke here arises from the system of kinds and relations, <span class="c-red">not from the set-theoretic semantics</span>.

<div class="footnote">Guizzardi and Guarino (2024), "Explanation, semantics, and ontology", <em>Data &amp; Knowledge Engineering</em> 153, 102325, &sect;2.1: the quotation, and the three facts (1)–(3) that understanding the cartoon needs, stated there in words; the symbols are the deck's.</div>


---

<!-- slide 28 · When Maurice learns the ontology -->

<style scoped>
.fig { margin: 0.2em 0 0.4em 0; }
.fig img { width: 100%; display: block; }
p { font-size: 19px; margin: 0 0 0.35em 0; }
</style>

## When Maurice learns the ontology

<div class="fig"><img src="assets/maurice-learns.svg" alt="Above a horizontal line, the words ham, bacon, sausages and Maurice with their set-theoretic denotations and no connection between them. Below the line, the ontology: the kinds Ham, Bacon, Sausage, Pork and Pig, the individual Maurice, and the relations constitutedBy, dependsOn and instantiation, with the path between kinds from Ham through Pork to Pig in red, a green instantiation arrow from Maurice to Pig, and dashed arrows from each word above the line to its entity below it."></div>

Above the line stand the words, the <strong>written form</strong>. Below it stand the kinds, individuals and relations, the <strong>domain of meaning</strong>. The dashed arrows are <strong>Υ</strong>, which assigns each word its meaning. The solid arrows state relations between kinds and do not identify Maurice as the source of any particular ham.

<div class="footnote">Guizzardi and Guarino (2024), &sect;2.1: "Mapping the words 'ham', 'bacon' and 'sausages' to subsets of a semantic domain would not do Maurice here any good"; the three facts (1)&ndash;(3); real-world semantics "maps symbols to the entities (types, relations, objects, events, aspects) that are part of this ontology".</div>


---

<!-- slide 29 · Semantics and Ontology -->

<style scoped>
table { font-size: 14px; margin: 0.3em 0 0 0; width: 100% !important; }
th, td { padding: 0.24em 0.8em 0.24em 0; vertical-align: top; }
th:first-child, td:first-child { width: 22%; }
p, li { font-size: 18.5px; }
.katex { white-space: nowrap; }
p { margin: 0 0 0.4em 0; }
ul { margin: 0 0 0.3em 0; }
li { margin: 0 0 0.05em 0; }
</style>

## Semantics and ontology

<span class="lbl">Semantics.</span> A set-theoretic semantics maps each word to a subset of a set $D$ of individuals, $\llbracket\mathit{ham}\rrbracket\subseteq D$, and nothing more.

<span class="lbl">Ontology.</span> The ontology is a separate system of kinds, individuals and relations, written as typed symbols.
- Kinds: $\mathsf{Pig},\ \mathsf{Pork},\ \mathsf{Ham},\ \mathsf{Bacon},\ \mathsf{Sausage}$. The word $\mathit{ham}$ names the kind $\mathsf{Ham}$, whose instances are the individual hams.
- Individual: $\mathit{Maurice}:\mathsf{Pig}$. A typed symbol pairs a symbol with the kind of what it names. Here the colon is the instantiation relation, which holds between the individual Maurice and the kind $\mathsf{Pig}$.
- Relations: $\mathit{constitutedBy}$, a relation from $\mathsf{Ham}$ to $\mathsf{Pork}$, and $\mathit{dependsOn}$, a relation from $\mathsf{Pork}$ to $\mathsf{Pig}$. Each holds between individuals of its two kinds and is not a function from one kind to the other. The kind-level facts $\mathsf{Ham}\sqsubseteq\exists\mathit{constitutedBy}.\mathsf{Pork}$ and $\mathsf{Pork}\sqsubseteq\exists\mathit{dependsOn}.\mathsf{Pig}$ say that every ham is constituted by some pork and that every quantity of pork comes from some pig.

| | The pigs | The buffer-stock model |
|---|---|---|
| Written form | $\mathit{ham},\ \mathit{bacon},\ \mathit{sausages}$ | $m,\ y,\ \mathbb{E},\ v,\ \mathbb{T}$ in the Bellman equation |
| Semantics, $\llbracket\cdot\rrbracket$ into a set | $\llbracket\mathit{ham}\rrbracket,\ \llbracket\mathit{bacon}\rrbracket,\ \llbracket\mathit{sausages}\rrbracket\subseteq D$ | $\llbracket\text{Bellman equation}\rrbracket=\mathbb{T}$, some operator |
| Left open | foods for pigs, or foods from pigs | which variable $\max$ chooses and which $\mathbb{E}$ averages over, the space of $v$, the law and timing of $y$ |
| Ontology, typed statements | $\mathit{Maurice}:\mathsf{Pig}$, $\mathsf{Ham}\sqsubseteq\exists\mathit{constitutedBy}.\mathsf{Pork}$, $\mathsf{Pork}\sqsubseteq\exists\mathit{dependsOn}.\mathsf{Pig}$ | $v:\mathbb{R}_{++}\to\mathbb{R}$, $\ y:\mathbb{R}_{++}$ with law $\nu_y$, $\ \mathbb{T}:(\mathbb{R}_{++}\to\mathbb{R})\to(\mathbb{R}_{++}\to\mathbb{R})$ |
| False agreement | two pigs agree that the words name foods, one meaning foods for pigs and the other foods from pigs | two readers accept the Bellman equation and disagree on the timing of the response to a shock (slide 21) |

<div class="footnote">Guizzardi and Guarino (2024), "Explanation, semantics, and ontology", <em>Data &amp; Knowledge Engineering</em> 153, 102325, &sect;2.1 (semantics as a function; an ontology as "a specific theory about the kinds of entity and their ties"; types, individuals and instantiation, where &sect;2.1 writes "the type Pig" for what the deck calls a kind and &sect;3 keeps "kind" for a type whose instances keep their identity; the facts (1) and (2) are stated there in words and written above in the deck's notation), &sect;3.4 (false agreement).</div>


---

<!-- slide 30 · Current modelling tools and AI (divider) -->

<!-- _class: divider -->

<style scoped>
.section-context { color: #cfd8e2; font-size: 24px; line-height: 1.4; margin: 1em 0 0; max-width: 82%; }
</style>

# Current modelling tools and AI

<p class="section-context">Dynare and other tools already turn model descriptions into computed results.</p>


---

<!-- slide 31 · What Dynare and other modelling tools do -->
<!-- _class: roomy -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.6em 0; font-size: 18px; line-height: 1.42; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 14px; }
</style>

## What Dynare and other modelling tools do

<div class="sub">Dynare and Dolo read a model description and apply a numerical method to it, as a program in R or Stata calls a numerical routine. In the figure, the lower route is this computation, carried out in the tool’s own language and modelling rules.</div>

<div class="center">

![w:860](assets/dynare-skip.svg)

</div>

<div class="stack">
<div>

<span class="lbl">With a shared economic interpretation.</span> The upper route states the interpretation separately. Υ maps the written model to a typed model object, ⟦file⟧, to which Ρ (rho) then attaches a numerical method.

</div>
</div>

<div class="footnote">Conceptual routes in this deck’s notation: Υ denotes a separately stated, shared economic interpretation. Compilers can already perform semantic checks. Dynare represents equations separately from solution commands. <a href="https://clang.llvm.org/docs/CommandGuide/clang.html#description">Clang documentation</a> &middot; <a href="https://www.dynare.org/manual/the-model-file.html#model-declaration">Dynare manual</a> &middot; <a href="https://www.econforge.org/dolo.py/">Dolo documentation</a> &middot; Bellman calculus, Introduction §1.</div>


---

<!-- slide 32 · What AI needs beyond code compilation -->
<!-- _class: airy -->

<style scoped>
p { font-size: 21px; line-height: 1.45; }
.stack > div { padding: 0 0 0.8em 0; font-size: 21px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.callout { font-size: 20px; line-height: 1.4; margin-top: 0.9em; padding: 0.65em 0.9em; }
</style>

## What AI needs beyond code compilation

Successful compilation or execution does not establish agreement with the intended economic model.

<div class="stack">
<div>

<span class="lbl">Shared definitions.</span> Give the AI an ontology that specifies the economic objects, their units, timing and relations.

</div>
<div>

<span class="lbl">Links to code.</span> Identify the variables and functions that implement each shared economic definition.

</div>
<div>

<span class="lbl">Checks on model agreement.</span> Check declarations against the ontology, review the links to code, and test the numerical results.

</div>
</div>

<div class="callout"><strong>Example.</strong> Shared definitions distinguish assets chosen today from resources after tomorrow’s income shock, even though both are stored as floating-point numbers.</div>

<div class="footnote">Υ interprets the declared symbols as economic objects. Reviewing their implementation is a separate task. Proposed requirements for AI model generation and translation. Precedent for shared definitions and mappings: <a href="https://kwarc.info/people/frabe/Research/ODK_interop_17.pdf">Kohlhase et al. (2017), MACIS, §§2–5</a>.</div>


---

<!-- slide 33 · The community library (divider) -->

<!-- _class: divider -->

# The community library


---

<!-- slide 34 · One model, several numerical implementations -->
<!-- _class: roomy -->

## One model, several numerical implementations

<style scoped>
p { font-size: 21px; line-height: 1.5; }
table { font-size: 20px; margin: 0.65em 0; }
th:first-child { width: 27%; }
th, td { padding: 0.5em 0.8em 0.5em 0; }
.callout { font-size: 20px; line-height: 1.45; margin-top: 0.8em; }
</style>

QuantEcon’s community library asks each toolkit to implement a shared model and calibration with its own solution method, in a runnable tutorial.

| Part of a contribution | Buffer-stock example |
|:---|:---|
| Common economics | Equations, timing, shock laws, normalisation and calibration. |
| Implementation choices | Solution method, shock approximation, grids, interpolation and software version. |
| Comparison quantities | Consumption, target resources, marginal propensities to consume and the seven model conditions listed in the submission guide. |

<div class="callout">The starting point is the buffer-stock description and the tutorial in the HARK toolkit, submitted as <a href="https://github.com/QuantEcon/community-library/pull/5">pull request #5</a> (a proposed addition to the library’s repository), open with changes requested.</div>

<div class="footnote"><a href="https://quantecon.github.io/community-library/">Community Library</a> &middot; <a href="https://github.com/akshayshanker/community-library/blob/e0452585392965c41f90a98a77a94b185f3501e7/models/buffer-stock/README.md">Buffer-stock submission guide</a>. The result tables, metadata format and tolerances are optional draft conventions. Reporting requirements remain under discussion. Status checked 15 October 2026.</div>


---

<!-- slide 35 · Link toolkit variables to shared model definitions -->
<!-- _class: airy2 -->

## Link toolkit variables to shared model definitions

<style scoped>
table { font-size: 20px; line-height: 1.45; margin: 0.35em 0 0.9em; }
th:first-child { width: 26%; }
th, td { padding: 0.5em 0.8em 0.5em 0; }
p { font-size: 21px; line-height: 1.5; }
</style>

| Published precedent | What was done |
|:---|:---|
| SemGen | Ontology annotations matched biological quantities across different model formats. |
| Math-in-the-Middle | Symbols from SageMath, GAP and Singular were mapped to shared mathematical definitions. |
| BioModels, a curated database of biological models | Curators annotated model entities and reproduced published simulations. |

**Proposed for the library.** Link each implementation’s variables and operations to agreed economic definitions. The links align the written terms. Interpreting those terms as economic objects is what **Υ** does.

<div class="footnote"><a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC6499248/">Neal et al. (2019), <em>Bioinformatics</em>, §§2–5</a> &middot; <a href="https://kwarc.info/people/frabe/Research/ODK_interop_17.pdf">Kohlhase et al. (2017), MACIS, §§2–5</a> &middot; <a href="https://pubmed.ncbi.nlm.nih.gov/31701150/">Malik-Sheriff et al. (2020), <em>Nucleic Acids Research</em></a>. The library extension is proposed; the papers establish the precedents.</div>


---

<!-- slide 36 · Define the quantity before comparing the numbers -->
<!-- _class: roomy -->

## Two estimates of one defined quantity

<style scoped>
p { font-size: 21px; line-height: 1.45; }
table { font-size: 23px; margin: 0.5em 0 0.75em; }
th:first-child { width: 65%; }
th, td { padding: 0.45em 0.8em 0.45em 0; }
.callout { font-size: 20px; line-height: 1.45; margin-top: 0.75em; }
</style>

In the buffer-stock description, **target resources** are the level of resources, measured relative to permanent income, at which expected next-period resources equal current resources.

| Points in the income-shock approximation, besides the zero-income point | Saved HARK estimate of target resources |
|:---|:---|
| 7 | **1.3910** |
| 21 | **1.3994** |

The same model and calibration give different numerical estimates when the shock approximation changes.

<div class="callout"><strong>Proposed extension.</strong> Each result would declare its model version, quantity definition, normalisation and numerical settings. Reviewers would check these declarations against the code and numerical results.</div>

<div class="footnote"><a href="https://github.com/akshayshanker/community-library/blob/e0452585392965c41f90a98a77a94b185f3501e7/projects/HARK/BST/checks/sensitivity.md">Saved HARK sensitivity study, §3</a> &middot; <a href="https://github.com/akshayshanker/community-library/blob/e0452585392965c41f90a98a77a94b185f3501e7/models/buffer-stock/model-description.md">Quantity definition, §1</a>. Both calculations retain the same additional zero-income outcome and asset grid. These are saved estimates, not a new computation.</div>


---

<!-- slide 37 · Use the library to test WG1’s common definitions -->
<!-- _class: airy2 -->

## Use the library to test WG1’s common definitions

<style scoped>
.stack > div { padding: 0 0 0.8em 0; font-size: 21px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.callout { font-size: 20px; line-height: 1.45; margin-top: 0.8em; }
</style>

<div class="stack">
<div>

**Proposed pilot.** Start with the full buffer-stock description and the HARK contribution before adding a second toolkit.

</div>
<div>

**Task.** Ask an AI to identify comparable results and report differences in numerical settings.

</div>
<div>

**Comparison.** Compare the AI’s answers with and without semantic annotations, using the same complete model statement, equations, calibration and run information. Record correct matches, incorrect matches and cases requiring review.

</div>
</div>

<div class="callout">The library supplies the worked examples from which WG1 can decide which definitions and checks to share.</div>

<div class="footnote">Proposed pilot, not an existing library feature. The annotations restate supplied facts. The full buffer-stock model includes permanent and transitory shocks. The earlier Bellman stage illustration is simplified.</div>


---

<!-- slide 38 · Appendix (divider) -->

<!-- _class: divider -->

# Appendix


---

<!-- slide 39 · Further examples (divider) -->

<!-- _class: divider sub -->

<p class="eyebrow">Appendix</p>

# Further examples


---

<!-- slide 40 · Biology – the Gene Ontology -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 15px; }
</style>

## Biology: the Gene Ontology

<div class="meaning-key"><span>Written form</span><span>Map Υ</span><span>Domain of meaning</span></div>

<div class="center">

![w:1000](assets/case-go.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Excludes.</span> The ontology excludes three misreadings. A missing annotation may not be read as the absence of a function, under the open-world assumption, which treats an absent statement as unknown rather than false. A NOT qualifier, which records that a gene lacks a function, may not be read as an inconclusive result. A term may not be read by its name rather than by its definition and relations, since a label must be unique and a definition must always denote the same referents (principles 12 and 19 of the OBO Foundry, the body that sets the rules for biomedical ontologies).

</div>
<div>

<span class="lbl">For economics.</span> A model's object is named by a <span class="c-red">term with a definition and relations</span>, not by a variable name. The role tags `!ctrl` and `!vlu` and the law line of a stage file play that part, as the `sboTerm` of the Systems Biology Ontology does for a rate law in SBML, the exchange format for biochemical models.

</div>
</div>

<div class="footnote">Ashburner et al. (2000), "Gene Ontology: tool for the unification of biology", <em>Nature Genetics</em> 25(1), 25–29 &middot; The Gene Ontology Consortium (2026), "The Gene Ontology knowledgebase in 2026", <em>Nucleic Acids Research</em> 54(D1), D1779–D1792, Table 3 (the release of 22 July 2025) &middot; GAF 2.2 documentation and the human annotation file of 21 May 2026 (geneontology.org); the go-ontology build file, which runs the ELK reasoner &middot; SBO: Courtot et al. (2011), <em>Molecular Systems Biology</em> 7, 543.</div>


---

<!-- slide 41 · Engineering – OntoCAPE, the ontology for chemical process engineering -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 15px; }
</style>

## Engineering: OntoCAPE, the ontology for chemical process engineering

<div class="meaning-key"><span>Written form</span><span>Map Υ</span><span>Domain of meaning</span></div>

<div class="center">

![w:1000](assets/case-ontocape.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Excludes.</span> The ontology excludes a model confused with the system it models and a model variable confused with the physical quantity it stands for. The relation `models` joins a model to its system, while `correspondsToQuantity` pairs a variable with a quantity, as a declared domain excludes the deck's <span class="c-red">function on the wrong space</span> (slide 50).

</div>
<div>

<span class="lbl">For economics.</span> OntoCAPE is the nearest case to Project A because it is an ontology of models themselves. Model variables, equation systems and solution strategies are kinds in its modules (its sub-ontologies), so that a process model and its solver are distinct typed objects, as Υ and Ρ keep a model apart from its numerical method.

</div>
</div>

<div class="footnote">Morbach, Yang and Marquardt (2007), "OntoCAPE—A large-scale ontology for chemical process engineering", <em>Engineering Applications of Artificial Intelligence</em> 20(2), 147–161 &middot; Morbach, Wiesner and Marquardt (2009), <em>Computers &amp; Chemical Engineering</em> 33(10), 1546–1556 &middot; Marquardt, Morbach, Wiesner and Yang (2010), <em>OntoCAPE: A Re-Usable Ontology for Chemical Process Engineering</em>, Springer &middot; the OntoCAPE 2.0 distribution (AVT, RWTH Aachen, GPL): system.owl and mathematical_model.owl; technical reports LPT-2008-25 and LPT-2008-28; Morbach (2009), dissertation, RWTH Aachen, on the RacerPro checks.</div>


---

<!-- slide 42 · Earth science – the SWEET ontologies -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 15px; }
</style>

## Earth science: the SWEET ontologies

<div class="meaning-key"><span>Written form</span><span>Map Υ</span><span>Domain of meaning</span></div>

<div class="center">

![w:1000](assets/case-sweet.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Excludes.</span> The ontology excludes a quantity name read as any of several kinds, since a SWEET class fixes the kind by its definition and by its place among realms (SWEET's divisions of the Earth system), quantities and phenomena. The Climate and Forecast (CF) standard names, published with their canonical units as SKOS concepts (the W3C's format for agreed lists of terms) on the NERC vocabulary server, settle the same question for a variable such as `temp` in a netCDF data file (a format for climate data). In the deck's terms this is the question of <span class="c-red">the shock law</span> (slide 20) and of <span class="c-red">timing stated in words</span> (slide 21).

</div>
<div>

<span class="lbl">For economics.</span> The comparison paper of the special issue that Project A proposes needs a vocabulary of this kind: which object each team reports, a value or a marginal value function, on which state and under which timing, as in the comparison projects that den Haan, Judd and Juillard (2010, 2011) introduced.

</div>
</div>

<div class="footnote">Raskin and Pan (2005), "Knowledge representation in the semantic web for Earth and environmental terminology (SWEET)", <em>Computers &amp; Geosciences</em> 31(9), 1119–1125 &middot; ESIPFed/sweet, release 3.5.0 (14 July 2022), the header of sweetAll.ttl; the class count from the 3.5.0 source &middot; CF standard names: NERC Vocabulary Server, collection P07, version 95 (16 September 2026), publisher Natural Environment Research Council, owner the CF Standard Names Committee &middot; den Haan, Judd and Juillard (2010, 2011), <em>Journal of Economic Dynamics and Control</em> 34(1), 1–3 and 35(2), 175–177.</div>


---

<!-- slide 43 · Finance – FIBO, the Financial Industry Business Ontology -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.6em 0; font-size: 18px; line-height: 1.4; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 15px; }
</style>

## Finance: FIBO, the Financial Industry Business Ontology

<div class="meaning-key"><span>Written form</span><span>Map Υ</span><span>Domain of meaning</span></div>

<div class="center">

![w:920](assets/case-fibo.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Excludes.</span> The ontology excludes an issuer read as the obligor (the party that owes the payments) of a bond and a notional amount read as a principal, since each is a defined class or property (OWL's word for a relation). The 2023 revision of the Swaps ontology separated the nominal from the notional amount, which its change note says "were confused". In the deck's terms these are <span class="c-red">a function on the wrong space</span> (slide 50) and <span class="c-red">the shock law</span> (slide 20).

</div>
<div>

<span class="lbl">For economics.</span> FIBO is finance's own ontology, with the Bureau of Economic Analysis, the Bureau of Labor Statistics, the CFTC and the Office of Financial Research among its contributors. The 2026 rule under the Financial Data Transparency Act records it among the standards that commenters proposed. Project A's ontology names the objects of a model as FIBO names the parties and terms of a contract.

</div>
</div>

<div class="footnote">EDM Council, FIBO (spec.edmcouncil.org/fibo), release Q2 2026 (14 July 2026), MIT licence; the development-process page on consistency; onto-viewer's consistency checker (Openllet and HermiT) &middot; OMG specifications EDMC-FIBO/FND 1.2, BE 1.1, FBC 1.0 and IND 1.0 (2017–2018) &middot; Bennett (2013), "The financial industry business ontology: best practice for big data", <em>Journal of Banking Regulation</em> 14(3–4), 255–268 &middot; Allemang, Garbacz, Grądzki, Kendall and Trypuz (2021), <em>FOIS 2021</em>, 112–126 &middot; Financial Data Transparency Act Joint Data Standards, 91 FR 38246 (25 June 2026) &middot; GoodRelations, the ontology schema.org absorbed in 2012: Hepp (2008), <em>EKAW 2008</em>, LNCS 5268, 329–346.</div>


---

<!-- slide 44 · Knowledge representation – OWL 2, the language ontologies are written in -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 15px; }
</style>

## Knowledge representation: OWL 2, the language ontologies are written in

<div class="meaning-key"><span>Written form</span><span>Map Υ</span><span>Domain of meaning</span></div>

<div class="center">

![w:1000](assets/case-owl.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Excludes.</span> The language excludes any reading of the axioms other than the one fixed by the Direct Semantics, OWL's official rule for what its statements mean, under which "the correct answer to any such question is predetermined by the formal semantics", whatever reasoner computes it (Primer §2). It also forbids reading a missing statement as false and reading two names as two individuals.

</div>
<div>

<span class="lbl">For economics.</span> This is the three-part definition <span class="c-red">in full</span>: classes, properties and individuals as typed symbols, an interpretation as the domain, and a map whose consistency (that the axioms do not contradict one another) and entailments (what follows from them) a reasoner decides. A stage file's Υ plays the part of the Direct Semantics, and the elaborator the part of the reasoner.

</div>
</div>

<div class="footnote">W3C (2012), <em>OWL 2 Web Ontology Language</em>, Recommendations of 11 December 2012: Document Overview §2.3; Direct Semantics §§2.2–2.5; Profiles §§1 and 5; Primer §§2, 4 and 9 &middot; Baader, Calvanese, McGuinness, Nardi and Patel-Schneider (eds.) (2007), <em>The Description Logic Handbook</em>, 2nd ed., Cambridge University Press &middot; HermiT: Glimm, Horrocks, Motik, Stoilos and Wang (2014), <em>Journal of Automated Reasoning</em> 53(3), 245–269; ELK: Kazakov, Krötzsch and Simančík (2014), <em>Journal of Automated Reasoning</em> 53(1), 1–61.</div>


---

<!-- slide 45 · The five reference ontologies against the three parts of a semantic ontology -->

<style scoped>
table { font-size: 16px; margin: 0.3em 0 0 0; width: 100% !important; }
th, td { padding: 0.45em 0.7em 0.45em 0; vertical-align: top; }
th:first-child, td:first-child { width: 15%; }
td code { font-size: 13.5px; }
</style>

## The five reference ontologies against the three parts of a semantic ontology

<div class="sub">Each row places one ontology against the three parts of slide 5, the typed symbols of the written form, the domain of meaning and the map between them, and names in the last column the program that checks the map.</div>

| Ontology | Written form | Domain of meaning | Map Υ | Checker |
|---|---|---|---|---|
| Gene Ontology | the GO terms, each by ID | kinds of molecular function, biological process and cellular component | the term in a GAF annotation | the ELK reasoner on the ontology at every commit |
| OntoCAPE | OWL classes and relations in 62 modules | models, systems, materials and quantities | the axioms, `models` and `hasModelVariable` | the RacerPro reasoner |
| SWEET and the CF names | OWL classes, and SKOS concepts for the CF names | Earth-science quantities, realms and phenomena | the class, or the standard name on a variable | any OWL tool; the CF checker against the NVS table |
| FIBO | OWL classes and properties | contracts, instruments and parties | the class asserted of a record | two OWL 2 reasoners on every release |
| OWL 2 | classes, properties and individuals | an interpretation: a set with relations on it | the Direct Semantics | a reasoner: consistency and entailment |

<div class="footnote">Harel and Rumpe (2004), <em>Computer</em> 37(10), 64–72, for the three parts &middot; the sources of each ontology are on its slide: Ashburner et al. (2000) and the Gene Ontology Consortium (2026); Morbach, Yang and Marquardt (2007); Raskin and Pan (2005) and the NERC Vocabulary Server; the EDM Council and Bennett (2013); W3C (2012).</div>


---

<!-- slide 46 · The stage file against the same three parts -->

<style scoped>
table { font-size: 17px; margin: 0.3em 0 0 0; width: 100% !important; }
th, td { padding: 0.5em 0.8em 0.5em 0; vertical-align: top; }
th:first-child, td:first-child { width: 22%; }
td code { font-size: 14px; }
</style>

## The stage file against the same three parts

<div class="sub">The stage file of slide 23, the deck's own written form, is read here against the columns of the table on slide 45.</div>

| Part | In the Bellman-SYM stage file |
|---|---|
| Written form | the fields and the blocks, each with a type and a perch, and the declared law of the shock (slide 23) |
| Domain of meaning | state spaces, laws, value functions and the operators between them (slide 5) |
| Map Υ | the perch tags `@ !arvl`, `@ !dcsn` and `@ !cntn`, the role tags `!ctrl` and `!vlu` and the law line (slide 23), interpreted by Υ (upsilon), the checked interpretation of slide 48, as the objects of slide 5 |
| Checker | the elaborator (slide 24), which constructs the typed object or refuses the file, naming the rule the file breaks and the line; and the comparator, a program that compares two elaborated files up to renaming and reports, for each kind of item, agreement, difference or an undecided residue, the items it can neither match nor reject |
| Run on the file of slide 23 | The elaborator constructed the object from the file and refused the line `E_{y}(V) + y`, with `y` listed among the block's inputs, under `shock-reintroduced`.<br>The comparator read the file and the documentation example, with b and w for k and m, as one object under that renaming. |

<div class="footnote">Bellman-SYM, Stages §5 (checked interpretation) &middot; bellman-ddsl wiki, Υ §1 (the elaborator) and judge §4 (the comparator) &middot; the runs: <code>elaborate_text</code> of <code>bellman.factory.elaboration</code> and <code>compare</code> of <code>meaning_map_training.compare</code>, 13 October 2026, on the stage file of slide 23 and on Bellman-SYM's documentation example (Stages §4).</div>


---

<!-- slide 47 · The parse tree of a written statement -->
<!-- _class: airy2 -->

<!-- _header: 'Appendix &middot; [return to slide 18](#context)' -->
<style scoped>
.cols { grid-template-columns: 1fr 1fr; gap: 1.6em; align-items: center; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
</style>

## The parse tree of a written statement

Parsing a written statement into a tree, as every compiler first does, shows what the statement leaves to context.

<div class="cols">
<div>

![w:500](assets/parse-tree.svg)

</div>
<div>

<div class="stack">
<div>

<span class="lbl">What the parser does.</span> It splits `v = u(c) + beta * w` into a tree by grammar rules alone.

</div>
<div>

<span class="lbl">What the tree records.</span> The tree records only which symbol is applied to which, node by node.

</div>
<div>

<span class="lbl">What the tree omits.</span> The tree records nothing about what `v`, `c` or `w` are, which variable is bound where, or whether `v` is a function.

</div>
</div>

</div>
</div>

<div class="footnote">The tree is Python's abstract syntax tree, <code>ast.parse("v = u(c) + beta * w")</code>.</div>


---

<!-- slide 48 · From the syntax tree to the semantic graph -->

<!-- _header: 'Appendix &middot; [return to slide 18](#context)' -->
<style scoped>
.cols { grid-template-columns: 1.05fr 1fr; gap: 1.4em; align-items: center; }
.cols .katex-display { margin: 0.2em 0 0.2em 0 !important; font-size: 0.9em; }
.cap { font-size: 18px; line-height: 1.45; margin: 0.4em 0 0 0; }
</style>

## From the parse tree to the semantic graph

In the model, $v$ is not a number obtained by adding $\beta w$ to $u(c)$. That $v_t=\mathbb{T}\,v_{t+1}$ sends a function to a function appears only once the binders, types and declarations on the right are attached to the tree by the dotted lines in the figure, which turn the tree into the semantic graph.

<div class="cols">
<div>

![w:540](assets/binding-graph.svg)

</div>
<div>

$$\begin{aligned}
&\textsf{binders:}&& \max_{c_t}\ \text{binds } c_t,\quad \mathbb{E}_t\ \text{binds } y_{t+1},\\
&&& v_t(m_t)=\cdots\ \ \forall m_t\in\mathbb{R}_{++}\ \text{ binds } m_t\\[4pt]
&\textsf{fixed from outside:}&& u:\mathbb{R}_{++}\to\mathbb{R},\quad \beta,\,R\in\mathbb{R},\\
&&& \nu_y\ \text{the law of } y_{t+1},\ \text{on } \mathbb{R}_{++}\\[4pt]
&\textsf{obtained:}&& v_{t+1}\big(R(m_t-c_t)+y_{t+1}\big):\mathbb{R},\\
&&& \mathbb{T}:(\mathbb{R}_{++}\to\mathbb{R})\to(\mathbb{R}_{++}\to\mathbb{R})
\end{aligned}$$

<div class="cap">The law <em>ν</em><sub><em>y</em></sub> is the probability distribution of the income shock. A semantic ontology states the quantifier over <em>m</em><sub><em>t</em></sub> on the left-hand side, the binder conventions, the types and the declarations of <em>u</em> and <em>ν</em><sub><em>y</em></sub>, none of which the tree records.</div>

</div>
</div>

<div class="footnote">Bellman-SYM, Project Bellman's model language, parses a file into such a tree, builds the semantic graph from it by a checked interpretation, which the calculus calls Υ (upsilon), and discards the tree (Bellman calculus, Introduction §§1–2; Bellman-SYM, Stages §5).</div>


---

<!-- slide 49 · What the expectation integrates -->

<!-- _header: 'Appendix &middot; [return to slide 22](#multiple-possible-parsed-meanings)' -->
<style scoped>
.box { border: 1px solid var(--ark-line-2); border-left: 4px solid var(--ark-blue); border-radius: 4px; background: #ffffff; padding: 0.65em 1.1em 0.6em 1.1em; margin: 0 0 1.1em 0; font-size: 19px; line-height: 1.45; }
.box:last-child { margin-bottom: 0; }
.box .katex-display { margin: 0.35em 0 0.4em 0 !important; }
.box p { margin: 0; }
.sub p { margin: 0; }
</style>

## What the expectation integrates

<div class="sub">

The paper's Bellman equation gives $\mathbb{E}$ the date $t$ as its subscript rather than the variable it integrates. Because the tree specifies neither that variable nor the type of $\mathbb{E}_t$, each box below puts the paper's expression to the left of "read as" and a reading that the tree does not exclude to the right.

</div>

<div class="box">

<span class="lbl">The shock leaves the expectation.</span>
$$\mathbb{E}_t\,v\big(R(m-c)+y'\big)\qquad\text{read as}\qquad v\big(R(m-c)+\mathbb{E}_t\,y'\big)\quad\text{or}\quad \mathbb{E}_t\big[v\big(R(m-c)\big)\big]+y'.$$
Since Jensen's inequality gives $\mathbb{E}_t\,v(R(m-c)+y')\le v(R(m-c)+\mathbb{E}_t\,y')$ for concave $v$, the first reading overstates the continuation value. Because it replaces the income risk by its mean, it also removes the precautionary motive, the saving held against that risk (Kimball 1990). The second reading treats $y'$ as known before it is drawn.

</div>
<div class="box">

<span class="lbl">The expectation moved through the maximisation.</span>
$$\max_c\big\{u(c)+\beta\,\mathbb{E}_t\,v_{t+1}(\cdot)\big\}\qquad\text{read as}\qquad \mathbb{E}_t\max_c\big\{u(c)+\beta\,v_{t+1}(\cdot)\big\}.$$
Since $\mathbb{E}\max\ge\max\mathbb{E}$, the reading on the right overstates the value and lets consumption respond to income that has not yet been drawn.

</div>

<div class="footnote">The precautionary motive: Kimball (1990), "Precautionary saving in the small and in the large", <em>Econometrica</em> 58(1), 53–73. Jensen's inequality is a standard result.</div>


---

<!-- slide 50 · A number for a function, and a function on the wrong space -->
<!-- _class: airy -->

<!-- _header: 'Appendix &middot; [return to slide 22](#multiple-possible-parsed-meanings)' -->
<style scoped>
.box { border: 1px solid var(--ark-line-2); border-left: 4px solid var(--ark-blue); border-radius: 4px; background: #ffffff; padding: 0.65em 1.1em 0.6em 1.1em; margin: 0 0 1.1em 0; font-size: 19px; line-height: 1.45; }
.box:last-child { margin-bottom: 0; }
.box .katex-display { margin: 0.35em 0 0.4em 0 !important; }
.box p { margin: 0; }
</style>

## A number for a function, and a function on the wrong space

<div class="box">

<span class="lbl">A number where a function belongs.</span>
$$v_t=\mathbb{T}\,v_{t+1},\quad v_t:\mathbb{R}_{++}\to\mathbb{R}\qquad\text{read as}\qquad v_t(\hat m_t)\ \text{ alone, at }\ \hat m_t=R\,\hat k_t+\hat y_t,\ \text{ one simulated household's resources.}$$
The backward step then returns one number and one consumption $c_t(\hat m_t)$, although $\mathbb{T}$ needs $v_{t+1}$ at every $R(\hat m_t-c)+y'$. Under this reading the reader has simulated a path where the model asked for a function.

</div>
<div class="box">

<span class="lbl">A function on the wrong space.</span>
$$\mathbb{E}_t\,v_{t+1}(Ra+y')\ \text{ on savings } a=m-c,\ \text{the paper's } k_{t+1},\ a\in[0,\infty)\qquad\text{read as}\qquad v_{t+1}\ \text{ itself, on resources } m\in(0,\infty).$$
The borrowing limit acts at $a=0$, a point at which a function of resources is not defined, so that the two functions have different domains. A reading that confuses them puts the boundary at a point where the constraint does not act.

</div>


---

<!-- slide 51 · The discount and the expectation applied twice, and the recursion as a fixed point -->

<!-- _header: 'Appendix &middot; [return to slide 22](#multiple-possible-parsed-meanings)' -->
<style scoped>
.box { border: 1px solid var(--ark-line-2); border-left: 4px solid var(--ark-blue); border-radius: 4px; background: #ffffff; padding: 0.65em 1.1em 0.6em 1.1em; margin: 0 0 1.1em 0; font-size: 19px; line-height: 1.45; }
.box:last-child { margin-bottom: 0; }
.box .katex-display { margin: 0.35em 0 0.4em 0 !important; }
.box p { margin: 0; }
</style>

## The discount and the expectation applied twice, and the recursion as a fixed point

<div class="box">

<span class="lbl">The discount and the expectation applied by both steps once $\mathbb{T}$ is split.</span>
$$v_t=\max_c\big\{u(c)+\beta\,\mathbb{E}_t\,v_{t+1}(\cdot)\big\}\qquad\text{read as}\qquad v_t=\max_c\big\{u(c)+\beta^2\,\mathbb{E}_{y'}\mathbb{E}_{y''}\,v_{t+1}(\cdot)\big\}.$$
Since the Bellman equation writes $\beta$ and $\mathbb{E}_t$ once each, an implementation that splits $\mathbb{T}$ into the choice and the expectation must decide which step applies $\beta$ and which applies $\mathbb{E}_t$. An implementation that applies $\beta$ and $\mathbb{E}_t$ in each of the two steps makes the household discount at $\beta^2$ and draw income twice.

</div>
<div class="box">

<span class="lbl">Dated value functions read as one stationary function.</span>
$$v_t=\mathbb{T}\,v_{t+1},\ \ v_{t+1}\ \text{an input}\qquad\text{read as}\qquad v=\mathbb{T}\,v,\ \ \text{a fixed point.}$$
A stationarity condition that the statement never makes replaces the backward recursion from a terminal value. Once the terminal value has disappeared from the problem, the last period's consumption is chosen as if another period followed.

</div>


---

<!-- slide 52 · How an AI works with a semantic ontology (divider) -->

<!-- _class: divider sub -->

<p class="eyebrow">Appendix</p>

# How an AI works with a semantic ontology


---

<!-- slide 53 · The AI writes against the ontology -->

<!-- _header: 'Appendix &middot; [return to slide 4](#semantic-ontology)' -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.4em 0; font-size: 16px; line-height: 1.36; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 14px; }
</style>

## The AI writes against the ontology

<div class="center">

![w:700](assets/ai-loop.svg)

</div>

<div class="stack">
<div>

<span class="lbl">Autoformalization.</span> The AI translates the paper into the written form, which the checker accepts or refuses (Wu et al. 2022, where the checker decided syntactic correctness and people judged faithfulness; AlphaProof, Hubert et al. 2026, which learned by reinforcement with Lean's kernel, the core program that checks each proof step, as the verifier).

</div>
<div>

<span class="lbl">Refuse and repair.</span> The checker's refusal, with its rule named, is the AI's next prompt, as the error message of a proof assistant (a program that checks proofs) is in Baldur, a proof-repair system (First et al. 2023). The elaborator's rules `shock-reintroduced` and `field-perch` are messages of this kind.

</div>
<div>

<span class="lbl">Constrained generation.</span> The AI's output is restricted, as the AI produces each word of its output, to the grammar of the written form, so that only its meaning remains to be checked (Poesia et al. 2022; Geng et al. 2023).

</div>
<div>

<span class="lbl">Compute, then answer.</span> From the accepted file the ontology's programs compute Υ's object and Ρ's numbers (or, for a proof, the kernel checks it), so that the AI's answer to the user is built from that output rather than from its own guess.

</div>
<div>

<span class="lbl">Round trip.</span> A second program writes the accepted object back into prose for a judge, a program or a second AI, to compare with the paper (Li et al. 2024), or regenerates the object for comparison with the original (Allamanis et al. 2024). Matsya, the project's assistant service, runs the first loop with the elaborator and two judges and the second with its comparator.

</div>
</div>

<div class="footnote">Wu, Jiang, Li, Rabe, Staats, Jamnik and Szegedy (2022), "Autoformalization with large language models", <em>NeurIPS 2022</em>, 32353–32368 &middot; Hubert, Mehta, Sartran et al. (2026), <em>Nature</em> 651, 607–613, published online 12 November 2025 &middot; First, Rabe, Ringer and Brun (2023), "Baldur: whole-proof generation and repair with large language models", <em>ESEC/FSE 2023</em>, 1229–1241 &middot; Poesia et al. (2022), "Synchromesh", <em>ICLR 2022</em>; Geng, Josifoski, Peyrard and West (2023), "Grammar-constrained decoding for structured NLP tasks without finetuning", <em>EMNLP 2023</em>, 10932–10952 &middot; Li, Wu, Li, Wei, Yang, Zhang and Ma (2024), "Autoformalize mathematical statements by symbolic equivalence and semantic consistency", <em>NeurIPS 2024</em>, 53598–53625; Allamanis, Panthaplackel and Yin (2024), "Unsupervised evaluation of code LLMs with round-trip correctness", <em>ICML 2024</em>, PMLR 235, 1050–1066 &middot; Matsya's architect mode: bellman-ddsl, terminology, 9 October 2026.</div>


---

<!-- slide 54 · The AI reads from the ontology -->
<!-- _class: airy -->

<!-- _header: 'Appendix &middot; [return to slide 4](#semantic-ontology)' -->

<style scoped>
.center img { margin: 0 auto; display: block; }
.stack > div { padding: 0 0 0.8em 0; font-size: 19px; line-height: 1.45; }
.stack > div:last-child { padding-bottom: 0; }
.stack p { margin: 0; }
.stack code { font-size: 14px; }
</style>

## The AI reads from the ontology

<div class="stack">
<div>

<span class="lbl">Retrieval over a knowledge graph.</span> The AI answers from a graph of entities and relations rather than from passages alone (surveyed in Pan et al. 2024; GraphRAG, Edge et al. 2024, which answers from summaries of entity clusters). Matsya retrieves passages of the project's documents with their sections, links and tags, and reads the typed object itself when a question names a stage file.

</div>
<div>

<span class="lbl">Training on generated pairs.</span> The ontology's programs generate pairs of a file and its prose, or the comparator labels two files as one object or as two, so that a model can be trained on the pairs. AlphaProof's roughly one million natural-language problems, auto-formalised into about 80 million formal statements, are the largest instance. The project's comparator module, <code>meaning_map_training.compare</code>, labels such pairs, while the package's own training revises Matsya's instruction texts and settings against the round trip, with the language models' weights fixed.

</div>
<div>

<span class="lbl">What separates the two groups.</span> In the five uses of the previous slide the checker, not the AI, decides what the file means, which makes the AI's reading inspectable. In these two the AI's reading improves but stays statistical, which is why they do not replace the checker.

</div>
</div>

<div class="footnote">Pan, Luo, Wang, Chen, Wang and Wu (2024), "Unifying large language models and knowledge graphs: a roadmap", <em>IEEE Transactions on Knowledge and Data Engineering</em> 36(7), 3580–3599 &middot; Edge et al. (2024), "From local to global: a graph RAG approach to query-focused summarization", arXiv:2404.16130 &middot; Hubert, Mehta, Sartran et al. (2026), <em>Nature</em> 651, 607–613, on the auto-formalised training problems &middot; <code>meaning_map_training.compare</code>: bellman-ddsl.</div>
