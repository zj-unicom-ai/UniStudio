#!/usr/bin/env python3
"""Optional OpenAI-compatible VoiceStudio narration generator. Configure endpoint and voice via environment."""
import json, os, subprocess, urllib.request, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    base=os.environ.get("VOICESTUDIO_BASE_URL", "").rstrip("/")
    voice=os.environ.get("VOICESTUDIO_VOICE_ID", "")
    if not base or not voice:
        raise SystemExit("Set VOICESTUDIO_BASE_URL and VOICESTUDIO_VOICE_ID before generating narration.")
    selected=Path(os.environ.get("EPISODE_DATA", "data/sample-episode.json"))
    data=json.loads((ROOT/selected).read_text(encoding="utf-8"))
    opening=data.get("opening", {})
    seg=[{"id":"welcome","text":opening.get("welcome", "")},{"id":"bridge","text":opening.get("bridge", "")}]
    seg=[item for item in seg if item["text"]]
    seg += [{"id":p["id"],"text":p["say"]} for p in data["pages"] if p.get("say")]
    audio_dir=ROOT/"assets/audio"; audio_dir.mkdir(parents=True,exist_ok=True); manifest=[]
    for i,item in enumerate(seg,1):
        payload={"model":os.environ.get("VOICESTUDIO_MODEL","omnivoice"),"voice":voice,"input":item["text"],"speed":float(os.environ.get("VOICESTUDIO_SPEED","1.0")),"response_format":"wav"}
        req=urllib.request.Request(base+"/v1/audio/speech",data=json.dumps(payload,ensure_ascii=False).encode(),headers={"Content-Type":"application/json","Accept":"audio/wav"},method="POST")
        with urllib.request.urlopen(req,timeout=600) as response: audio=response.read()
        if not audio.startswith(b"RIFF") or b"WAVE" not in audio[:16]: raise RuntimeError(f"Non-WAV response for {item['id']}")
        target=audio_dir/(item["id"]+".wav"); target.write_bytes(audio)
        with wave.open(str(target),"rb") as wav: duration=wav.getnframes()/wav.getframerate(); rate=wav.getframerate(); channels=wav.getnchannels()
        manifest.append({"id":item["id"],"path":f"assets/audio/{target.name}","duration_s":round(duration,6),"sample_rate":rate,"channels":channels})
        print(f"[{i}/{len(seg)}] {item['id']} {duration:.2f}s",flush=True)
    (ROOT/"voice-manifest.json").write_text(json.dumps({"sample_note":"Narration generated with user-configured provider.","segments":manifest},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    timing={x["id"]:round(x["duration_s"]+1.35,3) for x in manifest if x["id"] not in ("welcome","bridge")}
    intro={x["id"]:x["duration_s"] for x in manifest if x["id"] in ("welcome","bridge")}
    timing["p01"]=round(intro["welcome"]+0.15+intro["bridge"],3)
    (ROOT/"timing.json").write_text(json.dumps(timing,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
