// Shared bilingual toggle (EN / IT).
// Content comes in pairs of elements carrying data-lang="en" / data-lang="it";
// the inactive one gets [hidden]. The toggle is any [data-lang-toggle] button
// and shows the language it switches to. The choice persists in localStorage
// so the language carries across pages (GioRadio included).
(function () {
  var KEY = 'lang';

  function get() {
    try { return localStorage.getItem(KEY) || 'en'; } catch (e) { return 'en'; }
  }
  function save(l) {
    try { localStorage.setItem(KEY, l); } catch (e) {}
  }
  function apply(l) {
    document.documentElement.lang = l;
    var nodes = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].hidden = nodes[i].getAttribute('data-lang') !== l;
    }
    var btns = document.querySelectorAll('[data-lang-toggle]');
    for (var j = 0; j < btns.length; j++) {
      btns[j].textContent = l === 'it' ? 'en' : 'it';
      btns[j].setAttribute('aria-label', l === 'it' ? 'Switch to English' : 'Passa all’italiano');
    }
  }

  function init() {
    apply(get());
    document.addEventListener('click', function (e) {
      if (!e.target.closest('[data-lang-toggle]')) return;
      var next = get() === 'it' ? 'en' : 'it';
      save(next);
      apply(next);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
