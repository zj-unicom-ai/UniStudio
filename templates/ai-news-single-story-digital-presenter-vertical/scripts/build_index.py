#!/usr/bin/env python3
"""Generate index.html for this episode from data/sample-episode.json + approved-timing.json.

The narration lengths drive every slot, so re-running voice -> timing -> this
script keeps the film in sync without touching markup.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
stories_doc = json.loads((ROOT / "data" / "sample-episode.json").read_text(encoding="utf-8"))
timing = json.loads((ROOT / "approved-timing.json").read_text(encoding="utf-8"))
manifest = {i["id"]: i["duration_s"] for i in json.loads((ROOT / "voice-manifest.json").read_text(encoding="utf-8"))}

STORIES = stories_doc["stories"]
COVER = stories_doc["cover"]
T = timing["total_duration"]
CD = timing["cover_duration"]

HEAD = """<!doctype html>
<html lang="zh-CN" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <title>__TITLE__</title>
    <script src="./assets/vendor/gsap.min.js"></script>
    <style>
      @font-face {
        font-family: "Noto Sans SC";
        src: url("./assets/fonts/NotoSansSC-VF.ttf") format("truetype-variations");
        font-weight: 100 900; font-style: normal; font-display: block;
      }
      :root {
        --bg:#0B1120; --ink:#F4F6FA; --accent:#37D7E8; --muted:#94A3B8; --card:#1A2433;
        --display:"Noto Sans SC", system-ui, sans-serif;
      }
      * { box-sizing: border-box; }
      html, body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--bg); }
      #root { position: relative; width: 100%; height: 100%; overflow: hidden; isolation: isolate; }
      #root > * { position: absolute; }
      /* the cover/brand layers live inside their scene, not at the root — they need the same absolute base */
      .scene > * { position: absolute; }
      .scene { inset: 0; overflow: hidden; }
      .backdrop { inset: 0; background:
        radial-gradient(72% 40% at 16% 6%, rgba(30,92,168,.34) 0%, rgba(11,17,32,0) 68%),
        radial-gradient(90% 46% at 30% 100%, rgba(22,106,178,.30) 0%, rgba(11,17,32,0) 70%), var(--bg); }

      /* ---------- cover ---------- */
      #cover { z-index: 1; }
      #earth-group { left: 0; right: 0; top: 0; bottom: -18px; z-index: 1; }
      #earth-group img { position: absolute; width: 1765px; height: 1177px; }
      #earth-base { left: -102px; top: 760px; }
      #earth-net { left: -228px; top: 904px; }
      #earth-fx { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
      #star-ring { inset: 0; z-index: 2; overflow: visible; }
      #logo { left: 10px; top: 83px; width: 597px; z-index: 6; }
      #logo img { display: block; width: 100%; height: auto; }
      #date-pill { right: 64px; top: 140px; height: 78px; padding: 0 30px 0 24px; z-index: 6;
        display: flex; align-items: center; gap: 16px; border: 1.5px solid rgba(55,215,232,.55);
        border-radius: 22px; background: linear-gradient(150deg, rgba(26,36,51,.94), rgba(11,17,32,.94));
        box-shadow: inset 0 0 22px rgba(55,215,232,.12), 0 0 26px rgba(22,106,178,.22); }
      #date-pill svg { display: block; width: 34px; height: 34px; flex: none; }
      #date-pill span { color: var(--ink); font-family: var(--display); font-weight: 700;
        font-size: 34px; line-height: 1; letter-spacing: 1.5px; white-space: nowrap; }
      #headline { left: 0; top: 318px; width: 1080px; z-index: 5; display: flex; flex-direction: column; align-items: center; }
      .hl-row { display: block; white-space: nowrap; }
      .hl-em { font-family: var(--display); font-weight: 900; font-size: 176px; line-height: 0.86;
        letter-spacing: -2px; transform: skewX(-8deg); }
      .hl-main { font-family: var(--display); font-weight: 900; font-size: 150px; line-height: 0.86;
        margin-top: 26px; transform: skewX(-8deg) scaleX(0.78); }
      .hl-ink { background-image: linear-gradient(178deg,#fff 4%,#eafcff 42%,#9beeff 70%,var(--accent) 100%);
        -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: var(--ink); }
      #title-flare { left: 90px; top: 858px; width: 900px; height: 3px; z-index: 5; overflow: hidden;
        background: linear-gradient(90deg, rgba(55,215,232,0), rgba(55,215,232,.75) 34%, #fff 50%, rgba(55,215,232,.75) 66%, rgba(55,215,232,0));
        box-shadow: 0 0 24px rgba(55,215,232,.55); }
      /* one bright glint slides along the rule, end to end, on a loop */
      #title-flare .flare-run { position: absolute; left: 0; top: -2px; width: 190px; height: 7px;
        background: radial-gradient(closest-side, rgba(255,255,255,.95), rgba(190,246,255,.55) 55%, rgba(55,215,232,0));
        filter: blur(.4px); }
      #slogan { left: 0; right: 0; top: 902px; height: 62px; z-index: 5; display: flex; align-items: center; justify-content: center; gap: 26px; }
      #slogan i { display: block; width: 104px; height: 1.5px; background: linear-gradient(90deg, rgba(148,163,184,0), rgba(148,163,184,.75)); }
      #slogan i:last-child { background: linear-gradient(90deg, rgba(148,163,184,.75), rgba(148,163,184,0)); }
      #slogan strong { color: var(--ink); font-family: var(--display); font-weight: 600; font-size: 56px; line-height: 1; letter-spacing: 2px; white-space: nowrap; }
      #keywords { left: 0; right: 0; top: 996px; z-index: 5; display: flex; justify-content: center; gap: 30px; }
      .chip { display: flex; align-items: center; gap: 16px; height: 84px; padding: 0 36px;
        border: 1.5px solid rgba(55,215,232,.5); border-radius: 42px;
        background: linear-gradient(150deg, rgba(26,36,51,.92), rgba(11,17,32,.92));
        box-shadow: inset 0 0 18px rgba(55,215,232,.10); }
      .chip b { color: var(--ink); font-family: var(--display); font-weight: 600; font-size: 38px; line-height: 1; letter-spacing: 1px; white-space: nowrap; }
      #presenter { right: 0; bottom: 0; width: 678px; height: 815px; z-index: 7; }
      #presenter video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: right bottom; }
      #veil { inset: 0; z-index: 20; background: var(--bg); }

      /* ---------- story pages ---------- */
      .page { z-index: 10; }
      .sheet { position: absolute; inset: 0; overflow: hidden; transform-origin: 0% 100%; }
      /* one shared backdrop for every story page: the cover paints over it while it is up */
      #body-bg { inset: 0; z-index: 0; background: var(--bg); }
      #body-bg::before { content: ""; position: absolute; inset: 0; opacity: .38;
        background-image: url("./assets/bg/earth-base.png"), url("./assets/bg/earth-network.png");
        background-repeat: no-repeat, no-repeat;
        background-size: 1765px 1177px, 1765px 1177px;
        background-position: -102px 900px, -228px 1044px; }
      #body-bg::after { content: ""; position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(11,17,32,.96) 0%, rgba(11,17,32,.78) 34%, rgba(11,17,32,.52) 62%, rgba(11,17,32,.86) 100%); }
      .pad { position: absolute; left: 56px; right: 56px; top: 64px; bottom: 56px; }
      .chrome-logo { display: block; width: 300px; height: auto; }
      #chrome { z-index: 12; }
      .chrome-space { display: block; height: 123px; }
      .rule { display: block; width: 100%; height: 1px; background: linear-gradient(90deg, rgba(55,215,232,.65), rgba(55,215,232,.05)); margin-top: 22px; }
      .kicker { display: block; margin-top: 34px; color: var(--accent); font-family: var(--display); font-weight: 800; font-size: 30px; letter-spacing: 4px; }
      .ptitle-wrap { position: relative; display: block; margin-top: 16px; overflow: hidden; }
      .ptitle { display: block; color: var(--ink); font-family: var(--display); font-weight: 900; font-size: 92px; line-height: 1.1; letter-spacing: -1px; }
      .sheen { position: absolute; left: -420px; top: 0; width: 340px; height: 100%;
        background: linear-gradient(100deg, transparent 8%, rgba(55,215,232,.30) 38%, rgba(255,255,255,.85) 50%, rgba(55,215,232,.30) 62%, transparent 92%); }
      .stat { position: absolute; left: 0; top: 460px; width: 968px; height: 246px; padding: 28px 40px;
        border: 1px solid rgba(55,215,232,.34); border-radius: 26px;
        background: linear-gradient(135deg, rgba(26,36,51,.94), rgba(11,17,32,.94));
        box-shadow: inset 0 0 30px rgba(55,215,232,.09); }
      .stat em { display: block; font-family: var(--display); font-style: normal; font-weight: 900; font-size: 116px; line-height: 1;
        background-image: linear-gradient(180deg,#fff,#7fe6f6 70%,var(--accent)); -webkit-background-clip: text; background-clip: text;
        -webkit-text-fill-color: transparent; color: var(--ink); }
      .stat u { display: block; margin-top: 10px; text-decoration: none; color: var(--accent); font-family: var(--display); font-weight: 700; font-size: 28px; letter-spacing: 3px; }
      .stat i { display: block; margin-top: 6px; font-style: normal; color: var(--muted); font-family: var(--display); font-weight: 400; font-size: 25px; }
      .facts { position: absolute; left: 0; top: 736px; width: 968px; }
      /* the observation page has no stat card — the facts move up and speak louder */
      .no-stat .facts { top: 330px; }
      .no-stat .fact { margin-bottom: 44px; }
      .no-stat .fact p { font-size: 47px; line-height: 1.5; }
      .no-stat .fact i { min-height: 74px; }
      .fact { display: flex; gap: 22px; margin-bottom: 26px; }
      .fact i { flex: none; display: block; width: 6px; height: 100%; min-height: 62px; border-radius: 3px;
        background: linear-gradient(180deg, var(--accent), rgba(55,215,232,.15)); }
      .fact p { margin: 0; color: var(--ink); font-family: var(--display); font-weight: 500; font-size: 39px; line-height: 1.42; letter-spacing: .5px; }
      .fact p small { display: block; color: var(--muted); font-size: 27px; line-height: 1.5; margin-top: 4px; }
      .src { position: absolute; left: 0; right: 0; bottom: 0; display: flex; align-items: center; gap: 16px;
        padding-top: 20px; border-top: 1px solid rgba(148,163,184,.22); }
      .src b { color: var(--accent); font-family: var(--display); font-weight: 800; font-size: 21px; letter-spacing: 3px; }
      .src span { color: var(--muted); font-family: var(--display); font-weight: 400; font-size: 23px; letter-spacing: .5px; }

      /* ---------- brand outro (sub-composition: 模板/刚哥聊AI/固定片尾) ---------- */
      #gangge-ai-outro { inset: 0; z-index: 40; }
    </style>
  </head>
  <body>
"""

# --- cover markup (mirrors 封面动效模板/index.html, retimed to the narration) ---
NODES = [(111,1211,252),(56,1271,228),(147,1430,252),(572,1277,252),
         (542,1384,234),(535,1552,253),(473,1444,242),(598,1252,226)]
RIM = ("M -40 1153.5 L 17 1147.4 L 74 1143.5 L 131 1142 L 188 1142.8 L 245 1145.9 L 302 1151.2 "
       "L 359 1158.7 L 416 1168.4 L 473 1180.2 L 530 1194.1 L 587 1210.1 L 644 1228.1 L 701 1248.1 "
       "L 758 1270 L 815 1293.8 L 872 1319.5 L 929 1347 L 986 1376.2 L 1020 1394.6")
CHIP_ICONS = [
 '<path d="M12 2.6 21 7.4v9.2L12 21.4 3 16.6V7.4z" /><path d="M3 7.4 12 12l9-4.6M12 12v9.4" />',
 '<path d="M4 20h16M7.5 20v-6M12 20V8M16.5 20v-9" />',
 '<circle cx="12" cy="5" r="2.6" /><circle cx="5" cy="17.5" r="2.6" /><circle cx="19" cy="17.5" r="2.6" /><path d="M10.4 7.1 6.6 15.4M13.6 7.1l3.8 8.3M7.6 17.5h8.8" />',
]

def cover_markup():
    nodes = "\n        ".join(
        f'<circle class="node" cx="{x}" cy="{y}" r="{round(4 + (b-226)*3/27,1)}" />' for x, y, b in NODES
    )
    chips = "\n".join(
        f'''      <div class="chip">
        <svg viewBox="0 0 24 24" fill="none" stroke="#37D7E8" stroke-width="1.6" stroke-linejoin="round" aria-hidden="true">{CHIP_ICONS[i]}</svg>
        <b>{kw}</b>
      </div>'''
        for i, kw in enumerate(COVER["keywords"])
    )
    lines = "\n".join(f'        <div class="hl-row hl-main hl-ink">{ln}</div>' for ln in COVER["lines"])
    return f'''    <section id="cover" class="scene clip" data-start="0" data-duration="{CD}" data-track-index="1">
      <div class="backdrop"></div>
      <div id="earth-group" data-layout-allow-overflow>
        <img id="earth-base" src="./assets/bg/earth-base.png" alt="" aria-hidden="true" />
        <img id="earth-net" src="./assets/bg/earth-network.png" alt="" aria-hidden="true" />
        <svg id="earth-fx" viewBox="0 0 1080 1938" preserveAspectRatio="none" aria-hidden="true">
          <defs>
            <filter id="soft-blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="14" /></filter>
            <linearGradient id="streak" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#EAFCFF" stop-opacity="0" /><stop offset="1" stop-color="#EAFCFF" stop-opacity=".95" /></linearGradient>
          </defs>
          <path id="rim-glow" d="{RIM}" fill="none" stroke="#3FC8EE" stroke-opacity=".5" stroke-width="22" stroke-linecap="round" filter="url(#soft-blur)" />
          <path id="run-1" pathLength="1000" d="M 56 1271 Q 320 1148 598 1252" fill="none" stroke="url(#streak)" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="64 936" />
          <path id="run-2" pathLength="1000" d="M 147 1430 Q 336 1436 535 1552" fill="none" stroke="url(#streak)" stroke-width="3" stroke-linecap="round" stroke-dasharray="48 952" />
          <g id="nodes" fill="#BFF6FF">
        {nodes}
          </g>
        </svg>
      </div>

      <svg id="star-ring" viewBox="0 0 1080 1920" aria-hidden="true">
        <defs>
          <linearGradient id="ring-stroke" x1="0" y1="0" x2="1" y2=".3"><stop offset="0" stop-color="#37D7E8" stop-opacity=".06" /><stop offset=".34" stop-color="#5FD9EF" stop-opacity=".42" /><stop offset=".72" stop-color="#BDF3FF" stop-opacity=".8" /><stop offset="1" stop-color="#37D7E8" stop-opacity=".12" /></linearGradient>
          <filter id="dot-glow" x="-400%" y="-400%" width="900%" height="900%"><feGaussianBlur stdDeviation="7" /></filter>
        </defs>
        <g transform="translate(556 448) rotate(-12)">
          <ellipse rx="478" ry="158" fill="none" stroke="url(#ring-stroke)" stroke-width="2.4" />
          <ellipse rx="418" ry="126" fill="none" stroke="#37D7E8" stroke-opacity=".14" stroke-width="1" />
        </g>
        <circle id="ring-dot-a" r="20" fill="#8FE9FF" opacity=".5" filter="url(#dot-glow)" />
        <circle id="ring-dot-b" r="5" fill="#8FE9FF" opacity=".55" />
      </svg>

      <div id="logo"><img src="./assets/brand/logo-lockup.png" alt="刚哥聊AI GANGGE AI INSIGHT" /></div>
      <div id="date-pill">
        <svg viewBox="0 0 24 24" fill="none" stroke="#37D7E8" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="3" /><path d="M3 10h18M8 3v4M16 3v4" /></svg>
        <span>{stories_doc["date"]}</span>
      </div>

      <div id="headline">
        <div class="hl-row hl-em hl-ink">{COVER["em"]}</div>
{lines}
      </div>
      <div id="title-flare"><i class="flare-run" data-layout-allow-overflow></i></div>
      <div id="slogan"><i></i><strong>{COVER["slogan"]}</strong><i></i></div>
      <div id="keywords">
{chips}
      </div>

    </section>

    <!-- root-level sibling: a <video> with data-start may not live inside a timed ancestor -->
    <div id="presenter">
      <video id="host-cover-video" class="clip" src="./assets/presenter/host-cover-alpha.webm" muted playsinline preload="auto" aria-hidden="true" data-start="0" data-duration="{CD}" data-track-index="2"></video>
    </div>

    <!-- the open fade must also cover #presenter, so it sits at the root, above both -->
    <div id="veil" class="clip" data-start="0" data-duration="{CD}" data-track-index="3"></div>
'''

def page_markup(i, story):
    start = timing["story_starts"][i]
    end = timing["story_ends"][i]
    dur = round(end - start, 3)
    facts = "\n".join(
        f'        <div class="fact"><i></i><p>{f}</p></div>' for f in story["facts"]
    )
    stat = story.get("stat")
    stat_block = (
        f'''      <div class="stat"><em>{stat["value"]}</em><u>{stat["label"]}</u><i>{stat["note"]}</i></div>'''
        if stat else ""
    )
    return f'''    <section id="page-{i+1}" class="page scene clip" data-start="{start}" data-duration="{dur}" data-track-index="{10+i}">
      <div class="sheet{"" if stat else " no-stat"}" id="sheet-{i+1}" data-layout-allow-overlap data-layout-allow-overflow>
        <div class="pad">
          <div class="chrome-space"></div>
          <span class="kicker">{story["kicker"]}</span>
          <div class="ptitle-wrap"><span class="ptitle">{story["title"]}</span><i class="sheen" id="sheen-{i+1}"></i></div>
{stat_block}
          <div class="facts" id="facts-{i+1}">
{facts}
          </div>
          <div class="src"><b>SOURCE</b><span>{story["source"]}</span></div>
        </div>
      </div>
    </section>
'''

# the page chrome lives above every sheet: it stays put while the content turns
CHROME_START = timing["story_starts"][0]
CHROME = '''    <div id="chrome" class="clip" data-start="%s" data-duration="%s" data-track-index="30">
      <div class="pad chrome-pad">
        <img class="chrome-logo" src="./assets/brand/logo-lockup.png" alt="刚哥聊AI GANGGE AI INSIGHT" />
        <i class="rule"></i>
      </div>
    </div>
''' % (CHROME_START, round(timing["brand_start"] + 0.6 - CHROME_START, 3))

brand_start = timing["brand_start"]
brand_dur = round(T - brand_start, 3)
# the series-standard outro ships as a sub-composition: 模板/刚哥聊AI/固定片尾
BRAND = f'''    <div id="gangge-ai-outro" class="clip" data-composition-id="gangge-ai-outro" data-composition-src="compositions/gangge-ai-outro.html" data-start="{brand_start}" data-duration="{brand_dur}" data-track-index="40" data-width="1080" data-height="1920"></div>
'''

audio = ['    <audio id="vo-00" class="clip" src="./assets/voice/00-intro.wav" data-start="%s" data-duration="%s" data-track-index="60"></audio>' % (timing["intro_voice_start"], manifest["00-intro"])]
for i, story in enumerate(STORIES):
    vid = story["voice"]
    audio.append('    <audio id="vo-%d" class="clip" src="./assets/voice/%s.wav" data-start="%s" data-duration="%s" data-track-index="%d"></audio>' % (i + 1, vid, timing["story_voice_starts"][i], manifest[vid], 61 + i))
audio.append('    <audio id="vo-outro" class="clip" src="./assets/voice/99-outro.wav" data-start="%s" data-duration="%s" data-track-index="67"></audio>' % (timing["outro_voice_start"], manifest["99-outro"]))
# page-turn whoosh: one per seam, starting at the overlap
seams = [timing["story_starts"][i] for i in range(len(STORIES))] + [timing["brand_visual_start"]]
for i, s in enumerate(seams):
    audio.append('    <audio id="sfx-%d" class="clip" src="./assets/sfx/page-whoosh.mp3" data-start="%s" data-duration="0.575" data-track-index="%d" data-volume="0.72"></audio>' % (i + 1, round(s - 0.1, 3), 70 + i))

SCRIPT = """
    <script>
      const T = %s, CD = %s;
      const RING = { cx: 556, cy: 448, rx: 478, ry: 158, tilt: -12 };
      const RING_SPIN = 360;
      const rad = (d) => (d * Math.PI) / 180;
      function ringPoint(deg) {
        const t = rad(deg), r = rad(RING.tilt);
        const x = RING.rx * Math.cos(t), y = RING.ry * Math.sin(t);
        return { x: RING.cx + x * Math.cos(r) - y * Math.sin(r), y: RING.cy + x * Math.sin(r) + y * Math.cos(r) };
      }
      const STORY = %s;
      /* daily titles vary in length — shrink the cover lines rather than let them wrap */
      function fitHeadline() {
        const fit = window.__hyperframes && window.__hyperframes.fitTextFontSize;
        if (!fit) return;
        document.querySelectorAll(".hl-row").forEach((row) => {
          const base = parseFloat(getComputedStyle(row).fontSize);
          const squeeze = row.classList.contains("hl-main") ? 0.78 : 1;
          const r = fit(row.textContent.trim(), {
            maxWidth: 980 / squeeze, baseFontSize: base, minFontSize: 84,
            fontWeight: 900, fontFamily: '"Noto Sans SC"', step: 2,
          });
          if (r.fontSize < base) row.style.fontSize = r.fontSize + "px";
        });
      }
      const ready = document.fonts ? document.fonts.ready : Promise.resolve();
      ready.then(() => {
        fitHeadline();
        const tl = gsap.timeline({ paused: true });

        /* cover: veil lifts, headline floats up once, then only the world moves */
        tl.fromTo("#veil", { opacity: 1 }, { opacity: 0, duration: 0.46, ease: "power1.out" }, 0);
        /* the alpha webm composites as its own layer — the veil cannot dim it, so it fades in on its own */
        tl.fromTo("#presenter", { opacity: 0 }, { opacity: 1, duration: 0.46, ease: "power1.out" }, 0);
        tl.fromTo("#earth-group", { scale: 1, y: 0, transformOrigin: "50%% 100%%" },
          { scale: 1.03, y: -11, duration: CD, ease: "none" }, 0);
        tl.fromTo("#rim-glow", { opacity: 0.42 }, { opacity: 0.86, duration: 2.1, ease: "sine.inOut", yoyo: true, repeat: Math.max(1, Math.floor(CD / 2.1)) - 1 }, 0.05);
        tl.fromTo("#run-1", { strokeDashoffset: 0 }, { strokeDashoffset: -1000, duration: CD - 1.2, ease: "none" }, 0.6);
        tl.fromTo("#run-2", { strokeDashoffset: 0 }, { strokeDashoffset: -1000, duration: CD - 1.6, ease: "none" }, 1.0);
        const nodePhases = [0.15, 0.95, 1.72, 0.5, 1.28, 2.05, 0.72, 1.55];
        const nodeCycle = [0.62, 0.78, 0.54, 0.7, 0.66, 0.58, 0.74, 0.6];
        document.querySelectorAll("#nodes .node").forEach((node, i) => {
          gsap.set(node, { opacity: 0.4 });
          const cycles = Math.max(1, Math.floor((CD - nodePhases[i]) / (nodeCycle[i] * 2)));
          tl.to(node, { opacity: 0.95, duration: nodeCycle[i], ease: "sine.inOut", yoyo: true, repeat: cycles - 1 }, nodePhases[i]);
        });
        const dotA = document.getElementById("ring-dot-a"), dotB = document.getElementById("ring-dot-b");
        /* the two lights ride the ellipse: one full lap across the cover, near arc bright, far arc dim */
        const orbit = { a: 2, b: 196 };
        const ringDepth = (deg) => (0.3 + 0.55 * (0.5 + 0.5 * Math.sin(rad(deg)))).toFixed(2);
        tl.to(orbit, { a: 2 + RING_SPIN, b: 196 + RING_SPIN, duration: CD, ease: "none",
          onUpdate() {
            const p = ringPoint(orbit.a); dotA.setAttribute("cx", p.x); dotA.setAttribute("cy", p.y);
            dotA.setAttribute("opacity", ringDepth(orbit.a));
            const q = ringPoint(orbit.b); dotB.setAttribute("cx", q.x); dotB.setAttribute("cy", q.y);
            dotB.setAttribute("opacity", ringDepth(orbit.b));
          } }, 0);
        tl.fromTo("#logo", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power1.out" }, 0.1);
        tl.fromTo("#headline", { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: 0.82, ease: "power2.out" }, 0.16);
        tl.fromTo("#title-flare", { opacity: 0 }, { opacity: 0.9, duration: 0.7, ease: "power1.out" }, 0.34);
        /* a glint keeps sliding along the rule under the title */
        tl.fromTo("#title-flare .flare-run", { x: -200 },
          { x: 910, duration: 2.2, ease: "power1.inOut", repeat: Math.max(1, Math.floor(CD / 2.5)) - 1 }, 0.9);
        tl.fromTo("#date-pill", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.56, ease: "power2.out" }, 0.26);
        tl.fromTo("#slogan", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.56, ease: "power2.out" }, 0.34);
        tl.fromTo("#keywords .chip", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.54, ease: "power2.out", stagger: 0.08 }, 0.42);

        /* the cover hands off: every layer lifts out as page 1 lands on the shared backdrop */
        tl.to("#earth-group, #star-ring, #logo, #date-pill, #headline, #title-flare, #slogan, #keywords, #presenter",
          { opacity: 0, y: -34, duration: 0.6, ease: "power2.in" }, STORY[0].start - 0.06);

        /* each page: land, title clears the blur + one sheen, then facts rise in */
        STORY.forEach((s, i) => {
          const lead = 0.18;
          tl.fromTo("#sheet-" + (i + 1), { x: -74, y: 40, opacity: 0, rotation: -3.2, transformOrigin: "0%% 100%%" },
            { x: 0, y: 0, opacity: 1, rotation: 0, duration: 0.56, ease: "power3.out" }, s.start);
          tl.to("#sheet-" + (i + 1), { x: 58, y: -26, opacity: 0, rotation: 2.4, duration: 0.44, ease: "power2.in" }, s.end - 0.44);
          const t0 = Math.max(s.start + lead, i > 0 ? STORY[i - 1].end : CD);
          tl.fromTo("#page-" + (i + 1) + " .kicker", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, t0);
          tl.fromTo("#page-" + (i + 1) + " .ptitle", { opacity: 0, y: 26, filter: "blur(14px)" },
            { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.42, ease: "power3.out" }, t0 + 0.06);
          tl.fromTo("#sheen-" + (i + 1), { x: 0 }, { x: 1400, duration: 0.62, ease: "power1.inOut" }, t0 + 0.34);
          if (s.stat) {
            tl.fromTo("#page-" + (i + 1) + " .stat", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.42, ease: "power2.out" }, t0 + 0.5);
          }
          tl.fromTo("#facts-" + (i + 1) + " .fact", { opacity: 0, y: 18 },
            { opacity: 1, y: 0, duration: 0.42, ease: "power2.out", stagger: 0.16 }, t0 + (s.stat ? 0.62 : 0.2));
          tl.fromTo("#page-" + (i + 1) + " .src", { opacity: 0 }, { opacity: 1, duration: 0.34, ease: "power1.out" }, t0 + 1.1);
        });

        /* the masthead is fixed chrome: it settles in once and leaves with the last page */
        tl.fromTo("#chrome", { opacity: 0 }, { opacity: 1, duration: 0.45, ease: "power1.out" }, Math.max(STORY[0].start + 0.3, CD));
        tl.to("#chrome", { opacity: 0, duration: 0.45, ease: "power1.in" }, STORY[STORY.length - 1].end + 0.05);

        /* the outro is a sub-composition with its own timeline and sfx */
        window.__timelines["episode"] = tl;
      });
    </script>
  </body>
</html>
""" % (
    T, CD,
    json.dumps([{"start": timing["story_starts"][i], "end": timing["story_ends"][i], "stat": bool(s.get("stat"))} for i, s in enumerate(STORIES)]),
)

out = (HEAD.replace("__TITLE__", "刚哥聊AI · %s · %s" % (stories_doc["date"], COVER["em"]))
    + '    <div id="root" data-composition-id="episode" data-start="0" data-duration="%s" data-width="1080" data-height="1920">\n' % T
    + (
        '    <div id="body-bg" class="clip" data-start="%s" data-duration="%s" data-track-index="0"></div>\n'
        % (timing["story_starts"][0], round(timing["brand_start"] - timing["story_starts"][0], 3))
    )
    + cover_markup()
    + CHROME
    + "".join(page_markup(i, s) for i, s in enumerate(STORIES))
    + BRAND
    + "\n".join(audio)
    + "\n" + SCRIPT)
(ROOT / "index.html").write_text(out, encoding="utf-8")
print("index.html written: %.3fs, cover %.2fs, %d story pages, outro at %.2fs" % (T, CD, len(STORIES), brand_start))
