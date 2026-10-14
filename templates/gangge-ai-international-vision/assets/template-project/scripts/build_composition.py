import re,json,wave,html,argparse
from pathlib import Path
p=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--demo',action='store_true',help='Generate silent sample tracks; for template verification only')
parser.add_argument('--narration',action='store_true',help='Confirm imported WAVs are real narration')
args=parser.parse_args()
r=json.loads((p/'voice-requests.json').read_text(encoding='utf-8'))
modefile=p/'voice-mode.json'
if args.demo:
 (p/'assets/voice-guobiao').mkdir(parents=True,exist_ok=True)
 for seg in r['segments']:
  f=p/'assets/voice-guobiao'/f"{seg['id']}.wav"
  if f.exists(): raise SystemExit(f'Refusing to overwrite audio: {f}')
  with wave.open(str(f),'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(b'\0\0'*24000*4)
 modefile.write_text('{"mode":"demo-silent"}')
if args.narration: modefile.write_text('{"mode":"narration"}')
mode=json.loads(modefile.read_text())['mode'] if modefile.exists() else 'narration'
print('Audio mode:',mode)
if mode=='demo-silent': print('NOTICE: silent template sample, not a narrated production film.')
starts=[]; ds=[];t=.3
for s in r['segments']:
 f=p/'assets/voice-guobiao'/f"{s['id']}.wav"
 if f.exists():
  with wave.open(str(f)) as w:d=w.getnframes()/w.getframerate()
 else:raise SystemExit(f'Missing WAV: {f}. Import narration or use --demo on a fresh project.')
 starts.append(t);ds.append(d);t+=d+.1
end=t+.3; total=end+6
story=json.loads((p/'story-data.json').read_text(encoding='utf-8'))
css=story['base_css']
scenes=story['scenes']
bounds=story['scene_boundaries']
style='''
@font-face{font-family:GG;src:url("assets/vendor/NotoSansCJKsc-Regular.otf")}
html,body{width:100%;height:100%;font-family:GG,sans-serif;display:block}#root{width:100%;height:100%;position:relative;overflow:hidden}.frame{width:100%;height:100%;box-shadow:none}.top{font-size:30px;top:5.3%}.date{color:#b1bdd8}.eyebrow{font-size:30px;margin-bottom:38px}.scene{inset:15% 8% 29%;display:flex!important;justify-content:center}.sheet{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;transform-origin:0% 100%}.title{font-size:104px;line-height:1.18;margin-bottom:40px}.desc{font-size:40px;line-height:1.6;max-width:100%}.tag{font-size:29px;margin-top:28px;padding:18px 22px}.label{font-size:27px;color:#adbfdd}.pill{padding:26px 24px;border-radius:24px}.pill b{font-size:64px}.pill small{font-size:26px;color:#b0bedb}.vs{font-size:30px}.formula{gap:25px;margin-top:40px}.formula div{font-size:34px;padding:20px 10px 20px 28px}.flow{gap:8px;margin-top:60px}.node{min-height:160px;padding:20px 8px;font-size:28px}.arrow{font-size:32px}.q{font-size:39px;padding:28px 0}.q span{font-size:30px}.outro{font-size:59px;line-height:1.4}.caption{left:8%;right:8%;top:75%;bottom:auto;height:240px;font-size:40px;line-height:1.6;padding:24px 0;margin:0;color:#f4f7ff}.bottom{font-size:25px;color:#b0bdd8;bottom:6%}.source{font-size:23px;bottom:3%;color:#a4b3d0}.progress{height:6px}.orb{animation:none}.accent{color:#69e4ff}.rule{height:2px}
'''
earth_svg = '<svg id="earth-grid" viewBox="0 0 648 648" aria-hidden="true" data-layout-allow-overflow data-layout-allow-overlap><g id="earth-meridians" fill="none" stroke="#69e4ff" stroke-width="1.4" opacity=".17"><circle cx="324" cy="324" r="305"/><ellipse cx="324" cy="324" rx="125" ry="305"/><ellipse cx="324" cy="324" rx="235" ry="305"/><ellipse cx="324" cy="324" rx="305" ry="105"/><ellipse cx="324" cy="324" rx="305" ry="220"/><path d="M19 324H629 M324 19V629"/></g><g id="earth-signals" fill="none" stroke="#69e4ff" stroke-width="2" opacity=".24"><ellipse cx="324" cy="324" rx="305" ry="220" stroke-dasharray="18 30"/><ellipse cx="324" cy="324" rx="235" ry="305" stroke-dasharray="8 44"/></g><g id="earth-orbit-a"><circle cx="80" cy="143" r="10" fill="#69e4ff" opacity=".10"/><circle cx="80" cy="143" r="3.6" fill="#9fefff" opacity=".58"/></g><g id="earth-orbit-b"><circle cx="108" cy="478" r="8" fill="#69e4ff" opacity=".10"/><circle cx="108" cy="478" r="3" fill="#69e4ff" opacity=".45"/></g></svg>'
style += '.orb{pointer-events:none}.orb svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}'
parts=[f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{story["project_title"]}</title><script src="assets/vendor/gsap.min.js"></script><style>{css}{style}</style></head><body><div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-duration="{total:.3f}"><div class="frame"><div class="orb" data-layout-allow-overflow data-layout-allow-overlap>{earth_svg}</div><header class="top"><div class="brand">{story["brand"]}</div><div class="date">{story["date_label"]}</div></header><div class="rule"></div>']
for i,s in enumerate(scenes):
 a=0 if i==0 else starts[bounds[i]]-.15;b=starts[bounds[i+1]]-.15 if i<len(scenes)-1 else end
 parts.append(f'<section id="scene-{i}" class="scene clip" data-start="{a:.3f}" data-duration="{b-a:.3f}" data-track-index="0"><div class="sheet" id="sheet-{i}">{s}</div></section>')
for i,(s,d,a) in enumerate(zip(r['segments'],ds,starts)):
 parts.append(f'<div id="caption-{i}" class="caption clip" data-start="{a:.3f}" data-duration="{d+.1:.3f}" data-track-index="2">{html.escape(s["text"])}</div><audio id="voice-{i}" src="assets/voice-guobiao/{s["id"]}.wav" data-start="{a:.3f}" data-duration="{d:.3f}" data-track-index="10"></audio>')
parts.append(f'<footer class="bottom"><span>不止看资讯，更看见本质</span><span>刚哥解读</span></footer><div class="source">{story["source_line"]}</div><div class="progress"><i id="bar"></i></div></div><div id="gangge-ai-outro" style="position:absolute;inset:0;z-index:20" class="clip" data-composition-id="gangge-ai-outro" data-composition-src="compositions/gangge-ai-outro.html" data-start="{end:.3f}" data-duration="6" data-track-index="5" data-width="1080" data-height="1920"></div>')
for i in range(1,len(scenes)):parts.append(f'<audio id="page-{i}" src="assets/sfx/page-whoosh.mp3" data-start="{starts[bounds[i]]-.15:.3f}" data-duration=".45" data-volume=".08" data-track-index="4"></audio>')
parts.append('</div><script>const tl=gsap.timeline({paused:true});')
parts.append(f'tl.fromTo("#earth-meridians",{{rotation:-12,svgOrigin:"324 324"}},{{rotation:100,duration:{end},ease:"none"}},0);')
parts.append(f'tl.to("#earth-signals",{{strokeDashoffset:-320,duration:{end},ease:"none"}},0);')
parts.append(f'tl.fromTo("#earth-orbit-a",{{rotation:0,svgOrigin:"324 324"}},{{rotation:720,duration:{end},ease:"none"}},0);')
parts.append(f'tl.fromTo("#earth-orbit-b",{{rotation:0,svgOrigin:"324 324"}},{{rotation:-540,duration:{end},ease:"none"}},0);')
parts.append('tl.to(".orb",{y:-16,duration:9,repeat:7,yoyo:true,ease:"sine.inOut"},0);')
for i in range(len(scenes)):
 a=0 if i==0 else starts[bounds[i]]-.15
 parts.append(f'tl.fromTo("#sheet-{i}",{{opacity:0,y:28}},{{opacity:1,y:0,duration:.25,ease:"power2.out"}},{a:.3f});')
 parts.append(f'tl.fromTo("#sheet-{i} .title",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:.4,ease:"power2.out"}},{a+.1:.3f});')
parts.append(f'tl.set(".frame",{{autoAlpha:0}},{end});')
parts.append(f'tl.to("#bar",{{width:"100%",duration:{end},ease:"none"}},0);window.__timelines=window.__timelines||{{}};window.__timelines["main"]=tl;</script></body></html>')
(p/'index.html').write_text(''.join(parts))
(p/'timing.json').write_text(json.dumps({'starts':starts,'durations':ds,'outro_start':end,'total':total},indent=2))
(p/'STORYBOARD.md').write_text('# 分镜\n\n'+'\n'.join(f'{i+1}. {starts[bounds[i]]:.2f}s — {story["scene_titles"][i]}' for i in range(len(scenes)))+f'\n{len(scenes)+1}. {end:.2f}s — 固定品牌片尾，保留Logo至结束。\n')
print('Duration',total)

(p/'renders').mkdir(exist_ok=True)
def stamp(v):
 ms=round(v*1000)
 return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
(p/'renders/subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(a+d)}\n{s["text"]}' for i,(s,a,d) in enumerate(zip(r['segments'],starts,ds))),encoding='utf-8')
