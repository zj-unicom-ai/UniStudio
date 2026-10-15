"""从已审校的章节草稿生成纯代码动态图镜头时间轴；不伪造史料、不假定配音时长。"""
from pathlib import Path
import re,json,math,csv
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'content/EP01_SCRIPT.md').read_text()
CHAPTERS=[
('S01','序幕·四个年份',0,35,'hero'),
('S02','我们怎样阅读历史',35,80,'timeline'),
('S03','时代之问',80,270,'timeline'),
('S04','从石库门到南湖',270,490,'archive'),
('S05','从城市到农村的探索',490,735,'route'),
('S06','古田会议与组织建设',735,955,'network'),
('S07','遵义会议与历史转折',955,1125,'route'),
('S08','历史中的三个观察角度',1125,1180,'network'),
('S09','尾声·回到历史现场',1180,1200,'recap')]
PATTERNS=['timeline','route','archive','network','whiteboard','contrast','archive','route','network','timeline']
shots=[]; chapters=[]
for cid,title,start,end,base in CHAPTERS:
 m=re.search(r'^## '+cid+r'\b[^\n]*\n(?P<body>.*?)(?=\n## S\d+|\n---\n\n## 录制注意|\Z)', SCRIPT,re.M|re.S)
 assert m,cid
 body=m.group('body').split('**口播**：',1)[1]
 body=re.sub(r'\*\*[^*]*\*\*','',body).strip()
 parts=re.split(r'(?<=[。！？；])|(?<=[，、])',re.sub(r'\s+','',body))
 parts=[p.strip() for p in parts if p.strip()]
 # short phrases merge; very long phrase split by around 24 chars
 units=[]; buf=''
 for p in parts:
  buf+=p
  if len(buf)>=18 or p.endswith(('。','！','？','；')) and len(buf)>=13:
   units.append(buf);buf=''
 if buf: units.append(buf)
 # For shorter chapters force >=2 shots, duration set proportional to weighted voice length
 while len(units)<2:
  units = [units[0][:len(units[0])//2],units[0][len(units[0])//2:]]
 weights=[max(11,len(re.sub(r'[，。！？；、]','',s))) for s in units]
 total=sum(weights)
 bounds=[start]
 acc=0
 for w in weights[:-1]:
  acc+=w
  bounds.append(round(start+(end-start)*acc/total,3))
 bounds.append(end)
 idx=int(cid[1:])-1
 chapters.append({'id':cid,'title':title,'start':start,'end':end,'type':base,'spoken_chars':len(body),'n_shots':len(units)})
 for j,(text,a,b) in enumerate(zip(units,bounds[:-1],bounds[1:])):
  tp=base if j%4==0 else PATTERNS[(j+idx*2)%len(PATTERNS)]
  if cid=='S01':tp=['hero','timeline','route','recap'][j%4]
  if cid=='S09':tp='recap'
  shots.append({'id':f'{cid}-{j+1:03d}','chapter':cid,'start':a,'end':b,'kind':tp,'label':text.strip('，。；！？')[:18], 'spoken':text, 'motion_cue':{'hero':'年份层叠并连线','timeline':'年代线条渐进绘制','route':'示意路线弧线描绘','archive':'模拟资料结构展开（非原始史料）','network':'组织节点与关系连线','whiteboard':'逻辑图形逐笔写出','contrast':'两种方法对照移动','recap':'年份与历史节点回望'}[tp], 'verified_media':False})
assert int(chapters[-1]['end'])==1200
(ROOT/'content/EP01_TIMELINE.json').write_text(json.dumps({'episode':'EP01','title':'从石库门到遵义：在探索中寻找中国革命的道路','resolution':[1920,1080],'fps':25,'target_seconds':1200,'timing_status':'draft_proportional_to_text_not_TTS_aligned','chapters':chapters,'shots':shots},ensure_ascii=False,indent=2))
(ROOT/'src/episode-data.js').write_text('/* 从 content/EP01_SCRIPT.md 生成；章节时间是目标，不是已对齐的配音时间。*/\nwindow.EP01='+json.dumps({'chapters':chapters,'shots':shots},ensure_ascii=False,separators=(',',':'))+';\n')
with (ROOT/'content/SHOTLIST.csv').open('w',newline='',encoding='utf-8-sig') as f:
 wr=csv.writer(f);wr.writerow(['id','chapter','start_sec','end_sec','kind','motion_cue','on_screen_text','narration_piece'])
 for s in shots:wr.writerow([s[k] for k in ['id','chapter','start','end','kind','motion_cue','label','spoken']])
print('Generated',len(shots),'shots',len(chapters),'chapters. Total 1200 sec.')
