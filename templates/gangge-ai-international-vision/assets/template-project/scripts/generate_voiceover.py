"""Optional configurable WAV TTS adapter; never hardcodes another user's profile."""
import argparse, json, os, urllib.request, wave
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--url',default=os.environ.get('TTS_URL'),help='Full authorized speech endpoint, e.g. http://localhost:3900/v1/audio/speech')
 parser.add_argument('--voice',default=os.environ.get('TTS_VOICE'),help='Voice profile on YOUR provider')
 parser.add_argument('--model',default=os.environ.get('TTS_MODEL'),help='Model supported by YOUR provider')
 args=parser.parse_args()
 if not all((args.url,args.voice,args.model)): parser.error('Set --url, --voice and --model (or TTS_URL/TTS_VOICE/TTS_MODEL). Import WAV instead if no TTS is available.')
 r=json.loads((P/'voice-requests.json').read_text(encoding='utf-8')); out=P/'assets/voice-guobiao';out.mkdir(parents=True,exist_ok=True)
 manifest=[]
 for seg in r['segments']:
  body=json.dumps({'model':args.model,'voice':args.voice,'input':seg['text'],'language':r.get('language','zh'),'speed':r.get('speed',1.0),'response_format':'wav'},ensure_ascii=False).encode()
  headers={'Content-Type':'application/json'}
  if os.environ.get('TTS_API_KEY'): headers['Authorization']='Bearer '+os.environ['TTS_API_KEY']
  req=urllib.request.Request(args.url,data=body,headers=headers,method='POST')
  with urllib.request.urlopen(req,timeout=600) as response: data=response.read()
  if not data.startswith(b'RIFF') or b'WAVE' not in data[:16]: raise RuntimeError('Provider did not return WAV; configure a supported endpoint or import WAV manually.')
  dest=out/(seg['id']+'.wav'); dest.write_bytes(data)
  with wave.open(str(dest)) as wav: duration=wav.getnframes()/wav.getframerate()
  manifest.append({'id':seg['id'],'path':str(dest.relative_to(P)),'duration_s':duration});print(seg['id'],round(duration,2),'seconds')
 (P/'voice-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 (P/'voice-mode.json').write_text('{"mode":"narration"}')
 print('Narration prepared. Run npm run compose before rendering.')
if __name__=='__main__': main()
