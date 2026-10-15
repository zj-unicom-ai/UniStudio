"""真实 huashu MP4 存在时，自动生成带视频轨道的 HyperFrames HTML；绝不引用不存在的片段。"""
from pathlib import Path
import json,subprocess,re
ROOT=Path(__file__).resolve().parents[1]
OVERLAYS=[('1921-organization',340),('1927-path',555),('1929-organization',800),('1935-decision',1030)]
parts=[]
for name,start in OVERLAYS:
 p=ROOT/'media'/'huashu'/(name+'.mp4')
 if not p.is_file():
  print('SKIP (no rendered video):',p.name)
  continue
 try:
  meta=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(p)],check=True,capture_output=True,text=True)
  duration=float(meta.stdout.strip())
 except Exception as e:
  raise RuntimeError(f'Cannot probe {p}: {e}')
 if not 0<duration<=12:raise ValueError(f'Unexpected overlay duration {duration} for {name}; must be ≤12s')
 parts.append(f'<video id="huashu-{name}" class="clip huashu-fullscreen" data-start="{start}" data-duration="{duration:.3f}" data-track-index="9" data-hf-media-start-basis="global" src="../media/huashu/{p.name}" muted playsinline preload="metadata"></video>')
source=(ROOT/'index.html').read_text()
assert '<!-- HF_OVERLAYS:' in source
source=source.replace('<!-- HF_OVERLAYS: scripts/build_composition.py 根据存在的 media/huashu/*.mp4 生成 clip，不存在素材时绝不插空视频。 -->','\n'.join(parts))
source=source.replace('data-composition-id="guangyingdangshi-ep01"','data-composition-id="guangyingdangshi-ep01-huashu"')
source=source.replace("const compId='guangyingdangshi-ep01';","const compId='guangyingdangshi-ep01-huashu';")
source=source.replace('src="./src/','src="../src/').replace('src="./node_modules/','src="../node_modules/')
out=ROOT/'compositions'/'index-with-huashu.html'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(source)
print('Wrote compositions/index-with-huashu.html with',len(parts),'real clips')
