from pathlib import Path
import json,subprocess,sys
P=Path(__file__).resolve().parents[1]
j=json.loads((P/'content/EP01_TIMELINE.json').read_text())
shots=j['shots']; chap=j['chapters'];assert len(chap)==9 and len(shots)>=150
assert j['target_seconds']==1200 and chap[0]['start']==0 and chap[-1]['end']==1200
for i,s in enumerate(shots):
 assert abs(s['end']-s['start'])>0.05,s
 if i:assert abs(shots[i-1]['end']-s['start'])<.002,(shots[i-1]['id'],s['id'])
for f in (P/'huashu-specs').glob('*.json'):
 x=json.loads(f.read_text());assert x['grammar'] in {'y3_whiteboard','y5_kinetic_type'}
 assert 0<x['duration']<=8 and all(0<=c['at']<x['duration'] for c in x['cues']),f
print('PASS:',len(shots),'shots, 1200 seconds, 9 chapters, huashu specs OK')
