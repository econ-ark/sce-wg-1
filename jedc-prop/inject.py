# Post-build injection: working-group line and compact PDF control in the
# article header (inserted after hydration via a load-time script).
p = '_build/html/index.html'
t = open(p).read()
svg_doc = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" '
           'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
           'stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 '
           '0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
           '<polyline points="14 2 14 8 20 8"></polyline></svg>')
svg_dl = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" '
          'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'stroke-linejoin="round"><path d="M12 3v12"></path>'
          '<polyline points="7 10 12 15 17 10"></polyline>'
          '<line x1="5" y1="21" x2="19" y2="21"></line></svg>')
script = (
 "<script>window.addEventListener('load',function(){setTimeout(function(){"
 "var h=document.querySelector('.myst-article-header-fm');"
 "if(h&&!document.querySelector('.pdf-button')){"
 "var st=document.createElement('div');st.className='page-subtitle';"
 "st.textContent='Special Issue Proposal';"
 "var t1=h.querySelector('h1');if(t1)t1.insertAdjacentElement('afterend',st);"
 "var w=document.createElement('div');w.className='wg-line';"
 "w.textContent='Society for Computational Economics Working Group No. 1 "
 "on Language and Formal Semantics';h.appendChild(w);"
 "var a=document.createElement('a');a.className='pdf-button';"
 "a.href='JEDC-special-issue-proposal.pdf';"
 "a.setAttribute('aria-label','Download PDF');a.title='Download PDF';"
 "a.innerHTML='" + svg_doc + svg_dl + "';h.appendChild(a);}},250);});"
 "</script>")
t = t.replace('</body>', script + '</body>', 1)
open(p, 'w').write(t)
