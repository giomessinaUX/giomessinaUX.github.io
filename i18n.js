// Shared bilingual toggle (EN / IT).
// Content comes in pairs of elements carrying data-lang="en" / data-lang="it";
// the inactive one gets [hidden]. The choice persists in localStorage so the
// language carries across pages.
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
    var btn = document.getElementById('lang-toggle');
    if (btn) {
      btn.textContent = (l === 'it') ? 'EN' : 'IT';
      btn.setAttribute('aria-label', l === 'it' ? 'Switch to English' : 'Passa all\u2019italiano');
    }
  }

  function init() {
    apply(get());
    var btn = document.getElementById('lang-toggle');
    if (btn) {
      btn.addEventListener('click', function () {
        var next = (get() === 'it') ? 'en' : 'it';
        save(next);
        apply(next);
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
