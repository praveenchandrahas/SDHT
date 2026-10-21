#!/usr/bin/env python3
"""Builds a single-file HTML page from docs/technical-writeup.md with images embedded. Usage: build-writeup-page.py OUT.html"""
import base64, os, re, sys, markdown
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
md = open(os.path.join(root, "docs", "technical-writeup.md")).read()
html = markdown.markdown(md, extensions=["tables"])
def emb(m):
    src = m.group(1)
    if src.endswith("placeholder"):
        return '<div class="slot">Photo slot: add a room photo here</div>'
    data = base64.b64encode(open(os.path.join(root, "docs", src), "rb").read()).decode()
    return f'<img src="data:image/png;base64,{data}" alt="{m.group(2)}"'
html = re.sub(r'<img alt="([^"]*)" src="([^"]+)" ?/?>', lambda m: emb(type("M",(),{"group":lambda s,i:[None,m.group(2),m.group(1)][i]})()) + ("" if m.group(2).endswith("placeholder") else ' />'), html)
html = html.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
css = """
:root{--bg:#f6f7f8;--fg:#14181c;--mute:#566069;--rule:#d9dde1;--accent:#1f5fbf;--panel:#ffffff;--code:#eceff2;--slot:#eaf0f8}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#101418;--fg:#e8ecef;--mute:#9aa5ae;--rule:#2b333b;--accent:#6aa5f0;--panel:#171d23;--code:#1d252d;--slot:#18222e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#101418;--fg:#e8ecef;--mute:#9aa5ae;--rule:#2b333b;--accent:#6aa5f0;--panel:#171d23;--code:#1d252d;--slot:#18222e;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font:16px/1.6 "IBM Plex Sans",system-ui,sans-serif;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
main{max-width:900px;margin:0 auto;min-width:0}
h1{font:600 2rem/1.2 "IBM Plex Serif",Georgia,serif;text-wrap:balance;margin:0 0 .5rem}
h2{font:600 1.35rem/1.3 "IBM Plex Serif",Georgia,serif;margin:2.6rem 0 .6rem;padding-top:1rem;border-top:1px solid var(--rule);text-wrap:balance}
h3{font-size:1.05rem;margin:1.6rem 0 .4rem}
p,li{max-width:68ch}
a{color:var(--accent)}
code{font:.88em "IBM Plex Mono",ui-monospace,monospace;background:var(--code);padding:.1em .35em;border-radius:3px}
img{display:block;max-width:100%;height:auto;margin:1rem 0;border:1px solid var(--rule);background:#fcfcfb}
.tw{overflow-x:auto;margin:1rem 0}
table{border-collapse:collapse;font-size:.9rem;min-width:100%}
th,td{border-bottom:1px solid var(--rule);padding:.5rem .7rem;text-align:left;vertical-align:top}
th{color:var(--mute);font-weight:600;font-size:.78rem;text-transform:uppercase;letter-spacing:.04em}
td{font-variant-numeric:tabular-nums}
.slot{border:1.5px dashed var(--accent);background:var(--slot);color:var(--mute);padding:2.2rem 1rem;text-align:center;border-radius:6px;margin:1rem 0}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
"""
page = f'''<title>Home Theatre Technical Writeup</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Serif:wght@600&display=swap">
<style>{css}</style>
<main>{html}</main>
'''
open(sys.argv[1], "w").write(page)
print(len(page)//1024, "KB")
