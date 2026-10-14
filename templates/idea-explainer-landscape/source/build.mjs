// 生成 HyperFrames 合成页（dist/index.html）、浏览器预览页（dist/preview.html）和镜头表（dist/shotlist.csv）。
// 用法：node build.mjs      （有真实配音后，把每页时长写进 timing.json 再重跑一遍）
import fs from "node:fs";
import { EPISODE as E, PAGES } from "./storyboard.mjs";
import { ILLUS } from "./illus.mjs";

const W = 1920, H = 1080, LEAD = 0.35;          // 每页开头留 0.35s，口播再开口
const AMB = "#E8B66A", INK = "#E9E4D8", DIM = "#9AA3AE", LINE = "#2C3642", SEG = "#3A4654", PURPLE = "#B7A2D6";
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const hl = s => esc(s).replace(/\[([^\]]+)\]/g, "<em>$1</em>");
const lines = (s, cls = "ln", plain = false) => s.split("\n").map(x => `<div class="${cls}">${plain ? esc(x) : hl(x)}</div>`).join("");
const count = s => [...s.replace(/\s/g, "")].length;
const f2 = n => Math.round(n * 100) / 100;

const timing = fs.existsSync("timing.json") ? JSON.parse(fs.readFileSync("timing.json", "utf8")) : {};
const errors = [];

// ── 时间轴 ──
let cur = 0;
for (const p of PAGES) {
  p.speech = p.say ? count(p.say) / E.cps : 0;
  const auto = p.fixed ?? (LEAD + p.speech + E.gap + (p.tail ?? 0));
  p.dur = f2(timing[p.id] ?? auto);
  // 有真实配音时长：按它反推这一页的口播时长，逐条出现的时间也随之缩放
  if (timing[p.id] != null && p.say) p.speech = Math.max(1, p.dur - LEAD - E.gap - (p.tail ?? 0));
  p.cps = p.say ? count(p.say) / (p.speech || 1) : E.cps;
  p.start = f2(cur);
  cur += p.dur;
}
const CONTENT_TOTAL = f2(cur);
const OUTRO_DURATION = 4.5;
const OUTRO_START = CONTENT_TOTAL;
const TOTAL = f2(CONTENT_TOTAL + OUTRO_DURATION);

const cueAt = (p, cue, what) => {
  if (typeof cue === "number") return f2(LEAD + cue * p.speech);
  const i = p.say.indexOf(cue);
  if (i < 0) { errors.push(`${p.id} ${what}: 口播里找不到「${cue}」`); return LEAD; }
  return f2(Math.max(1.0, LEAD + count(p.say.slice(0, i)) / p.cps - 0.1));
};

// ── 页面 DOM ──
const illusBox = (key) => {
  if (!ILLUS[key]) { errors.push(`未知插画 ${key}`); return ""; }
  const svg = ILLUS[key].replace(/<(circle|path|rect|ellipse)([^>]*?)class="([^"]*\bd\b[^"]*)"([^>]*?)\/?>/g, (m, tag, a, c, b) =>
    /pathLength/.test(m) ? m : `<${tag}${a}class="${c}"${b} pathLength="1"/>`);
  return `<div class="illus"><div class="fl"><svg viewBox="0 0 400 320" width="660" height="528" fill="none" stroke="${INK}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${svg}</svg></div></div>`;
};

const timed = (cls, at, inner, extra = "") => `<div class="${cls}" data-at="${at}"${extra}>${inner}</div>`;

const render = {
  opening: (p) => `
<img class="bg" src="vendor/cover-bg.jpg" alt="">
<div class="op">
  <div class="op-top"></div>
  <div class="op-mid">
    <div class="op-rule"></div>
    <div class="op-title">${E.show}</div>
    <div class="op-sub">第 ${E.no} 期　${esc(E.title)}</div>
  </div>
  <div class="op-slogan">${esc(E.slogan)}</div>
</div>`,

  point: (p) => {
    const rows = (p.rows || []).map(([t, c]) => timed("row", cueAt(p, c, "row"), hl(t))).join("");
    const fm = p.formula ? timed("formula", f2(Math.max(LEAD + p.speech - 2.4, 2.2)), esc(p.formula)) : "";
    return `<div class="body ${p.illus ? "withIllus" : ""}">
  <div class="textcol"><div class="bar"></div><div class="tx">
    <div class="lbl">${esc(p.label)}</div>
    <h1 class="ttl">${lines(p.title)}</h1>
    <div class="rows">${rows}</div>${fm}
  </div></div>
  ${p.illus ? illusBox(p.illus) : ""}
</div>`;
  },

  quote: (p) => {
    const n = p.quote.split("\n").length;
    const subs = (p.subs || []).map(([t, c]) => timed("sub", cueAt(p, c, "sub"), esc(t))).join("");
    return `<div class="qbg"><svg viewBox="0 0 400 320" width="1280" height="1024" fill="none" stroke="${INK}" stroke-width="1.2" style="opacity:.16">${ILLUS.mark.replace(/class="d"/g, 'class="d" pathLength="1"').replace(/<circle[^>]*class="(a|halo)"[^>]*>/g, "")}</svg></div>
<div class="body q">
  <div class="lbl">${esc(p.label)}</div>
  <h1 class="qt q${Math.min(n, 3)}">${lines(p.quote, "qln")}</h1>
  <div class="subs">${subs}</div>
</div>`;
  },

  ledger: (p) => {
    const cols = p.cols.map((c, ci) => `<div class="col ${ci === 1 ? "colR" : ""}" data-at="${f2(1.0 + ci * 0.25)}">
  <div class="chead">${esc(c.head)}</div>
  ${c.lines.map(([t, cue], li) => timed("cl" + (c.accent === li ? " strong" : ""), cueAt(p, cue, "ledger line"), esc(t))).join("")}
</div>`).join("");
    return `<div class="body led">
  <div class="lbl">${esc(p.label)}</div>
  <h1 class="lttl">${hl(p.title)}</h1>
  <div class="cols">${cols}<div class="mid"></div></div>
</div>`;
  },

  grid4: (p) => `<div class="body led">
  <div class="lbl">${esc(p.label)}</div>
  <h1 class="lttl">${hl(p.title)}</h1>
  <div class="grid">${p.cards.map(c => timed("card", cueAt(p, c.cue, "card"), `<div class="tag">${esc(c.tag)}</div><div class="cq">${esc(c.q)}</div>`)).join("")}</div>
</div>`,

  ending: (p) => `<div class="body end">
  <div class="lbl" data-at="0.2">留一个问题给你</div>
  <div class="ask" data-at="${cueAt(p, p.askCue, "ask")}">${p.ask.map(x => `<div class="aln">${esc(x)}</div>`).join("")}</div>
  <div class="ask2" data-at="${cueAt(p, p.ask2Cue, "ask2")}">${esc(p.ask2)}</div>
  <div class="next" data-at="${cueAt(p, p.nextCue, "next")}">${esc(p.next)}</div>
  <div class="sign" data-at="${cueAt(p, p.signCue, "sign")}">${esc(p.sign)}</div>
</div>`,
};

const pageHtml = PAGES.map((p, i) => `
<section id="${p.id}" class="clip page ${p.type}" data-start="${p.start}" data-duration="${Math.max(0, Number((p.dur - 0.001).toFixed(3)))}" data-track-index="1" data-ch="${p.ch}" data-speech="${f2(p.speech)}">${render[p.type](p)}</section>`).join("\n");

const outroSource = fs.readFileSync(new URL("./yinian-outro-template.html", import.meta.url), "utf8");
const outroTemplate = outroSource.match(/<template>([\s\S]*?)<\/template>/)?.[1];
const outroScript = outroSource.match(/<script>\s*([\s\S]*?)<\/script>\s*<\/template>\s*<\/body>/)?.[1];
if (!outroTemplate || !outroScript) throw new Error("Could not parse reusable outro template");
const outroSubcomposition = `<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><title>${E.show} · 通用片尾</title></head><body><template>${outroTemplate
  .replaceAll("一念三千", E.show)
  .replaceAll("一个念头，想透一个世界", E.slogan)
  .replaceAll("感谢观看 · 下期再见", E.outro || "感谢观看 · 下期再见")
  .replaceAll("assets/fonts/NotoSerifSC-VF.ttf", "../fonts/NotoSerifSC-VF.woff2")
  .replaceAll("assets/fonts/NotoSansSC-VF.ttf", "../fonts/NotoSansSC-VF.woff2")
  .replace('<script src="assets/vendor/gsap.min.js"></script>', "")
  .replaceAll("format('truetype')", "format('woff2')")
  }</template><template><script>${outroScript.replace("(function () {", "(function () {\n  window.__timelines = window.__timelines || {};").replace("if (previous) previous.kill();", "if (previous && typeof previous.kill === \"function\") previous.kill();")}</script></template></body></html>`;
fs.mkdirSync("compositions", { recursive: true });
fs.writeFileSync("compositions/yinian-outro-v1.html", outroSubcomposition.replace("</template><template><script>", "<script>").replace("</script></template></body>", "</script></template></body>"));
const outroMount = `<div id="yinian-outro-host" class="clip" data-composition-id="yinian-outro-v1" data-composition-src="compositions/yinian-outro-v1.html" data-start="${OUTRO_START}" data-duration="${OUTRO_DURATION}" data-track-index="2" data-width="${W}" data-height="${H}"></div>`;

// 章节时间（进度条）
const chap = E.chapters.map((name, ci) => {
  const ps = PAGES.filter(p => p.ch === ci);
  const start = ps[0].start, end = ps[ps.length - 1].start + ps[ps.length - 1].dur;
  return { name, start, end, dur: f2(end - start) };
});
const progress = `<div class="progress persist"><div class="segs">${chap.map((c, i) => `<div class="seg" data-i="${i}" style="flex:${c.dur}"></div>`).join("")}</div>
<div class="segl">${chap.map((c, i) => `<div class="sl" data-i="${i}" style="flex:${c.dur}">${c.name}</div>`).join("")}</div></div>`;

const flow = `<svg class="flow" data-layout-allow-overflow width="${W}" height="${H}" viewBox="0 0 1280 720" aria-hidden="true">
<defs>
<path id="fp1" pathLength="1000" d="M-40 180 C 300 130, 560 230, 840 170 S 1160 120, 1320 190"/>
<path id="fp2" pathLength="1000" d="M-40 250 C 220 190, 460 330, 700 270 S 1100 200, 1320 280"/>
<path id="fp3" pathLength="1000" d="M-40 330 C 260 400, 520 260, 780 340 S 1120 420, 1320 340"/>
<path id="fp4" pathLength="1000" d="M-40 430 C 200 380, 480 500, 760 440 S 1120 380, 1320 450"/>
<path id="fp5" pathLength="1000" d="M-40 520 C 280 580, 540 470, 820 530 S 1140 590, 1320 520"/>
<path id="fp6" pathLength="1000" d="M-40 600 C 240 540, 500 650, 760 600 S 1120 540, 1320 610"/>
</defs>
${[.05, .07, .09, .07, .06, .05].map((o, i) => `<use href="#fp${i + 1}" class="fb" stroke-opacity="${o}"/>`).join("")}
${[1, 2, 3, 4, 5, 6].map(i => `<use href="#fp${i}" class="fx"/>`).join("")}
</svg>`;

const css = `
*{box-sizing:border-box;margin:0;padding:0}
html,body{background:#0d1116}
#stage{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:#151A21;color:${INK};isolation:isolate;
  font-family:'Noto Sans SC',system-ui,sans-serif}
.serif,.ttl,.qt,.lttl,.ask,.op-title,.formula,.cl,.cq{font-family:'Noto Serif SC',serif}
.flow{position:absolute;left:0;top:0;z-index:0;pointer-events:none}
.fb,.fx{fill:none;stroke:${INK};stroke-width:1.3;stroke-linecap:round}
.fx{stroke-opacity:.22;stroke-dasharray:120 880}
.page{position:absolute;left:0;top:0;width:${W}px;height:${H}px;z-index:2;visibility:hidden}
.persist{position:absolute;z-index:3;visibility:hidden}
.hdr{left:144px;right:144px;top:64px;display:flex;justify-content:space-between;font-size:33px;color:${DIM}}
.hdr .no{font-variant-numeric:tabular-nums}
.progress{left:144px;right:144px;bottom:56px}
.segs{display:flex;gap:6px;height:9px}
.seg{background:${SEG};border-radius:5px}
.segl{display:flex;gap:6px;margin-top:14px;font-size:27px;color:${DIM}}
.sl{white-space:nowrap}
.body{position:absolute;left:144px;right:144px;top:132px;bottom:132px;display:flex}
/* 要点页 */
.point .body{align-items:center;justify-content:space-between;gap:48px}
.textcol{display:flex;gap:48px;align-items:stretch;min-width:0}
.withIllus .textcol{width:1000px}
.bar{width:6px;background:${PURPLE};flex:none;transform-origin:50% 0}
.tx{display:flex;flex-direction:column;gap:34px;min-width:0}
.lbl{font-size:40px;color:${DIM};letter-spacing:.04em}
.ttl{font-weight:600;font-size:84px;line-height:1.28}
.ln{white-space:nowrap}
em{font-style:normal;color:${AMB}}
.rows{display:flex;flex-direction:column}
.row{font-size:47px;line-height:1.4;padding:17px 0;border-top:1.5px solid ${LINE};white-space:nowrap}
.formula{font-size:44px;color:${DIM};letter-spacing:.06em;margin-top:10px;font-variant-numeric:tabular-nums}
.illus{flex:none;width:660px;height:528px}
.fl{width:660px;height:528px}
/* 金句页 */
.qbg{position:absolute;left:320px;top:28px;width:1280px;height:1024px;z-index:1}
.q{flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:40px;z-index:2}
.qt{font-weight:600;letter-spacing:.04em}
.q1{font-size:150px;letter-spacing:.14em}.q2{font-size:108px;line-height:1.3}.q3{font-size:88px;line-height:1.32}
.qln{white-space:nowrap}
.subs{display:flex;flex-direction:column;gap:10px;min-height:60px}
.sub{font-size:44px;line-height:1.5;color:${DIM}}
/* 对照页 */
.led{flex-direction:column;gap:34px;justify-content:center}
.lttl{font-weight:600;font-size:68px;line-height:1.3}
.cols{position:relative;display:flex;gap:80px}
.col{flex:1;background:#1D242D;border-radius:20px;padding:44px 52px;display:flex;flex-direction:column;gap:22px;min-height:360px}
.chead{font-size:34px;color:${DIM};letter-spacing:.05em;margin-bottom:6px}
.cl{font-size:50px;line-height:1.45}
.cl.strong{font-weight:700;color:#FFF6E4}
.mid{position:absolute;left:50%;top:44px;bottom:44px;width:2px;background:${LINE}}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:40px}
.card{background:#1D242D;border-radius:20px;padding:36px 44px;display:flex;flex-direction:column;gap:14px;min-height:240px}
.tag{font-size:34px;color:${DIM}}
.cq{font-size:46px;line-height:1.45}
/* 片头 */
.opening{background:#151A21}
.bg{position:absolute;left:0;top:0;width:${W}px;height:${H}px;object-fit:cover}
.op{position:absolute;inset:0;padding:96px 144px;display:flex;flex-direction:column;justify-content:space-between}
.op-mid{display:flex;flex-direction:column;gap:42px}
.op-rule{width:96px;height:6px;background:${AMB};transform-origin:0 50%}
.op-title{font-weight:600;font-size:168px;line-height:1.15;letter-spacing:.08em}
.op-sub{font-size:60px;line-height:1.5}
.op-slogan{font-size:39px;color:${DIM};letter-spacing:.1em}
/* 片尾 */
.end{flex-direction:column;justify-content:center;gap:34px}
.ask{font-weight:600;font-size:78px;line-height:1.4}
.ask2{font-size:46px;color:${DIM}}
.next{font-size:50px;margin-top:44px;padding-top:36px;border-top:1.5px solid ${LINE}}
.sign{font-size:38px;color:${DIM};letter-spacing:.1em;margin-top:6px}
`;

const script = `
document.fonts.ready.then(() => {
  const AMB = "${AMB}", INK = "${INK}", SEGC = "${SEG}", DIM = "${DIM}";
  const stage = document.getElementById("stage");
  const TOTAL = +stage.dataset.duration;
  const tl = gsap.timeline({ paused: true });
  const Q = (s, r = document) => Array.from(r.querySelectorAll(s));
  const reps = (period, span) => Math.max(1, Math.ceil(span / period) - 1);   // 有限次数的往返，不用无限循环

  gsap.set(".page, .persist", { autoAlpha: 0 });

  // 常驻背景：六条线上的光点，整期只有一条补间
  const periods = [28, 24, 32, 22, 34, 26];
  Q(".fx").forEach((el, i) => tl.fromTo(el, { strokeDashoffset: -170 * i }, { strokeDashoffset: -170 * i - 1000 * TOTAL / periods[i], duration: TOTAL, ease: "none" }, 0));

  const rise = (els, at, o = {}) => tl.fromTo(els, { autoAlpha: 0, y: o.y ?? 26 }, { autoAlpha: 1, y: 0, duration: o.d ?? 0.8, ease: "power3.out", stagger: o.s ?? 0 }, at);

  // 插画：描线 → 淡入细节 → 暖光点亮 → 缓慢浮动
  function illus(root, t0, span) {
    const ds = Q(".d", root), fs = Q(".f", root), as = Q(".a", root), hs = Q(".halo", root);
    const each = Math.min(0.12, 1.0 / Math.max(ds.length, 1)), dur = 0.9;
    const drawEnd = ds.length ? each * (ds.length - 1) + dur : 0.4;
    tl.fromTo(root, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4, ease: "power1.out" }, t0);
    if (ds.length) tl.fromTo(ds, { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: dur, ease: "power2.inOut", stagger: each }, t0);
    if (fs.length) tl.fromTo(fs, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.5, ease: "power1.out", stagger: Math.min(0.07, 1.0 / fs.length) }, t0 + drawEnd * 0.55);
    const ta = t0 + drawEnd + 0.1;
    if (as.length) tl.fromTo(as, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.6, ease: "power1.out" }, ta);
    if (hs.length) {
      tl.fromTo(hs, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.8, ease: "power1.out" }, ta);
      tl.fromTo(hs, { opacity: 1 }, { opacity: 0.45, duration: 2.4, ease: "sine.inOut", yoyo: true, repeat: reps(2.4, span) }, ta + 0.9);
    }
    const fl = root.querySelector(".fl");
    if (fl) tl.fromTo(fl, { y: 0 }, { y: -6, duration: 3.6, ease: "sine.inOut", yoyo: true, repeat: reps(3.6, span) }, t0 + 1.2);
    Q(".sway", root).forEach(g => tl.fromTo(g, { x: 0 }, { x: +g.dataset.dx, duration: 3.4, ease: "sine.inOut", yoyo: true, repeat: reps(3.4, span) }, ta));
    Q(".pulse", root).forEach((el, i) => tl.fromTo(el, { opacity: 1 }, { opacity: 0.2, duration: 0.9, ease: "sine.inOut", yoyo: true, repeat: reps(0.9, span) }, ta + 0.3 + i * 0.3));
    Q(".bob", root).forEach(g => tl.fromTo(g, { y: 0 }, { y: -9, duration: 2.4, ease: "sine.inOut", yoyo: true, repeat: reps(2.4, span) }, ta));
    Q(".spin", root).forEach(g => tl.fromTo(g, { rotation: 0, svgOrigin: "200 160" }, { rotation: +g.dataset.deg, svgOrigin: "200 160", duration: span, ease: "none" }, t0));
    Q(".travel", root).forEach(c => {
      const path = root.querySelector("#" + c.dataset.path), L = path.getTotalLength(), pr = { p: 0 };
      tl.fromTo(pr, { p: 0 }, { p: 1, duration: Math.max(4, span * 0.62), ease: "power1.inOut", onUpdate() {
        const q = path.getPointAtLength(L * pr.p); c.setAttribute("cx", q.x); c.setAttribute("cy", q.y);
      } }, t0 + 1.6);
    });
  }

  const pages = Q(".page");
  pages.forEach((p, idx) => {
    const t0 = +p.dataset.start, d = +p.dataset.duration, span = +p.dataset.speech || d, last = idx === pages.length - 1;
    const type = p.classList.contains("opening") ? "opening" : p.classList[2];
    tl.set(p, { autoAlpha: 1, y: 0 }, t0);
    if (!last) tl.fromTo(p, { autoAlpha: 1, y: 0 }, { autoAlpha: 0, y: -14, duration: 0.45, ease: "power2.in" }, t0 + d - 0.5);
    else tl.fromTo(p, { autoAlpha: 1 }, { autoAlpha: 0, duration: 1.2, ease: "power1.in" }, t0 + d - 1.2);

    if (type === "opening") {
      tl.fromTo(Q(".bg", p), { autoAlpha: 1, scale: 1.03 }, { autoAlpha: 1, scale: 1, duration: d, ease: "power1.out" }, t0);
      tl.set(Q(".op-title, .op-sub, .op-slogan"), { autoAlpha: 1, y: 0 }, t0);
      tl.fromTo(Q(".op-rule", p), { scaleX: 0 }, { scaleX: 1, duration: 0.9, ease: "power2.inOut" }, t0 + 0.8);
      return;
    }
    if (type === "point") {
      tl.fromTo(Q(".bar", p), { scaleY: 0 }, { scaleY: 1, duration: 0.8, ease: "power2.inOut" }, t0 + 0.1);
      rise(Q(".lbl", p), t0 + 0.2, { y: 14, d: 0.7 });
      rise(Q(".ln", p), t0 + 0.4, { d: 0.9, s: 0.15 });
      if (Q(".ttl em", p).length) tl.fromTo(Q(".ttl em", p), { color: INK }, { color: AMB, duration: 0.9, ease: "power1.inOut" }, t0 + 1.3);
      Q(".row", p).forEach(r => rise(r, t0 + +r.dataset.at, { y: 22 }));
      Q(".formula", p).forEach(r => rise(r, t0 + +r.dataset.at, { y: 14, d: 0.9 }));
      Q(".illus", p).forEach(il => illus(il, t0 + 0.6, span));
    } else if (type === "quote") {
      const bg = Q(".qbg", p)[0];
      illus(bg, t0 + 0.1, d);
      rise(Q(".lbl", p), t0 + 0.2, { y: 14, d: 0.7 });
      rise(Q(".qln", p), t0 + 0.5, { d: 1.1, s: 0.22, y: 30 });
      if (Q(".qt em", p).length) tl.fromTo(Q(".qt em", p), { color: INK }, { color: AMB, duration: 1.0, ease: "power1.inOut" }, t0 + 1.6);
      Q(".sub", p).forEach(r => rise(r, t0 + +r.dataset.at, { y: 16, d: 0.9 }));
    } else if (type === "ledger" || type === "grid4") {
      rise(Q(".lbl", p), t0 + 0.2, { y: 14, d: 0.7 });
      rise(Q(".lttl", p), t0 + 0.4, { d: 0.9 });
      if (Q(".lttl em", p).length) tl.fromTo(Q(".lttl em", p), { color: INK }, { color: AMB, duration: 0.9, ease: "power1.inOut" }, t0 + 1.3);
      Q(".col", p).forEach(c => rise(c, t0 + +c.dataset.at, { y: 24, d: 0.9 }));
      Q(".chead", p).forEach(c => rise(c, t0 + 1.2, { y: 8, d: 0.7 }));
      Q(".mid", p).forEach(m => tl.fromTo(m, { scaleY: 0 }, { scaleY: 1, duration: 0.9, ease: "power2.inOut" }, t0 + 1.0));
      Q(".cl, .card", p).forEach(r => rise(r, t0 + +r.dataset.at, { y: 20 }));
    } else if (type === "ending") {
      Q("[data-at]", p).forEach(el => rise(el, t0 + +el.dataset.at, { y: 20, d: 1.0 }));
    }
  });

  // 页眉、进度条：片头和片尾不显示
  const first = +pages[1].dataset.start, lastStart = +pages[pages.length - 1].dataset.start;
  Q(".persist").forEach(el => {
    tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.8, ease: "power1.out" }, first);
    tl.fromTo(el, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.6, ease: "power1.in", immediateRender: false }, lastStart - 0.1);
  });
  const chs = JSON.parse(stage.dataset.chapters);
  chs.forEach((c, i) => {
    const seg = Q('.seg[data-i="' + i + '"]')[0], sl = Q('.sl[data-i="' + i + '"]')[0];
    tl.fromTo(seg, { backgroundColor: SEGC }, { backgroundColor: AMB, duration: 0.6 }, c.start + (i ? 0 : 0.6));
    tl.fromTo(seg, { backgroundColor: AMB }, { backgroundColor: SEGC, duration: 0.6, immediateRender: false }, c.end - 0.3);
    tl.fromTo(sl, { color: DIM }, { color: INK, duration: 0.6 }, c.start + (i ? 0 : 0.6));
    tl.fromTo(sl, { color: INK }, { color: DIM, duration: 0.6, immediateRender: false }, c.end - 0.3);
  });

  window.__timelines = window.__timelines || {};
  window.__timelines["${E.id}"] = tl;
  window.dispatchEvent(new Event("yinian-ready"));
}).catch(e => { console.error("BUILD_ERR " + e.message + " " + String(e.stack).slice(0, 300).replace(/\s+/g, " ")); });
`;

const stageHtml = `<div id="stage" data-composition-id="${E.id}" data-width="${W}" data-height="${H}" data-start="0" data-duration="${TOTAL}" data-chapters='${JSON.stringify(chap)}'>
${flow}
<div class="hdr persist"><div>${E.show}</div><div class="no">第 ${E.no} 期</div></div>
${progress}
${pageHtml}
${outroMount}
</div>`;

const fontCss = `<style>${fs.readFileSync("fonts/fonts.css", "utf8").replaceAll('url("', 'url("fonts/')}</style>`;
const index = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=${W}, height=${H}">
<title>《一念三千》第 ${E.no} 期</title>
${fontCss}
<style>${css}</style></head>
<body>
${stageHtml}
<script src="vendor/gsap.min.js"></script>
<script>${script}</script>
</body></html>`;

// ── 预览页：同一份合成 + 播放控制，整体缩放到窗口 ──
const previewCss = `
body{margin:0;background:#0d1116;color:#E9E4D8;font-family:'Noto Sans SC',system-ui,sans-serif;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#view{flex:1;position:relative;overflow:hidden}
#view #stage{position:absolute;left:0;top:0;transform-origin:0 0}
#bar{flex:none;display:flex;align-items:center;gap:10px;padding:10px 14px;background:#10151b;border-top:1px solid #2C3642;font-size:14px;flex-wrap:wrap}
#bar button,#bar select{background:#1D242D;color:#E9E4D8;border:1px solid #2C3642;border-radius:8px;padding:8px 12px;font:inherit;min-height:38px;cursor:pointer}
#bar button.on{border-color:#E8B66A;color:#E8B66A}
#seek{flex:1;min-width:160px;accent-color:#E8B66A}
#tm{font-variant-numeric:tabular-nums;color:#9AA3AE;min-width:96px;text-align:right}
`;
const previewJs = `
(function(){
  const view=document.getElementById("view"), st=document.getElementById("stage");
  function fit(){const s=Math.min(view.clientWidth/${W},view.clientHeight/${H});st.style.transform="scale("+s+")";st.style.left=((view.clientWidth-${W}*s)/2)+"px";st.style.top=((view.clientHeight-${H}*s)/2)+"px";}
  addEventListener("resize",fit);fit();
  const mm=t=>{t=Math.max(0,Math.round(t));return String(Math.floor(t/60)).padStart(2,"0")+":"+String(t%60).padStart(2,"0")};
  window.addEventListener("yinian-ready",()=>{
    const tl=window.__timelines["${E.id}"], T=tl.duration(), seek=document.getElementById("seek"), tm=document.getElementById("tm"), pb=document.getElementById("pb"), sel=document.getElementById("pg");
    seek.max=T;
    const pages=[...document.querySelectorAll(".page")].map(p=>({id:p.id,t:+p.dataset.start}));
    pages.forEach((p,i)=>{const o=document.createElement("option");o.value=p.t;o.textContent=(i+1)+" · "+p.id+" · "+mm(p.t);sel.appendChild(o)});
    let drag=false;
    tl.eventCallback("onUpdate",()=>{if(!drag)seek.value=tl.time();tm.textContent=mm(tl.time())+" / "+mm(T);
      let k=0;pages.forEach((p,i)=>{if(tl.time()>=p.t)k=i});sel.selectedIndex=k;pb.classList.toggle("on",tl.isActive())});
    tl.eventCallback("onComplete",()=>pb.textContent="▶ 播放");
    const play=()=>{if(tl.time()>=T-0.05)tl.time(0);tl.play();pb.textContent="❚❚ 暂停"};
    const pause=()=>{tl.pause();pb.textContent="▶ 播放"};
    pb.onclick=()=>tl.paused()?play():pause();
    seek.oninput=()=>{drag=true;tl.pause();tl.time(+seek.value);pb.textContent="▶ 播放"};
    seek.onchange=()=>{drag=false};
    sel.onchange=()=>{tl.time(+sel.value+0.01)};
    document.querySelectorAll("[data-sp]").forEach(b=>b.onclick=()=>{tl.timeScale(+b.dataset.sp);document.querySelectorAll("[data-sp]").forEach(x=>x.classList.toggle("on",x===b))});
    document.getElementById("prev").onclick=()=>{const t=tl.time();let k=0;pages.forEach((p,i)=>{if(t>p.t+1)k=i});tl.time(pages[k].t+0.01)};
    document.getElementById("next").onclick=()=>{const t=tl.time();const n=pages.find(p=>p.t>t+0.05);if(n)tl.time(n.t+0.01)};
    addEventListener("keydown",e=>{if(e.code==="Space"){e.preventDefault();pb.onclick()}if(e.code==="ArrowRight")document.getElementById("next").onclick();if(e.code==="ArrowLeft")document.getElementById("prev").onclick()});
    tl.time(+(new URLSearchParams(location.search).get("t")||0));
  });
})();
`;
const gf = `<link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Noto+Serif+SC:wght@600;700&display=swap" rel="stylesheet">`;
const preview = (gsapSrc, withGF) => `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>一念三千 第1期 预览</title>
${withGF ? gf : fontCss}
<style>${css}${previewCss}</style></head>
<body>
<div id="view">${stageHtml}</div>
<div id="bar">
<button id="pb">▶ 播放</button><button id="prev">上一页</button><button id="next">下一页</button>
<input id="seek" type="range" min="0" max="${TOTAL}" step="0.1" value="0">
<span id="tm">00:00 / ${Math.floor(Math.round(TOTAL) / 60)}:${String(Math.round(TOTAL) % 60).padStart(2, "0")}</span>
<button data-sp="1" class="on">1×</button><button data-sp="4">4×</button><button data-sp="12">12×</button>
<select id="pg"></select>
</div>
<script src="${gsapSrc}"></script>
<script>${script}</script>
<script>${previewJs}</script>
</body></html>`;

fs.mkdirSync("dist/vendor", { recursive: true });
fs.mkdirSync("dist/fonts", { recursive: true });
fs.copyFileSync("vendor/gsap.min.js", "dist/vendor/gsap.min.js");
fs.copyFileSync("vendor/cover-bg.jpg", "dist/vendor/cover-bg.jpg");
fs.writeFileSync("dist/index.html", index);
fs.writeFileSync("dist/preview.html", preview("vendor/gsap.min.js", false).replace(` data-composition-id="${E.id}"`, ""));
fs.writeFileSync("dist/preview-web.html", preview("https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js", true));
fs.writeFileSync("dist/fonts/fonts.css", `/* 渲染机器没有网络时，把字体文件放进本目录，文件名与下面一致即可。
   推荐：Noto Serif SC（SemiBold 600）、Noto Sans SC（Regular 400 / Medium 500 / Bold 700）。 */
@font-face{font-family:"Noto Serif SC";font-weight:600;font-display:block;src:url("NotoSerifSC-SemiBold.woff2") format("woff2")}
@font-face{font-family:"Noto Sans SC";font-weight:400;font-display:block;src:url("NotoSansSC-Regular.woff2") format("woff2")}
@font-face{font-family:"Noto Sans SC";font-weight:700;font-display:block;src:url("NotoSansSC-Bold.woff2") format("woff2")}
`);

const mmss = t => { const s = Math.round(t); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };
const csv = ["序号,页面,章节,类型,开始,时长(秒),口播字数,标题或金句,插画"].concat(PAGES.map((p, i) =>
  [i + 1, p.id, E.chapters[p.ch], { opening: "片头", point: "要点页", quote: "金句页", ledger: "对照页", grid4: "四宫格", ending: "片尾" }[p.type],
    mmss(p.start), p.dur, p.say ? count(p.say) : 0, `"${(p.title || p.quote || p.ask?.join("") || E.show).replace(/\n/g, "").replace(/[\[\]]/g, "")}"`, p.illus || ""].join(","))).join("\n");
fs.writeFileSync("dist/shotlist.csv", "﻿" + csv);
fs.writeFileSync("dist/pages.json", JSON.stringify(PAGES.map(p => ({ id: p.id, ch: p.ch, type: p.type, start: p.start, dur: p.dur })), null, 1));

const chars = PAGES.reduce((a, p) => a + (p.say ? count(p.say) : 0), 0);
console.log(`页数 ${PAGES.length}，口播 ${chars} 字，总长 ${mmss(TOTAL)}（${TOTAL}s），按 ${E.cps} 字/秒`);
console.log("章节：" + chap.map(c => `${c.name} ${mmss(c.start)}–${mmss(c.end)}`).join("　"));
const used = new Set(PAGES.map(p => p.illus).filter(Boolean));
console.log(`插画 ${used.size} 种：${[...used].join(" ")}`);
if (errors.length) { console.log("\n需要修的问题：\n" + errors.join("\n")); process.exitCode = 1; }
