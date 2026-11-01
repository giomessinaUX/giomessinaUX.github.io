"""Inject the GioRadio site chrome (nav, breadcrumb, next link, footer) into
the bundled radio pages. Reads the originals from SRC, writes to DST.

    python3 _tools/gioradio/build.py            # src -> gioradio/

Edit page content in _tools/gioradio/src/*.html (the JSON-encoded template
inside <script type="__bundler/template">), then rebuild. Never edit the
files in gioradio/ directly: the next build overwrites them."""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "src")
DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..", "gioradio")
SITE = "GioRadio"

# order = nav order and "next" cycle
PAGES = [
    dict(file="Componenti.html", nav="Componenti", title="Componenti di radiotecnica", kind="Cheatsheet", width="var(--maxw)", box="content-box"),
    dict(file="Schemi.html", nav="Schemi", title="Schemi a blocchi", kind="Cheatsheet", width="1360px", box="content-box"),
    dict(file="propagazione-ionosferica.html", nav="Propagazione", title="Propagazione ionosferica", kind="Strumento", width="1560px", box="border-box"),
    dict(file="palinsesti-radio-milano.html", nav="Palinsesti", title="Palinsesti radio Milano", kind="Strumento", width="var(--maxw)", box="border-box"),
]

# Nav order. Riassunto and Codice Q have their own layout and are linked
# here only: the build doesn't touch them.
NAV = [
    ("Riassunto%20Corso%20Radioamatori.html", "Riassunto"),
    ("Componenti.html", "Componenti"),
    ("Schemi.html", "Schemi"),
    ("Codice%20Q.html", "Codice Q"),
    ("propagazione-ionosferica.html", "Propagazione"),
    ("palinsesti-radio-milano.html", "Palinsesti"),
]

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
           "%3Crect width='32' height='32' rx='8' fill='%232b4ee6'/%3E"
           "%3Cpath d='M6 17h5l2-5 3 9 3-9 2 5h5' fill='none' stroke='white' stroke-width='2.4' "
           "stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")

STYLE = """<style id="rd-chrome-style">
.rd-shell{position:sticky;top:0;z-index:60;padding:12px var(--gutter) 0}
.rd-shell .ds-nav{max-width:var(--maxw);margin:0 auto}
.rd-shell .ds-nav__links{gap:clamp(16px,2.4vw,30px)}
@media (max-width:760px){.rd-shell .ds-nav__links{display:none}}
.rd-wrap{max-width:var(--rd-w);margin:0 auto;padding:0 var(--gutter)}
.rd-way{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 20px;padding-top:clamp(26px,4vw,40px)}
.rd-way__trail{font-family:var(--font-mono);font-size:12.5px;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink-faint)}
.rd-way__trail b{font-weight:inherit;color:var(--accent)}
.rd-end{padding-top:clamp(40px,6vw,72px)}
.rd-end .ds-next{margin-top:0}
.rd-end .ds-footer{margin-top:clamp(28px,4vw,44px)}
</style>"""

def head_block(p):
    active = ' class="is-active" aria-current="page"'
    links = "\n".join(
        f'        <a href="{href}"{active if href == p["file"] else ""}>{label}</a>'
        for href, label in NAV)
    return f"""<!-- rd-chrome:start -->
{STYLE}
<div class="rd-shell">
  <nav class="ds-nav">
    <div class="ds-nav__inner">
      <a href="./" class="ds-nav__mark"><span class="ds-nav__dot"></span>{SITE}</a>
      <div class="ds-nav__links">
{links}
      </div>
    </div>
  </nav>
</div>
<div class="rd-wrap" style="--rd-w:{p['width']};box-sizing:{p['box']}">
  <div class="rd-way">
    <a class="ds-crumb" href="./"><span class="ds-crumb__arrow">←</span> Indice</a>
    <span class="rd-way__trail">{SITE} / <b>{p['kind']}</b></span>
  </div>
</div>
<!-- rd-chrome:end -->"""

def foot_block(p, nxt):
    return f"""<!-- rd-chrome:start -->
<div class="rd-wrap rd-end" style="--rd-w:{p['width']};box-sizing:{p['box']}">
  <nav class="ds-next">
    <span class="ds-next__label">Prossima pagina · {nxt['kind']}</span>
    <a href="{nxt['file']}">{nxt['title']} <span class="ds-next__arrow">→</span></a>
  </nav>
  <div class="ds-footer">
    <span>{SITE} — appunti di studio per il ripasso</span>
    <div class="ds-footer__links">
      <a href="./">Indice</a>
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

for i, p in enumerate(PAGES):
    s = open(os.path.join(SRC, p["file"]), encoding="utf-8").read()
    m = TPL_RE.search(s)
    t = json.loads(m.group(2))
    nxt = PAGES[(i + 1) % len(PAGES)]
    page_title = f"{p['title']} — {SITE}"

    t = re.sub(r"<title>.*?</title>\n?", "", t, count=1)
    t = t.replace("</head>", f"<title>{page_title}</title>\n{HEAD_EXTRA}</head>", 1)

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

    t = must_sub(r"</helmet>\n", lambda _: "</helmet>\n" + head_block(p) + "\n", t, "helmet end")
    t = must_sub(r"\n</x-dc>", lambda _: "\n" + foot_block(p, nxt) + "\n</x-dc>", t, "x-dc end")

    enc = json.dumps(t, ensure_ascii=True).replace("</", "<\\u002F")
    s = s[:m.start(2)] + enc + s[m.end(2):]

    # outer loader page (shown while unpacking)
    s = re.sub(r"<title>.*?</title>", f"<title>{page_title}</title>", s, count=1)
    s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  ' + HEAD_EXTRA.replace("\n", "\n  ").rstrip(), 1)
    s = s.replace("  <a href=\"indiceradio.html\">Torna all'indice</a>\n", "")
    open(os.path.join(DST, p["file"]), "w", encoding="utf-8").write(s)
    print("patched", p["file"])
