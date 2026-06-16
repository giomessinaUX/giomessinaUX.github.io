// Shared site behaviour: robust scroll reveal + nav hide/show.
(function () {
  var docEl = document.documentElement;
  docEl.classList.add('js-reveal');

  function initReveal() {
    var els = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
    if (!els.length) return;

    function reveal(el) { el.classList.add('is-in'); }
    function inView(el) {
      var r = el.getBoundingClientRect();
      var h = window.innerHeight || docEl.clientHeight;
      return r.top < h * 0.94 && r.bottom > 0;
    }
    function sweep() {
      for (var i = 0; i < els.length; i++) {
        if (!els[i].classList.contains('is-in') && inView(els[i])) reveal(els[i]);
      }
    }

    // 1) Reveal anything already in the viewport right away (hero, etc.)
    sweep();

    // 2) IntersectionObserver for elements scrolled into view later.
    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { reveal(e.target); obs.unobserve(e.target); }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
      els.forEach(function (el) { if (!el.classList.contains('is-in')) obs.observe(el); });
    }

    // 3) Fallbacks that never let content stay hidden if the observer misbehaves.
    window.addEventListener('scroll', sweep, { passive: true });
    window.addEventListener('resize', sweep);
    window.addEventListener('load', sweep);
    setTimeout(sweep, 400);
    // Last resort: if nothing ever revealed, show everything.
    setTimeout(function () {
      var any = els.some(function (el) { return el.classList.contains('is-in'); });
      if (!any) els.forEach(reveal);
    }, 1200);
  }

  function initNav() {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;
    var lastY = window.scrollY;
    window.addEventListener('scroll', function () {
      var y = window.scrollY;
      nav.classList.toggle('is-scrolled', y > 12);
      if (y > lastY && y > 240) nav.classList.add('is-hidden');
      else nav.classList.remove('is-hidden');
      lastY = y;
    }, { passive: true });
  }

  function start() { initReveal(); initNav(); }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
