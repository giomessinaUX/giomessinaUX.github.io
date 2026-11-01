"""Update gioradio/palinsesti.json from the radio stations' own websites.

Run by .github/workflows/palinsesti.yml (manually or weekly), or locally:
    python3 _tools/gioradio/palinsesti.py gioradio/palinsesti.json

Standard library only. Each station has an adapter that returns, for every
weekday, a list of (start, end|None, title, hosts) in hours (0-24). A station
that fails, or returns too little, keeps its previous data, so one broken
site never empties the page. Stations without an adapter are left untouched.
"""
import html
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

DAYS = ["lun", "mar", "mer", "gio", "ven", "sab", "dom"]
DAY_NAME = {"lun": "lunedì", "mar": "martedì", "mer": "mercoledì", "gio": "giovedì",
            "ven": "venerdì", "sab": "sabato", "dom": "domenica"}
DAY_SLUG = {k: v.replace("ì", "i") for k, v in DAY_NAME.items()}

# The page's timeline runs from 05:00 to 01:00 of the next day.
START, END = 5, 25
MIN_PROGRAMS = 3        # a day with fewer programs counts as not parsed
MIN_DAYS = 5            # a station needs this many parsed days to be updated

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130 Safari/537.36")


# ---- helpers ------------------------------------------------------------

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "it-IT,it"})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def text(fragment):
    s = re.sub(r"<[^>]+>", " ", fragment or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def hours(hm):
    h, m = hm.replace(".", ":").split(":")
    return int(h) + int(m) / 60


def split_hosts(s):
    parts = re.split(r"\s*(?:,|&|\be\b)\s*", s)
    return [p.strip() for p in parts if p.strip()]


def links(fragment, path_re):
    return [text(m.group(1)) for m in re.finditer(
        r'<a[^>]+href="[^"]*(?:%s)[^"]*"[^>]*>(.*?)</a>' % path_re, fragment, re.S) if text(m.group(1))]


def dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


# ---- adapters -----------------------------------------------------------

def mediaset(url):
    """105, R101, Virgin Radio, Radio Monte Carlo: one page, a tab per day."""
    page = fetch(url)
    days = {}
    for d in DAYS:
        i = page.find('id="content-%s"' % DAY_NAME[d])
        if i < 0:
            continue
        j = page.find('id="content-', i + 10)
        sec = page[i:j if j > 0 else len(page)]
        items = []
        chunks = sec.split("date-list")[1:]
        for ch in chunks:
            m = re.search(r"<span[^>]*>\s*(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*</span>", ch)
            t = re.search(r"<h3[^>]*>(.*?)</h3>", ch, re.S)
            if not (m and t):
                continue
            hosts = links(ch, r"/conduttori/|/speaker")
            if not hosts:  # 105.net puts the hosts in a <p> above the title
                p = re.search(r"<p[^>]*>(.*?)</p>\s*<h3", ch, re.S)
                if p and "sottotitolo" not in p.group(0):
                    hosts = split_hosts(text(p.group(1)))
            items.append((hours(m.group(1)), hours(m.group(2)), text(t.group(1)), hosts))
        days[d] = items
    return days


def gedi(base):
    """Radio Deejay, Radio Capital: a page per day, start times only."""
    days = {}
    for d in DAYS:
        page = fetch("%s/palinsesto/%s/" % (base, DAY_SLUG[d]))
        items = []
        for m in re.finditer(r'class="start-hour">\s*(\d{1,2}:\d{2})\s*</span>(.*?)</article>', page, re.S):
            body = m.group(2)
            t = re.search(r'<h3[^>]*class="title[^"]*"[^>]*>(.*?)</h3>', body, re.S)
            r = re.search(r'<h4[^>]*class="reference"[^>]*>(.*?)</h4>', body, re.S)
            if not t:
                continue
            hosts = links(r.group(1), r"/conduttori/") if r else []
            items.append((hours(m.group(1)), None, text(t.group(1)), hosts))
        days[d] = items
    return days


def m2o(url):
    """m2o: every day in a hidden #schedule-complete block (.dow_1 … .dow_7)."""
    page = fetch(url)
    days = {}
    for n, d in enumerate(DAYS, 1):
        b = re.search(r'<div class="dow_%d">(.*?)</ul>' % n, page, re.S)
        if not b:
            continue
        items = [(hours(m.group(1)), None, text(m.group(2)), [])
                 for m in re.finditer(r'class="kicker">\s*(\d{1,2}:\d{2})\s*</span>(.*?)</article>', b.group(1), re.S)
                 if text(m.group(2))]
        days[d] = items
    return days


def radioitalia(url):
    """Radio Italia: Next.js data, days titled 'Palinsesto Lunedì' etc."""
    page = fetch(url)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page, re.S)
    data = json.loads(m.group(1))["props"]["pageProps"]["schedule"]["days"]
    by_name = {DAY_NAME[d].replace("ì", "i"): d for d in DAYS}
    days = {}
    for day in data:
        name = day.get("title", "").lower().replace("palinsesto", "").strip().replace("ì", "i")
        d = by_name.get(name)
        if not d:
            continue
        days[d] = [(hours(s["startTime"]), None, s["program"]["title"].strip(), [])
                   for s in day.get("schedules", []) if s.get("startTime") and s.get("program")]
    return days


def rtl(base):
    """RTL 102.5: a page per day; start time plus duration in minutes."""
    days = {}
    for d in DAYS:
        page = fetch("%s/radio/palinsesto/%s/" % (base, DAY_SLUG[d]))
        items = []
        for card in page.split('class="schedule-card ')[1:]:
            t0 = re.search(r'schedule-card-time[^>]*>\s*(\d{1,2}:\d{2})\s*<', card)
            dur = re.search(r"<p>\s*(\d+)\s*min\s*</p>", card)
            name = re.search(r'schedule-card-show-name[^>]*>(.*?)</p>', card, re.S)
            if not (t0 and name):
                continue
            a = hours(t0.group(1))
            items.append((a, a + int(dur.group(1)) / 60 if dur else None, text(name.group(1)), []))
        days[d] = items
    return days


ADAPTERS = {
    "Radio Deejay": (gedi, "https://www.deejay.it"),
    "Radio 105": (mediaset, "https://www.105.net/palinsesto/"),
    "RTL 102.5": (rtl, "https://www.rtl.it"),
    "Radio Italia": (radioitalia, "https://www.radioitalia.it/palinsesto"),
    "Radio Monte Carlo": (mediaset, "https://www.radiomontecarlo.net/palinsesto/"),
    "R101": (mediaset, "https://www.r101.it/palinsesto/"),
    "Radio Capital": (gedi, "https://www.capital.it"),
    "m2o": (m2o, "https://www.m2o.it/palinsesto/"),
    "Virgin Radio": (mediaset, "https://www.virginradio.it/palinsesto/"),
}


# ---- normalisation ------------------------------------------------------

def close_day(items, next_first):
    """Sort, fill missing end times with the next start, handle midnight."""
    items = sorted(items, key=lambda x: x[0])
    # some sites repeat each slot (e.g. desktop + mobile markup): keep the first
    items = [x for k, x in enumerate(items) if k == 0 or x[0] != items[k - 1][0]]
    out = []
    for i, (a, b, title, hosts) in enumerate(items):
        if b is None:
            b = items[i + 1][0] if i + 1 < len(items) else (next_first if next_first is not None else 0) + 24
        if b <= a:
            b += 24
        out.append([a, b, title, hosts])
    return out


def to_timeline(days):
    """Map each day to the page's 05:00-01:00 window, borrowing the first
    hour of the next day for programmes that run past midnight."""
    closed = {}
    for i, d in enumerate(DAYS):
        nxt = days.get(DAYS[(i + 1) % 7]) or []
        closed[d] = close_day(days.get(d) or [], min((x[0] for x in nxt), default=None))
    out = {}
    for i, d in enumerate(DAYS):
        nxt = closed[DAYS[(i + 1) % 7]]
        progs = [list(p) for p in closed[d]] + [[a + 24, b + 24, t, h] for a, b, t, h in nxt if a < END - 24]
        res = []
        for a, b, title, hosts in progs:
            a, b = max(a, START), min(b, END)
            if b - a >= 1 / 60 and title:
                res.append([round(a, 2), round(b, 2), title, dedupe(hosts)])
        res.sort(key=lambda x: x[0])
        # drop exact duplicates created by overlapping sources
        out[d] = [p for k, p in enumerate(res) if k == 0 or p[:3] != res[k - 1][:3]]
    return out


# ---- main ---------------------------------------------------------------

def dump(data):
    """JSON with one programme per line: readable diffs in git."""
    lines = ["{", ' "updated": %s,' % json.dumps(data.get("updated")),
             ' "note": %s,' % json.dumps(data.get("note", ""), ensure_ascii=False), ' "stations": [']
    for si, s in enumerate(data["stations"]):
        head = {k: v for k, v in s.items() if k not in ("programs", "days")}
        lines.append("  {" + json.dumps(head, ensure_ascii=False)[1:-1] + ",")
        lines.append('   "programs": [')
        lines.append(",\n".join("    " + json.dumps(p, ensure_ascii=False) for p in s.get("programs", [])))
        lines.append("   ],")
        lines.append('   "days": {')
        dkeys = [d for d in DAYS if d in s.get("days", {})]
        for di, d in enumerate(dkeys):
            lines.append('    "%s": [' % d)
            lines.append(",\n".join("     " + json.dumps(p, ensure_ascii=False) for p in s["days"][d]))
            lines.append("    ]" + ("," if di < len(dkeys) - 1 else ""))
        lines.append("   }")
        lines.append("  }" + ("," if si < len(data["stations"]) - 1 else ""))
    lines += [" ]", "}", ""]
    return "\n".join(lines)


def main(path):
    data = json.load(open(path, encoding="utf-8"))
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ok = failed = 0
    for s in data["stations"]:
        adapter = ADAPTERS.get(s["name"])
        if not adapter:
            print("·  %-18s manuale (nessun adattatore)" % s["name"])
            continue
        fn, url = adapter
        try:
            days = to_timeline(fn(url))
            good = {d: p for d, p in days.items() if len(p) >= MIN_PROGRAMS}
            if len(good) < MIN_DAYS:
                raise ValueError("solo %d giorni leggibili" % len(good))
            s["days"] = {d: good.get(d, s.get("days", {}).get(d)) for d in DAYS if good.get(d) or s.get("days", {}).get(d)}
            s["programs"] = good.get("lun") or s.get("programs", [])
            s["source"] = url
            s["updated"] = now
            s.pop("error", None)
            ok += 1
            print("✓  %-18s %s" % (s["name"], " ".join("%s:%d" % (d, len(good.get(d, []))) for d in DAYS)))
        except Exception as e:
            s["error"] = "%s (%s)" % (type(e).__name__, str(e)[:120])
            failed += 1
            print("✗  %-18s %s — tengo i dati precedenti" % (s["name"], s["error"]))
    if ok:
        data["updated"] = now
    open(path, "w", encoding="utf-8").write(dump(data))
    print("\n%d aggiornate, %d fallite, %d manuali" % (ok, failed, len(data["stations"]) - ok - failed))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "gioradio/palinsesti.json"))
