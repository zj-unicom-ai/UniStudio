# -*- coding: utf-8 -*-
"""Align M4 shots and captions to VoiceStudio ASR timestamps; build HF entrypoint."""
from pathlib import Path
from difflib import SequenceMatcher
from bisect import bisect_left
import csv
import html
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "output/voice-m4"
SCRIPT_PATH = ROOT / "content/EP01_SCRIPT_M4.md"
MANIFEST_PATH = VOICE_DIR / "manifest.json"
GAP = 0.35

if not MANIFEST_PATH.exists():
    raise SystemExit("Missing voice manifest; run scripts/assemble_m4_audio.py after TTS generation.")
manifest = json.loads(MANIFEST_PATH.read_text())
chapter_meta = {item["id"]: item for item in manifest.get("chapters", [])}
if len(chapter_meta) != 9:
    raise SystemExit("Voice manifest must contain all 9 chapters and actual durations.")

script = SCRIPT_PATH.read_text()
script_meta = {}
for match in re.finditer(r"^## (S\d+)｜([^\n]+).*?\*\*口播\*\*[：:]\s*(.*?)(?=^## |^---$|\Z)", script, re.M | re.S):
    cid, heading, narration = match.group(1), match.group(2), match.group(3).strip()
    script_meta[cid] = {"title": re.sub(r"^\d{2}:\d{2}–\d{2}:\d{2}｜", "", heading), "text": narration}
if len(script_meta) != 9:
    raise SystemExit(f"Expected 9 narration sections in M4 script; found {len(script_meta)}")

def clean_char(c):
    return c.isalnum() or "\u3400" <= c <= "\u9fff"

def normalize_with_positions(text):
    chars, positions = [], []
    for i, c in enumerate(text):
        if clean_char(c):
            chars.append(c.lower())
            positions.append(i)
    return "".join(chars), positions

def timed_tokens(transcript):
    raw = transcript.get("words") or transcript.get("segments") or []
    result = []
    for item in raw:
        text = item.get("word") or item.get("text") or ""
        norm, _ = normalize_with_positions(text)
        if not norm:
            continue
        start = float(item.get("start", 0.0))
        end = float(item.get("end", start))
        if end < start:
            end = start
        result.append({"text": norm, "start": start, "end": end})
    if not result:
        text, _ = normalize_with_positions(transcript.get("text", ""))
        if text:
            duration = float(transcript.get("duration", 0.0))
            result.append({"text": text, "start": 0.0, "end": duration})
    return result

def align_char_times(reference, tokens, duration):
    ref, raw_positions = normalize_with_positions(reference)
    hyp = "".join(token["text"] for token in tokens)
    hyp_times = []
    for token in tokens:
        n = max(1, len(token["text"]))
        for i in range(n):
            a = token["start"] + (token["end"] - token["start"]) * i / n
            b = token["start"] + (token["end"] - token["start"]) * (i + 1) / n
            hyp_times.append((a, b))
    if not ref:
        return ref, raw_positions, [], 0.0
    matcher = SequenceMatcher(None, ref, hyp, autojunk=False)
    matches = [m for m in matcher.get_matching_blocks() if m.size]
    covered = sum(m.size for m in matches)
    mapped = [None] * len(ref)
    for match in matches:
        for offset in range(match.size):
            ref_idx = match.a + offset
            hyp_idx = match.b + offset
            if hyp_idx < len(hyp_times):
                mapped[ref_idx] = hyp_times[hyp_idx]
    known = [i for i, value in enumerate(mapped) if value is not None]
    if not known:
        return ref, raw_positions, [], 0.0
    first = known[0]
    first_t = mapped[first][0]
    for i in range(first):
        a = first_t * i / max(1, first)
        b = first_t * (i + 1) / max(1, first)
        mapped[i] = (a, b)
    for left, right in zip(known, known[1:]):
        if right <= left + 1:
            continue
        left_end = mapped[left][1]
        right_start = mapped[right][0]
        if right_start < left_end:
            right_start = left_end
        missing = right - left - 1
        for k in range(1, missing + 1):
            a = left_end + (right_start - left_end) * (k - 1) / (missing + 1)
            b = left_end + (right_start - left_end) * k / (missing + 1)
            mapped[left + k] = (a, b)
    last = known[-1]
    last_end = mapped[last][1]
    remaining = len(ref) - 1 - last
    for k in range(1, remaining + 1):
        a = last_end + (duration - last_end) * (k - 1) / max(1, remaining)
        b = last_end + (duration - last_end) * k / max(1, remaining)
        mapped[last + k] = (a, b)
    # Whisper may produce overlaps. Enforce a monotonic, in-bounds character clock.
    fixed = []
    previous = 0.0
    for a, b in mapped:
        a = min(max(float(a), previous, 0.0), duration)
        b = min(max(float(b), a, previous), duration)
        fixed.append((a, b))
        previous = a
    return ref, raw_positions, fixed, covered / max(1, len(ref))

def make_boundaries(raw, ref, positions, times, duration):
    punctuation = set("，。！？；、：")
    points = {0: 0.0, len(ref): duration}
    norm_count = 0
    for raw_i, char in enumerate(raw):
        if char in punctuation and 0 < norm_count < len(ref):
            points[norm_count] = (times[norm_count - 1][1] + times[norm_count][0]) / 2 if norm_count < len(times) else times[-1][1]
        if clean_char(char):
            norm_count += 1
    points[len(ref)] = duration
    sorted_points = sorted(points.items())
    # Fill punctuation-free/empty intervals from actual ASR character timing.
    return sorted_points

def choose_shots(cid, raw, duration, chapter_start, tokens, seq_start):
    ref, positions = normalize_with_positions(raw)
    _, _, char_times, coverage = align_char_times(raw, tokens, duration)
    if not char_times:
        raise SystemExit(f"No usable timestamps for {cid}")
    punctuation_points = make_boundaries(raw, ref, positions, char_times, duration)
    punctuation_indices = {idx for idx, _ in punctuation_points}
    punctuation_points_by_index = {
        idx: (0.0 if idx == 0 else duration if idx == len(ref) else (char_times[idx - 1][1] + char_times[idx][0]) / 2)
        for idx in range(len(ref) + 1)
    }
    for idx, point_time in punctuation_points:
        punctuation_points_by_index[idx] = point_time
    # Every cut must leave a readable 2–8 second visual event. Captions average 5.8 seconds.
    cuts = [0]
    cursor = 0
    while cursor < len(ref):
        local_start = 0.0 if cursor == 0 else punctuation_points_by_index[cursor]
        if duration - local_start <= 7.8:
            nxt = len(ref)
        else:
            target = local_start + 5.8
            min_t, max_t = local_start + 2.0, min(duration, local_start + 7.8)
            candidates = [idx for idx in punctuation_indices if idx > cursor and min_t <= punctuation_points_by_index[idx] <= max_t]
            if candidates:
                nxt = min(candidates, key=lambda idx: abs(punctuation_points_by_index[idx] - target))
            else:
                starts = [pair[0] for pair in char_times]
                guess = bisect_left(starts, target, lo=cursor + 1)
                nxt = max(cursor + 1, min(len(ref), guess))
                while nxt < len(ref) and punctuation_points_by_index[nxt] > max_t:
                    nxt -= 1
                if nxt <= cursor:
                    nxt = min(len(ref), cursor + 1)
        if nxt <= cursor:
            nxt = min(len(ref), cursor + 1)
        cuts.append(nxt)
        cursor = nxt
    if len(cuts) > 2:
        final_duration = duration - punctuation_points_by_index[cuts[-2]]
        if final_duration < 2.0:
            merged_duration = duration - punctuation_points_by_index[cuts[-3]]
            if merged_duration <= 8.0:
                cuts.pop(-2)
    patterns = {
        "S01": ["hero", "timeline", "recap", "hero"],
        "S02": ["timeline", "contrast", "network", "archive"],
        "S03": ["timeline", "contrast", "archive", "network", "timeline", "contrast"],
        "S04": ["archive", "route", "network", "whiteboard", "contrast", "timeline"],
        "S05": ["route", "whiteboard", "network", "contrast", "timeline", "route"],
        "S06": ["network", "whiteboard", "archive", "contrast", "network", "timeline"],
        "S07": ["route", "whiteboard", "contrast", "timeline", "archive", "network"],
        "S08": ["contrast", "recap", "timeline", "network"],
        "S09": ["recap", "hero", "timeline"],
    }
    cue = {
        "hero": "年份与主题由细线逐步连起",
        "timeline": "年代节点依次点亮并延展",
        "route": "标示性路径沿节点逐段描出（路线示意）",
        "archive": "事件信息卡与关系线逐项展开（结构示意）",
        "network": "组织节点出现并接通关系",
        "whiteboard": "图形与逻辑关系逐笔写出（非原始史料）",
        "contrast": "历史条件与实践回应并列显现",
        "recap": "历史年份回到同一条探索脉络",
    }
    shots = []
    raw_cursor = 0
    punctuation = set("，。！？；、：")
    for i, (a_idx, b_idx) in enumerate(zip(cuts[:-1], cuts[1:])):
        raw_start = positions[a_idx] if a_idx < len(positions) else len(raw)
        raw_end = positions[b_idx] if b_idx < len(positions) else len(raw)
        while raw_start < len(raw) and raw[raw_start].isspace():
            raw_start += 1
        while raw_end < len(raw) and (raw[raw_end] in punctuation or raw[raw_end].isspace()):
            raw_end += 1
        caption = raw[raw_start:raw_end].strip()
        if not caption:
            caption = raw[positions[a_idx]:positions[min(b_idx, len(positions)) - 1] + 1]
        local_start = 0.0 if i == 0 else punctuation_points_by_index[a_idx]
        local_end = duration if b_idx == len(ref) else punctuation_points_by_index[b_idx]
        if i == 0:
            local_start = min(local_start, char_times[a_idx][0])
        if local_end <= local_start:
            local_end = min(duration, local_start + 2.0)
        kind = patterns[cid][i % len(patterns[cid])]
        shots.append({
            "id": f"{cid}-{i+1:03d}", "chapter": cid,
            "start": round(chapter_start + local_start, 4), "end": round(chapter_start + local_end, 4),
            "local_start": round(local_start, 4), "local_end": round(local_end, 4),
            "kind": kind, "label": re.sub(r"[，。！？；、：\s]", "", caption)[:18],
            "caption": caption, "spoken": caption, "motion_cue": cue[kind],
            "alignment_coverage": round(coverage, 4), "verified_media": False,
        })
    return shots, coverage

all_chapters = []
all_shots = []
cursor_time = 0.0
sequence = 0
for number in range(1, 10):
    cid = f"S{number:02d}"
    audio_path = VOICE_DIR / f"{cid}.wav"
    transcript_path = VOICE_DIR / f"{cid}.transcript.json"
    if not audio_path.exists() or not transcript_path.exists():
        raise SystemExit(f"Missing audio or ASR output for {cid}")
    audio_duration = float(chapter_meta[cid]["duration_seconds"])
    if abs(audio_duration - float(manifest["chapters"][number-1]["duration_seconds"])) > 0.05:
        raise SystemExit(f"Audio duration mismatch in manifest for {cid}")
    transcript = json.loads(transcript_path.read_text())
    tokens = timed_tokens(transcript)
    if not tokens:
        raise SystemExit(f"No timed ASR tokens in {cid}")
    chapter_start = cursor_time
    shots, coverage = choose_shots(cid, script_meta[cid]["text"], audio_duration, chapter_start, tokens, sequence)
    for shot in shots:
        sequence += 1
        all_shots.append(shot)
    chapter = {
        "id": cid, "title": script_meta[cid]["title"],
        "start": round(chapter_start, 4), "end": round(chapter_start + audio_duration, 4),
        "duration_seconds": round(audio_duration, 4), "narration_chars": len(script_meta[cid]["text"]),
        "alignment_coverage": round(coverage, 4), "n_shots": len(shots),
    }
    all_chapters.append(chapter)
    print(f"{cid}: {audio_duration:.2f}s, {len(shots)} shots, ASR alignment {coverage:.1%}", flush=True)
    cursor_time += audio_duration
    if number < 9:
        cursor_time += GAP

total = round(cursor_time, 4)
episode = {
    "episode": "EP01", "version": "M4",
    "title": "从石库门到遵义：在探索中寻找中国革命的道路",
    "resolution": [1920, 1080], "fps": 25,
    "duration_seconds": total, "target_seconds": 1200,
    "timing_status": "aligned_to_voicestudio_whisper_timestamps",
    "voice_profile": {"id": "c36e2897", "name": "国标视野", "license": "CC-BY-NC; non-commercial use only"},
    "chapters": all_chapters, "shots": all_shots,
}
(ROOT / "content/EP01_TIMELINE_M4.json").write_text(json.dumps(episode, ensure_ascii=False, indent=2))
(ROOT / "src/episode-data-m4.js").write_text("/* M4 音频真实时码与语音识别分段对齐数据。 */\nwindow.EP01_M4=" + json.dumps({"duration_seconds": total, "chapters": all_chapters, "shots": all_shots}, ensure_ascii=False, separators=(",", ":")) + ";\n")
with (ROOT / "content/SHOTLIST_M4.csv").open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.writer(handle)
    writer.writerow(["id", "chapter", "start_sec", "end_sec", "duration_sec", "kind", "motion_cue", "caption", "asr_alignment_coverage"])
    for shot in all_shots:
        writer.writerow([shot["id"], shot["chapter"], shot["start"], shot["end"], round(shot["end"]-shot["start"], 3), shot["kind"], shot["motion_cue"], shot["caption"], shot["alignment_coverage"]])

# Reuse the already-reviewed Canvas renderer, with the real M4 clock and an external subtitle track.
graphics = (ROOT / "src/graphics.js").read_text()
graphics = graphics.replace("let data=window.EP01;let SHOTS=data.shots,CHAPS=data.chapters;", "let data=window.EP01_M4;let SHOTS=data.shots,CHAPS=data.chapters;const TOTAL=data.duration_seconds;")
graphics = graphics.replace("clamp(t/1200)", "clamp(t/TOTAL)")
graphics = graphics.replace("${format(t)}  /  20:00", "${format(t)}  /  ${format(TOTAL)}")
graphics = graphics.replace("clamp(timestamp,0,1199.999)", "clamp(timestamp,0,TOTAL-0.001)")
graphics = graphics.replace("'Noto Sans CJK SC','PingFang SC',sans-serif", "'GuangyingSans',sans-serif")
network_end = "g.restore();});\n}\nfunction drawWhiteboard(ch,sh,p,t){"
if network_end not in graphics:
    raise SystemExit("Could not locate drawNetwork end to add its non-archive label")
graphics = graphics.replace(
    network_end,
    "g.restore();});\n alphaText('组织关系示意 · 非历史原件',1824,845,22,C.dim,'sans','400','right');\n}\nfunction drawWhiteboard(ch,sh,p,t){",
    1,
)
contrast_end = "line(905,565,1000,565,C.gold,8,ease((p-.4)/.35));\n}\nfunction drawRecap"
if contrast_end not in graphics:
    raise SystemExit("Could not locate drawContrast end to label the modern comparison")
graphics = graphics.replace(
    contrast_end,
    "line(905,565,1000,565,C.gold,8,ease((p-.4)/.35));\n alphaText('本片归纳 · 非会议原文',1824,845,22,C.dim,'sans','400','right');\n}\nfunction drawRecap",
    1,
)
graphics = re.sub(r"\n // Actual narration-specific labels.*?\n window\.__currentShot=shot\.id;", "\n // Captions are a separate timed HyperFrames track so they remain visible over Huashu video.\n window.__currentShot=shot.id;", graphics, flags=re.S)
(ROOT / "src/graphics-m4.js").write_text(graphics)

def probe_duration(path):
    output = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], text=True)
    return float(output.strip())

huashu = [
    ("S04", "1921-organization.mp4", "一大纲领"),
    ("S05", "1927-path.mp4", "三湾改编"),
    ("S06", "1929-organization.mp4", "古田会议"),
    ("S07", "1935-decision.mp4", "遵义会议"),
    ("S09", "1935-coda.mp4", "从石库门到遵义"),
]
source_refs = {"S04": "R02 · R12 · R13", "S05": "R14", "S06": "R15", "S07": "R16", "S09": "R09 · R14 · R15 · R16"}
clip_records = []
for chapter_id, filename, term in huashu:
    candidates = [shot for shot in all_shots if shot["chapter"] == chapter_id and term in shot["spoken"]]
    if not candidates:
        candidates = [shot for shot in all_shots if shot["chapter"] == chapter_id]
    target = candidates[0]
    asset = ROOT / "media/huashu" / filename
    if not asset.exists():
        continue
    length = probe_duration(asset)
    clip_records.append({"id": f"huashu-{chapter_id.lower()}", "src": f"../media/huashu/{filename}", "start": round(target["start"], 4), "duration": round(min(length, target["end"]-target["start"] + 6.0), 4), "source_ref": source_refs[chapter_id], "caption": target["caption"]})

def seconds(value):
    return f"{value:.4f}".rstrip("0").rstrip(".")

duration_str = seconds(total)
html_parts = [f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><title>光影党史 EP01 · M4 长版</title>
<style>
@font-face{{font-family:GuangyingSans;src:url("../assets/fonts/NotoSansSC-500.woff") format("woff");font-weight:500}}
html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#181516}}
#main{{position:relative;width:1920px;height:1080px;background:#181516;overflow:hidden}}
#sceneCanvas{{position:absolute;inset:0;z-index:0;width:1920px;height:1080px}}
video.huashu{{position:absolute;left:0;top:44px;width:1920px;height:1080px;object-fit:contain;z-index:10}}
.caption{{position:absolute;inset:0;width:1920px;height:1080px;z-index:20}}
.source-label{{position:absolute;inset:0;width:1920px;height:1080px;z-index:30}}
text{{font-family:GuangyingSans,sans-serif;font-weight:500}}
hf-audio-group{{display:none!important}}
</style></head><body>
<div id="main" data-composition-id="guangyingdangshi-ep01-m4" data-start="0" data-duration="{duration_str}" data-width="1920" data-height="1080" data-fps="25">
<canvas id="sceneCanvas" width="1920" height="1080"></canvas>
<hf-audio-group id="voiceover" data-label="Voiceover"></hf-audio-group>
<audio id="narration" class="clip" src="../media/voice/EP01_M4_narration.wav" data-start="0" data-duration="{duration_str}" data-track-index="1" data-audio-group="voiceover"></audio>
<audio id="music-bed" class="clip" src="../media/audio/EP01_M4_music.wav" data-start="0" data-duration="{duration_str}" data-track-index="2" data-audio-group="music" data-fx-carve="{{&quot;enabled&quot;:true,&quot;sources&quot;:[&quot;voiceover&quot;],&quot;strength&quot;:0.4}}"></audio>
''']
for clip in clip_records:
    html_parts.append(f'<video id="{clip["id"]}" class="clip huashu" src="{clip["src"]}" muted playsinline preload="auto" data-start="{seconds(clip["start"])}" data-duration="{seconds(clip["duration"])}" data-track-index="10"></video>\n')
    html_parts.append(f'''<div id="label-{clip["id"]}" class="clip source-label" data-start="{seconds(clip["start"])}" data-duration="{seconds(clip["duration"])}" data-track-index="12">
<svg viewBox="0 0 1920 1080" aria-label="图解动画说明">
<rect x="80" y="72" width="390" height="58" rx="29" fill="#A94542"/>
<text x="275" y="110" text-anchor="middle" fill="#FFF9EF" font-size="24">图解动画 · 非原始史料</text>
<text x="1825" y="1030" text-anchor="end" fill="#181516" font-size="22">依据：{html.escape(clip["source_ref"])}</text>
</svg></div>\n''')

for shot in all_shots:
    caption = html.escape(re.sub(r"\s+", "", shot["caption"]))
    html_parts.append(f'''<div id="caption-{shot["id"]}" class="clip caption" data-start="{seconds(shot["start"])}" data-duration="{seconds(shot["end"]-shot["start"])}" data-track-index="20">
<svg viewBox="0 0 1920 1080" aria-label="旁白字幕"><rect x="96" y="868" width="1725" height="88" rx="4" fill="rgba(10,7,8,.84)"/><rect x="96" y="868" width="8" height="88" fill="#A94542"/><text x="138" y="923" fill="#F6F0E6" font-size="35">{caption}</text></svg></div>\n''')

html_parts.append(f'''</div>
<script src="../node_modules/gsap/dist/gsap.min.js"></script>
<script src="../src/episode-data-m4.js"></script><script src="../src/graphics-m4.js"></script>
<script>(function(){{const id='guangyingdangshi-ep01-m4';if(window.gsap){{const tl=gsap.timeline({{paused:true}});tl.to({{clock:0}},{{clock:{duration_str},duration:{duration_str},ease:'none',onUpdate:function(){{window.renderAt(this.targets()[0].clock)}}}},0);window.__timelines=window.__timelines||{{}};window.__timelines[id]=tl;window.__hfMotionReady=true;}}else{{window.__hfMotionReady=false;}}window.addEventListener('message',e=>{{if(e.data&&e.data.kind==='seek'&&Number.isFinite(e.data.t))window.renderAt(e.data.t)}});const qp=new URLSearchParams(location.search);if(qp.has('t'))window.renderAt(Number(qp.get('t'))||0);}})();</script>
</body></html>''')
(ROOT / "compositions/EP01_M4.html").write_text("".join(html_parts))
print(f"Wrote M4 timeline: {len(all_shots)} shots, {len(clip_records)} Huashu overlays, {total/60:.2f} minutes")
