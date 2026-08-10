/* Theme toggle behaviour, shared by every page. Loaded with defer, so it runs
   after the toggle button exists. The separate pre-paint snippet inlined in each
   page's <head> is what applies a saved theme before first paint; it has to stay
   inline to avoid a flash of the wrong theme, and is deliberately not here. */
(function(){
  var btn=document.getElementById('theme-toggle');
  var state=document.getElementById('theme-state');
  if(!btn||!state)return;
  var mq=window.matchMedia?window.matchMedia('(prefers-color-scheme: dark)'):null;
  function current(){return document.documentElement.dataset.omTheme||((mq&&mq.matches)?'dark':'light');}
  /* The button is named for what it does, not for the state it is in: an explicit aria-label
     wins over the button's contents, so the status span below never becomes its accessible name. */
  function describe(){var msg='Switch to '+(current()==='dark'?'light':'dark')+' theme';btn.setAttribute('aria-label',msg);btn.title=msg;}
  btn.addEventListener('click',function(){
    var next=current()==='dark'?'light':'dark';
    document.documentElement.dataset.omTheme=next;
    describe();
    /* Announced only in response to the click, so the live region stays quiet on load. */
    state.textContent='theme: '+next;
    try{localStorage.setItem('wg1-theme',next);}catch(e){}
  });
  if(mq&&mq.addEventListener)mq.addEventListener('change',describe);
  describe();
})();
