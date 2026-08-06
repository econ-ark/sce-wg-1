# Post-build injection: Econ-ARK top banner, Roboto stylesheet,
# working-group line, and PDF download controls (inserted after hydration
# via a load-time script, so the Remix re-render cannot remove them).
p = '_build/html/index.html'
t = open(p).read()
svg_dl = ('<svg viewBox="0 0 24 24" width="14" height="14" fill="none" '
          'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'stroke-linejoin="round"><path d="M12 3v12"></path>'
          '<polyline points="7 10 12 15 17 10"></polyline>'
          '<line x1="5" y1="21" x2="19" y2="21"></line></svg>')
script = (
 "<script>window.addEventListener('load',function(){setTimeout(function(){"
 # Roboto, as on econ-ark.org
 "if(!document.getElementById('ark-fonts')){"
 "var f=document.createElement('link');f.id='ark-fonts';f.rel='stylesheet';"
 "f.href='https://fonts.googleapis.com/css?family=Roboto:400,500,700"
 "&display=swap';document.head.appendChild(f);}"
 # Top banner: white logo left, white nav links right
 "if(!document.querySelector('.ark-banner')){"
 "var b=document.createElement('div');b.className='ark-banner';"
 "var bi=document.createElement('div');bi.className='ark-banner-inner';"
 "var la=document.createElement('a');la.className='ark-logo';"
 "la.href='https://econ-ark.org';"
 "var im=document.createElement('img');im.src='econ-ark-logo-white.png';"
 "im.alt='Econ-ARK';la.appendChild(im);"
 "var nv=document.createElement('nav');nv.className='ark-nav';"
 "[['JEDC-special-issue-proposal.pdf','Proposal PDF'],"
 "['JEDC-annex.pdf','Annex PDF'],"
 "['https://github.com/econ-ark/sce-wg1','GitHub']]"
 ".forEach(function(d){var a=document.createElement('a');a.href=d[0];"
 "a.textContent=d[1];nv.appendChild(a);});"
 "bi.appendChild(la);bi.appendChild(nv);b.appendChild(bi);"
 "document.body.insertBefore(b,document.body.firstChild);}"
 # Subtitle, working-group line, and PDF buttons in the article header
 "var h=document.querySelector('.myst-article-header-fm');"
 "if(h&&!document.querySelector('.pdf-buttons')){"
 "var st=document.createElement('div');st.className='page-subtitle';"
 "st.textContent='Special Issue Proposal';"
 "var t1=h.querySelector('h1');if(t1)t1.insertAdjacentElement('afterend',st);"
 "var w=document.createElement('div');w.className='wg-line';"
 "w.textContent='Society for Computational Economics Working Group No. 1 "
 "on Language and Formal Semantics';h.appendChild(w);"
 "var box=document.createElement('div');box.className='pdf-buttons';"
 "var docs=[['JEDC-special-issue-proposal.pdf','Proposal (PDF)'],"
 "['JEDC-annex.pdf','Annex (PDF)']];"
 "docs.forEach(function(d){var a=document.createElement('a');"
 "a.className='pdf-button';a.href=d[0];"
 "a.setAttribute('aria-label','Download '+d[1]);a.title='Download '+d[1];"
 "a.innerHTML='" + svg_dl + "<span>'+d[1]+'</span>';box.appendChild(a);});"
 "h.appendChild(box);}},250);});</script>")
t = t.replace('</body>', script + '</body>', 1)
open(p, 'w').write(t)
