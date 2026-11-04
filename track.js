// Click tracking for Google Analytics, through Google Tag Manager.
// Every click on a link or button pushes a 'ui_click' event to the dataLayer;
// in GTM a Custom Event trigger on 'ui_click' fires the GA4 event tag.
// Parameters: click_label, click_type, click_url, click_section, page_lang.
// Add data-track="name" to an element to give it a stable label.
(function () {
  window.dataLayer = window.dataLayer || [];

  function type(el) {
    if (el.tagName !== 'A') return 'button';
    var href = el.getAttribute('href') || '';
    if (el.hasAttribute('download') || /\.pdf$/i.test(el.pathname)) return 'download';
    if (href.indexOf('mailto:') === 0) return 'email';
    if (href.charAt(0) === '#') return 'anchor';
    if (el.hostname && el.hostname !== location.hostname) return 'outbound';
    return 'internal';
  }

  function label(el) {
    // innerText skips the hidden language, textContent would read "worklavori"
    var t = el.getAttribute('data-track') || el.innerText || el.getAttribute('aria-label') || el.textContent || '';
    return t.replace(/\s+/g, ' ').trim().slice(0, 100);
  }

  function section(el) {
    var s = el.closest('nav, header, section, footer, [id]');
    if (!s) return '';
    return s.id || (typeof s.className === 'string' && s.className.split(' ')[0]) || s.tagName.toLowerCase();
  }

  // capture phase: runs before the browser follows the link
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('a, button, [data-track]');
    if (!el) return;
    window.dataLayer.push({
      event: 'ui_click',
      click_label: label(el),
      click_type: type(el),
      click_url: el.href || '',
      click_section: section(el),
      page_lang: document.documentElement.lang
    });
  }, true);
})();
