#!/usr/bin/env python3
"""
build.py — INSIGHT AI Daily Magazine
Scans content/YYYY/MM/YYYY-MM-DD.md → generates docs/ static site
Usage: pip install markdown && python build.py
"""

import os, re, shutil
from pathlib import Path

try:
    import markdown as _md
except ImportError:
    print("Run: pip install markdown"); exit(1)

# ── Config ─────────────────────────────────────────────────────────────────

CONTENT = Path("content")
DOCS    = Path("docs")
TITLE   = "INSIGHT"
TAGLINE = "AI 领域每日精要"
RECENT  = 20

# ── Parse ──────────────────────────────────────────────────────────────────

def parse_md(path: Path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---\n"):
        rest = text[4:]
        if "\n---\n" in rest:
            fm, body = rest.split("\n---\n", 1)
            for line in fm.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip()

    stem = path.stem
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stem):
        return None
    y, m, d = stem.split("-")

    mk = _md.Markdown(extensions=["extra"])
    html = mk.convert(body.strip())

    first = re.search(r"<p>(.*?)</p>", html, re.DOTALL)
    raw = re.sub(r"<[^>]+>", "", first.group(1) if first else html)
    ex = re.sub(r"\s+", " ", raw).strip()
    if len(ex) > 150:
        ex = ex[:150].rsplit(" ", 1)[0] + "…"

    return {
        "date":  stem, "year": y, "month": m, "day": d,
        "title": meta.get("title", stem),
        "tags":  [t.strip() for t in meta.get("tags","").split(",") if t.strip()],
        "html":  html, "excerpt": ex,
    }

def load_all():
    entries = []
    for f in sorted(CONTENT.rglob("*.md"), reverse=True):
        e = parse_md(f)
        if e: entries.append(e)
    return entries

# ── CSS ────────────────────────────────────────────────────────────────────

CSS = """\
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#080808;--bg2:#161616;
  --t:#e2e2e2;--t2:#a0a0a0;--t3:#555;
  --ac:#00d4ff;--ac0:rgba(0,212,255,.1);
  --b:rgba(255,255,255,.07);
  --mono:'JetBrains Mono','Courier New',monospace;
  --sans:'Inter',-apple-system,sans-serif;
  --mw:860px
}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--t);font-family:var(--sans);font-size:15px;line-height:1.7;min-height:100vh}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:9999;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.025) 2px,rgba(0,0,0,.025) 4px)}
.wrap{max-width:var(--mw);margin:0 auto;padding:0 2rem}

header{border-bottom:1px solid var(--b);padding:2rem 0 1.5rem;margin-bottom:3rem}
.hi{max-width:var(--mw);margin:0 auto;padding:0 2rem;display:flex;align-items:flex-end;
  justify-content:space-between;flex-wrap:wrap;gap:1rem}
.ll{text-decoration:none;color:inherit}
.logo{font-family:var(--mono);font-size:1.5rem;font-weight:700;letter-spacing:.15em}
.cur{color:var(--ac);animation:blink 1s step-end infinite}
@keyframes blink{50%{opacity:0}}
.sub{font-family:var(--mono);font-size:.68rem;color:var(--t3);letter-spacing:.08em;margin-top:.25rem}

.mn{display:flex;gap:.8rem;flex-wrap:wrap}
.mn a{font-family:var(--mono);font-size:.72rem;color:var(--t3);text-decoration:none;
  letter-spacing:.05em;transition:color .15s}
.mn a:hover,.mn a.on{color:var(--ac)}

.list{list-style:none}
.item{border-bottom:1px solid var(--b);padding:1.5rem 0;
  display:grid;grid-template-columns:108px 1fr;gap:1.5rem;align-items:start}
.item:first-child{border-top:1px solid var(--b)}
.idate{font-family:var(--mono);font-size:.74rem;color:var(--t3);letter-spacing:.05em;
  padding-top:.1rem;white-space:nowrap}
.ititle{font-size:1rem;font-weight:500;color:var(--t);text-decoration:none;display:block;
  margin-bottom:.35rem;line-height:1.4;transition:color .15s}
.ititle:hover{color:var(--ac)}
.iex{font-size:.84rem;color:var(--t2)}
.tags{margin-top:.45rem;display:flex;gap:.4rem;flex-wrap:wrap}
.tag{font-family:var(--mono);font-size:.65rem;color:var(--ac);background:var(--ac0);
  padding:.12rem .45rem;border-radius:3px;letter-spacing:.03em}

.adate{font-family:var(--mono);font-size:.76rem;color:var(--ac);letter-spacing:.08em;margin-bottom:.75rem}
.atitle{font-size:1.5rem;font-weight:600;line-height:1.3;
  margin-bottom:2rem;padding-bottom:1.5rem;border-bottom:1px solid var(--b)}
.abody h2{font-family:var(--mono);font-size:.8rem;font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;color:var(--ac);margin:2.5rem 0 1rem;
  padding-bottom:.4rem;border-bottom:1px solid var(--ac0)}
.abody h3{font-size:1rem;font-weight:600;color:var(--t);margin:1.5rem 0 .5rem}
.abody p{color:var(--t2);margin-bottom:1rem}
.abody a{color:var(--ac);text-decoration:none;border-bottom:1px solid transparent;transition:border-color .15s}
.abody a:hover{border-bottom-color:var(--ac)}
.abody ul,.abody ol{padding-left:1.4rem;color:var(--t2);margin-bottom:1rem}
.abody li{margin-bottom:.3rem}
.abody strong{color:var(--t);font-weight:600}
.abody blockquote{border-left:2px solid var(--ac);padding-left:1rem;color:var(--t3);margin:1rem 0;font-style:italic}
.abody code{font-family:var(--mono);font-size:.84em;background:var(--bg2);
  padding:.12em .38em;border-radius:3px;color:var(--ac)}
.abody pre{background:var(--bg2);border:1px solid var(--b);border-radius:6px;
  padding:1.2rem;overflow-x:auto;margin-bottom:1rem}
.abody pre code{background:none;padding:0;color:var(--t2)}
.abody hr{border:none;border-top:1px solid var(--b);margin:2rem 0}

.mh{font-family:var(--mono);font-size:.78rem;letter-spacing:.1em;
  text-transform:uppercase;color:var(--t3);margin-bottom:2rem}

.crumb{max-width:var(--mw);margin:-1.5rem auto 2rem;padding:0 2rem;
  font-family:var(--mono);font-size:.7rem;color:var(--t3)}
.crumb a{color:var(--t3);text-decoration:none}
.crumb a:hover{color:var(--ac)}
.crumb s{margin:0 .4em;opacity:.4;font-style:normal}

.pn{display:flex;justify-content:space-between;margin-top:3rem;
  padding-top:1.5rem;border-top:1px solid var(--b)}
.pn a{font-family:var(--mono);font-size:.76rem;color:var(--t3);
  text-decoration:none;transition:color .15s}
.pn a:hover{color:var(--ac)}

footer{margin-top:5rem;border-top:1px solid var(--b);padding:2rem 0;text-align:center}
.foot{font-family:var(--mono);font-size:.68rem;color:var(--t3);letter-spacing:.08em}

@media(max-width:600px){
  .item{grid-template-columns:1fr;gap:.3rem}
  .atitle{font-size:1.2rem}
  .hi{flex-direction:column;align-items:flex-start}
}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono'
    ':wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">'
)

# ── Templates ──────────────────────────────────────────────────────────────

def mkpage(title, body, nav, root, crumb=""):
    c = f'<div class="crumb">{crumb}</div>' if crumb else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · {TITLE}</title>
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header>
<div class="hi">
<a href="{root}" class="ll">
  <div class="logo">{TITLE}<span class="cur">_</span></div>
  <div class="sub">{TAGLINE}</div>
</a>
<nav class="mn">{nav}</nav>
</div>
</header>
{c}
<div class="wrap">{body}</div>
<footer><div class="foot">{TITLE} · AI Daily · Built with Claude Code</div></footer>
</body>
</html>"""

def build_nav(months, root, active=None):
    recent = months[-8:]
    parts = []
    for (y, m) in recent:
        cls = ' class="on"' if (y, m) == active else ""
        parts.append(f'<a href="{root}{y}/{m}/"{cls}>{y}.{m}</a>')
    return "\n".join(parts)

def entry_card(e, root):
    tags = "".join(f'<span class="tag">{t}</span>' for t in e["tags"])
    trow = f'<div class="tags">{tags}</div>' if tags else ""
    href = f'{root}{e["year"]}/{e["month"]}/{e["date"]}.html'
    dt = e["date"].replace("-", ".")
    return f"""<li class="item">
<div class="idate">{dt}</div>
<div>
<a href="{href}" class="ititle">{e["title"]}</a>
<div class="iex">{e["excerpt"]}</div>
{trow}
</div>
</li>"""

# ── Page builders ──────────────────────────────────────────────────────────

def build_index(entries, months):
    nav = build_nav(months, "./")
    items = "".join(entry_card(e, "./") for e in entries[:RECENT])
    body = f'<ul class="list">{items}</ul>'
    return mkpage(TITLE, body, nav, "./")

def build_month_page(y, m, month_entries, months):
    root = "../../"
    nav = build_nav(months, root, active=(y, m))
    items = "".join(entry_card(e, root) for e in month_entries)
    body = f'<div class="mh">{y} / {m}月</div><ul class="list">{items}</ul>'
    crumb = f'<a href="{root}">INSIGHT</a><s>/</s><a href="./">{y}.{m}</a>'
    return mkpage(f"{y}.{m}", body, nav, root, crumb)

def build_entry_page(e, entries, months):
    root = "../../"
    nav = build_nav(months, root, active=(e["year"], e["month"]))

    idx = next(i for i, x in enumerate(entries) if x["date"] == e["date"])
    # entries sorted newest-first: idx+1 = older (prev), idx-1 = newer (next)
    prev_e = entries[idx + 1] if idx + 1 < len(entries) else None
    next_e = entries[idx - 1] if idx > 0 else None

    def pn_href(x):
        return f'{root}{x["year"]}/{x["month"]}/{x["date"]}.html'

    prev_a = (f'<a href="{pn_href(prev_e)}">← {prev_e["date"].replace("-",".")}</a>'
              if prev_e else "<span></span>")
    next_a = (f'<a href="{pn_href(next_e)}">{next_e["date"].replace("-",".")} →</a>'
              if next_e else "<span></span>")

    tags = "".join(f'<span class="tag">{t}</span>' for t in e["tags"])
    trow = f'<div class="tags" style="margin-bottom:1.5rem">{tags}</div>' if tags else ""
    dt = e["date"].replace("-", ".")

    body = f"""<div class="adate">{dt}</div>
<h1 class="atitle">{e["title"]}</h1>
{trow}
<div class="abody">{e["html"]}</div>
<div class="pn">{prev_a}{next_a}</div>"""

    mlink = f'<a href="./">{e["year"]}.{e["month"]}</a>'
    crumb = f'<a href="{root}">INSIGHT</a><s>/</s>{mlink}<s>/</s>{e["day"]}日'
    return mkpage(e["title"], body, nav, root, crumb)

# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    (DOCS / ".nojekyll").touch()

    entries = load_all()
    if not entries:
        print("No content found. Add content/YYYY/MM/YYYY-MM-DD.md files.")
        return

    # Group by (year, month)
    months_dict: dict = {}
    for e in entries:
        key = (e["year"], e["month"])
        months_dict.setdefault(key, []).append(e)
    months = sorted(months_dict.keys())

    # Index page
    (DOCS / "index.html").write_text(build_index(entries, months), encoding="utf-8")
    print(f"  index.html  ({len(entries)} entries)")

    # Month + entry pages
    for (y, m), month_entries in months_dict.items():
        out_dir = DOCS / y / m
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(
            build_month_page(y, m, month_entries, months), encoding="utf-8")
        print(f"  {y}/{m}/index.html  ({len(month_entries)} entries)")
        for e in month_entries:
            (out_dir / f"{e['date']}.html").write_text(
                build_entry_page(e, entries, months), encoding="utf-8")
            print(f"  {y}/{m}/{e['date']}.html")

    print(f"\nDone: {len(entries)} entries, {len(months)} months -> docs/")

if __name__ == "__main__":
    main()
