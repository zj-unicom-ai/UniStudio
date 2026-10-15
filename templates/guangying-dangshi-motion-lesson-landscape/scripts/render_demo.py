"""Offline example: export 8 programmatic motion types (16s, 12fps) via Playwright + FFmpeg.
No stock photos, AI pictures, or assets are required. This is a motion demo, NOT a narrated documentary.
"""
from pathlib import Path
import json,subprocess,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
config=json.loads((ROOT/'content/EP01_TIMELINE.json').read_text())
wanted=['hero','timeline','route','archive','network','whiteboard','contrast','recap']
chosen=[]
for kind in wanted:
 options=[x for x in config['shots'] if x['kind']==kind and x['end']-x['start']>2]
 if not options:raise RuntimeError('no shot kind:'+kind)
 chosen.append(options[len(options)//2])
OUT=ROOT/'sample/code-motion-montage.mp4';FPS=12
ff=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',str(FPS),'-vcodec','png','-i','-', '-vf','scale=960:540:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT)],stdin=subprocess.PIPE)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
 page=b.new_page(viewport={'width':960,'height':540},device_scale_factor=1)
 page.set_content('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;overflow:hidden;background:#000}#sceneCanvas{width:960px;height:540px;display:block}</style></head><body><canvas id="sceneCanvas" width="1920" height="1080"></canvas></body></html>')
 page.add_script_tag(content=(ROOT/'src/episode-data.js').read_text())
 page.add_script_tag(content=(ROOT/'src/graphics.js').read_text())
 for i,s in enumerate(chosen):
  for frame in range(FPS*2):
   u=(frame+.5)/(FPS*2)
   t=s['start']+(s['end']-s['start'])*u
   page.evaluate('(t)=>window.renderAt(t)',t)
   img=page.locator('#sceneCanvas').screenshot(type='png')
   ff.stdin.write(img)
  print(f'{i+1}/8 {s["kind"]}: {s["id"]}',flush=True)
 b.close()
ff.stdin.close()
code=ff.wait()
if code: raise RuntimeError(f'ffmpeg exit {code}')
print(f'Wrote {OUT} ({OUT.stat().st_size} bytes)')
