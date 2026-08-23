import json
import re
import subprocess
import tempfile
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parent
src = (ROOT / 'storyboard.html').read_text()
style = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
script = re.search(r'<script>(.*?)</script>', src, re.S).group(1)
prefix = script.split("let current=0, view='desktop';", 1)[0]
node_code = prefix + "\nconsole.log(JSON.stringify(frames.map(f=>({group:f.group,title:f.title,mode:f.mode,action:f.action,effect:f.effect,watch:f.watch,html:f.render()}))));\n"
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write(node_code)
    js_path = f.name
frames = json.loads(subprocess.check_output(['node', js_path], text=True))

extra_css = r'''
html,body{height:auto!important;overflow:auto!important;background:#f5f5f2!important}
body{margin:0;padding:0;color:#1c1d1f}
.staticHeader{position:sticky;top:0;z-index:50;background:rgba(250,250,248,.97);backdrop-filter:blur(12px);border-bottom:1px solid #d8d9d5;padding:12px 16px}
.staticHeader h1{font-size:18px;margin:0 0 4px;letter-spacing:-.02em}.staticHeader p{font-size:11px;color:#707277;margin:0}
.jump{margin-top:10px}.jump summary{font-size:12px;font-weight:650;cursor:pointer}.jumpGrid{display:grid;grid-template-columns:1fr;gap:4px;padding:8px 0}.jumpGrid a{color:#345f9d;text-decoration:none;font-size:11px;padding:5px 0;border-bottom:1px solid #eee}
.staticMain{max-width:780px;margin:0 auto;padding:14px 12px 80px}
.staticFrame{scroll-margin-top:130px;margin:0 0 42px;padding:0 0 28px;border-bottom:1px solid #d5d6d2}
.staticMeta{padding:4px 2px 12px}.staticMeta .eyebrow{font-size:9px;text-transform:uppercase;letter-spacing:.13em;color:#777;margin-bottom:4px}.staticMeta h2{font-size:17px;margin:0 0 8px}.staticMeta dl{margin:0;display:grid;gap:7px}.staticMeta dt{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#888}.staticMeta dd{font-size:11px;line-height:1.45;margin:2px 0 0}.staticMeta ul{font-size:11px;line-height:1.45;margin:4px 0 0;padding-left:18px}
.staticStage{background:#fff;border:1px solid #c9cac5;border-radius:10px;box-shadow:0 10px 30px rgba(30,32,36,.08);overflow:hidden;margin:0 auto;max-width:430px}
.staticStage .mockApp{min-height:0}.staticStage .note{padding-bottom:38px}.staticStage.mobile .mockApp{display:block;min-height:0}.staticStage.mobile .side{display:none}.staticStage.mobile .note{padding:25px 19px 55px;font-size:14px}.staticStage.mobile .compare{grid-template-columns:1fr}.staticStage.mobile .split{display:block}.staticStage.mobile .taskSide{border-left:0;border-top:1px solid #ddd}.staticStage.mobile .agentGrid{grid-template-columns:1fr}.staticStage.mobile .calendarSplit{display:block}.staticStage.mobile .calendarRail{border-left:0;border-top:1px solid #ddd}.staticStage.mobile .raw{grid-template-columns:1fr}.staticStage.mobile .taskLens{padding:18px 14px 70px}.staticStage .bulkBar{position:relative;bottom:auto;margin:14px 8px;overflow:auto}.staticStage .topbar,.staticStage .frameNav,.staticStage .reviewPanel{display:none!important}
.backTop{display:block;text-align:right;font-size:11px;margin-top:10px;color:#345f9d;text-decoration:none}
@media(min-width:700px){.jumpGrid{grid-template-columns:1fr 1fr}.staticMain{padding-left:20px;padding-right:20px}.staticStage{max-width:620px}.staticStage.mobile{max-width:430px}}
'''

toc = []
sections = []
for idx, f in enumerate(frames, 1):
    fid = f'frame-{idx}'
    toc.append(f'<a href="#{fid}">{escape(f["title"])}</a>')
    watch = ''.join(f'<li>{escape(x)}</li>' for x in f['watch'])
    sections.append(f'''<section class="staticFrame" id="{fid}">
<div class="staticMeta"><div class="eyebrow">{escape(f['group'])} · {escape(f['mode'])}</div><h2>{escape(f['title'])}</h2>
<dl><div><dt>User action</dt><dd>{escape(f['action'])}</dd></div><div><dt>Semantic result</dt><dd>{escape(f['effect'])}</dd></div><div><dt>Evaluate</dt><dd><ul>{watch}</ul></dd></div></dl></div>
<div class="staticStage mobile">{f['html']}</div><a class="backTop" href="#top">Back to frame list ↑</a></section>''')

html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>Task System Storyboard — Static Mobile Review</title><style>{style}\n{extra_css}</style></head><body><header class="staticHeader" id="top"><h1>Task system storyboard v2</h1><p>Static mobile review · text first · bulk first · no JavaScript required</p><details class="jump"><summary>Choose a frame (19)</summary><nav class="jumpGrid">{''.join(toc)}</nav></details></header><main class="staticMain">{''.join(sections)}</main></body></html>'''
(ROOT / 'mobile-review.html').write_text(html)
print(f'Built {len(frames)} static frames, {len(html)} bytes')
