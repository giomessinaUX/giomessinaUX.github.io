"""Inject the GioRadio site chrome (nav, breadcrumb, next link, footer) and the
IT/EN language switch into the bundled radio pages. Reads the originals from
SRC, writes to DST.

    python3 _tools/gioradio/build.py            # src -> gioradio/

Edit page content in _tools/gioradio/src/*.html (the JSON-encoded template
inside <script type="__bundler/template">), then rebuild. Never edit the
files in gioradio/ directly: the next build overwrites them.

Language: the pages carry both languages. Static text is written as
<span data-lang="it">…</span><span data-lang="en">…</span>; the page logic
picks strings by document.documentElement.lang and re-renders on the
'gioradio:lang' event. The runtime below sets the language from
localStorage 'lang' (shared with giomessina.com, default 'en') and handles
every [data-lang-toggle] button.

Look: gioradio/skin-v2.css (linked last in every page) maps the pages'
design tokens onto the giomessina.com v2 system (styles-v2.css)."""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "src")
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..", "gioradio")
SITE = "GioRadio"

# Order = nav order. Pages with chrome=False keep their own layout: they only
# get the language runtime, and the "next" cycle skips them.
PAGES = [
    dict(file="Riassunto Corso Radioamatori.html", nav=("Riassunto", "Course notes"),
         title=("Riassunto Corso Radioamatori", "Amateur Radio Course notes"), chrome=False),
    dict(file="Componenti.html", nav=("Componenti", "Components"),
         title=("Componenti di radiotecnica", "Radio components"), kind=("Cheatsheet", "Cheatsheet"),
         width="var(--maxw)", box="content-box"),
    dict(file="Schemi.html", nav=("Schemi", "Diagrams"),
         title=("Schemi a blocchi", "Block diagrams"), kind=("Cheatsheet", "Cheatsheet"),
         width="1360px", box="content-box"),
    dict(file="Codice Q.html", nav=("Codice Q", "Q code"),
         title=("Codice Q", "Q code"), chrome=False),
    dict(file="propagazione-ionosferica.html", nav=("Propagazione", "Propagation"),
         title=("Propagazione ionosferica", "Ionospheric propagation"), kind=("Strumento", "Tool"),
         width="1560px", box="border-box"),
    dict(file="palinsesti-radio-milano.html", nav=("Palinsesti", "Schedules"),
         title=("Palinsesti radio Milano", "Milan radio schedules"), kind=("Strumento", "Tool"),
         width="var(--maxw)", box="border-box"),
]
CHROME = [p for p in PAGES if p.get("chrome", True)]

href = lambda p: p["file"].replace(" ", "%20")
bi = lambda pair: f'<span data-lang="it">{pair[0]}</span><span data-lang="en">{pair[1]}</span>'

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%232b4ee6'/%3E"
           "%3Cpath d='M6 17h5l2-5 3 9 3-9 2 5h5' fill='none' stroke='white' stroke-width='2.4' "
           "stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")

STYLE = """<style id="rd-chrome-style">
.rd-shell{position:sticky;top:0;z-index:60;padding:0 var(--gutter);background:rgba(255,255,255,.92)}
.rd-shell .ds-nav{max-width:var(--maxw);margin:0 auto}
@media (max-width:1180px){.rd-shell .btn-lang{margin-left:auto}}
.rd-wrap{max-width:var(--rd-w);margin:0 auto;padding:0 var(--gutter)}
.rd-way{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 20px;padding-top:clamp(26px,4vw,40px)}
.rd-way__trail{font-family:var(--font-mono);font-size:12.5px;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink-faint)}
.rd-way__trail b{font-weight:inherit;color:var(--accent)}
.rd-end{padding-top:clamp(40px,6vw,72px)}
.rd-end .ds-next{margin-top:0}
.rd-end .ds-footer{margin-top:clamp(28px,4vw,44px)}
</style>"""

TOGGLE = ('<button class="btn-lang" type="button" data-lang-toggle aria-label="Switch language / Cambia lingua">'
          '<span data-lang="en">it</span><span data-lang="it">en</span></button>')

def runtime(p):
    titles = json.dumps({"it": f"{p['title'][0]} — {SITE}", "en": f"{p['title'][1]} — {SITE}"}, ensure_ascii=False)
    return """<style id="gr-i18n-style">
html[lang="en"] [data-lang="it"], html:not([lang="en"]) [data-lang="en"] { display: none !important; }
</style>
<script id="gr-i18n">
(function () {
  var KEY = 'lang', TITLES = %s;
  function get() { try { return localStorage.getItem(KEY) || 'en'; } catch (e) { return 'en'; } }
  function apply(l) {
    document.documentElement.lang = l;
    document.title = TITLES[l];
    window.dispatchEvent(new Event('gioradio:lang'));
  }
  apply(get());
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-lang-toggle]');
    if (!b) return;
    e.preventDefault();
    var l = get() === 'it' ? 'en' : 'it';
    try { localStorage.setItem(KEY, l); } catch (err) {}
    apply(l);
  });
})();
</script>
""" % titles

def head_block(p):
    active = ' class="is-active" aria-current="page"'
    links = "\n".join(
        f'        <a href="{href(q)}"{active if q is p else ""}>{bi(q["nav"])}</a>'
        for q in PAGES)
    return f"""<!-- rd-chrome:start -->
{STYLE}
<div class="rd-shell">
  <nav class="ds-nav">
    <div class="ds-nav__inner">
      <a href="./" class="ds-nav__mark"><span class="ds-nav__dot"></span>{SITE}</a>
      <div class="ds-nav__links">
{links}
      </div>
      {TOGGLE}
    </div>
  </nav>
</div>
<div class="rd-wrap" style="--rd-w:{p['width']};box-sizing:{p['box']}">
  <div class="rd-way">
    <a class="ds-crumb" href="./"><span class="ds-crumb__arrow">←</span> {bi(("Indice", "Index"))}</a>
    <span class="rd-way__trail">{SITE} / <b>{bi(p['kind'])}</b></span>
  </div>
</div>
<!-- rd-chrome:end -->"""

def foot_block(p, nxt):
    return f"""<!-- rd-chrome:start -->
<div class="rd-wrap rd-end" style="--rd-w:{p['width']};box-sizing:{p['box']}">
  <nav class="ds-next">
    <span class="ds-next__label">{bi(("Prossima pagina", "Next page"))} · {bi(nxt['kind'])}</span>
    <a href="{href(nxt)}">{bi(nxt['title'])} <span class="ds-next__arrow">→</span></a>
  </nav>
  <div class="ds-footer">
    <span>{SITE} — {bi(("appunti di studio per il ripasso", "study notes for revision"))}</span>
    <div class="ds-footer__links">
      <a href="./">{bi(("Indice", "Index"))}</a>
    </div>
  </div>
</div>
<!-- rd-chrome:end -->"""

TPL_RE = re.compile(r'(<script type="__bundler/template">\s*)(".*?")(\s*</script>)', re.S)

def must_sub(pattern, repl, t, label):
    t2, n = re.subn(pattern, repl, t, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"pattern not found: {label}")
    return t2

HEAD_EXTRA = (f'<meta name="robots" content="noindex, nofollow">\n'
              f'<link rel="icon" type="image/svg+xml" href="{FAVICON}">\n')
# giomessina.com v2 look; goes last in <head> so it overrides the page's own tokens
SKIN = '<link rel="stylesheet" href="skin-v2.css">\n'

for p in PAGES:
    s = open(os.path.join(SRC, p["file"]), encoding="utf-8").read()
    m = TPL_RE.search(s)
    t = json.loads(m.group(2))
    page_title = f"{p['title'][1]} — {SITE}"

    t = re.sub(r"<title>.*?</title>\n?", "", t, count=1)
    t = t.replace("</head>", f"<title>{page_title}</title>\n{HEAD_EXTRA}{runtime(p)}{SKIN}</head>", 1)

    # page-specific cleanup of the old, per-page chrome
    if p["file"] == "Componenti.html":
        t = must_sub(r'\n  <div style="position: sticky; top: 12px;.*?</nav>\n  </div>\n', "\n", t, "componenti nav")
        t = must_sub(r'\n  <footer class="ds-footer" style="margin-top: clamp\(56px, 8vw, 96px\);">.*?</footer>\n', "\n", t, "componenti footer")
        t = t.replace("scroll-margin-top: 90px;", "scroll-margin-top: 110px;")
        t = t.replace('<header id="top" style="padding: clamp(56px, 9vw, 120px) 0', '<header id="top" style="padding: clamp(32px, 5vw, 64px) 0', 1)
    if p["file"] == "palinsesti-radio-milano.html":
        t = must_sub(r'\n  <div style="position:sticky;top:0;z-index:50;.*?</nav>\n  </div>\n', "\n", t, "palinsesti nav")
        t = must_sub(r'\n  <div style="max-width:var\(--maxw\);margin:0 auto;padding:48px var\(--gutter\) 0;">\s*<footer class="ds-footer">.*?</footer>\s*</div>\n', "\n", t, "palinsesti footer")
        t = t.replace("padding:clamp(48px,8vw,96px) var(--gutter) clamp(28px,4vw,44px);", "padding:clamp(32px,5vw,64px) var(--gutter) clamp(28px,4vw,44px);", 1)

    if p in CHROME:
        nxt = CHROME[(CHROME.index(p) + 1) % len(CHROME)]
        t = must_sub(r"</helmet>\n", lambda _: "</helmet>\n" + head_block(p) + "\n", t, "helmet end")
        t = must_sub(r"\n</x-dc>", lambda _: "\n" + foot_block(p, nxt) + "\n</x-dc>", t, "x-dc end")

    enc = json.dumps(t, ensure_ascii=True).replace("</", "<\\u002F")
    s = s[:m.start(2)] + enc + s[m.end(2):]

    # outer loader page (shown while unpacking)
    s = re.sub(r"<title>.*?</title>", f"<title>{page_title}</title>", s, count=1)
    s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  ' + HEAD_EXTRA.replace("\n", "\n  ").rstrip(), 1)
    s = s.replace("  <a href=\"indiceradio.html\">Torna all'indice</a>\n", "")
    open(os.path.join(DST, p["file"]), "w", encoding="utf-8").write(s)
    print("built", p["file"])
