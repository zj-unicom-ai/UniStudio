// 插画库：viewBox 0 0 400 320，纸白细线 + 每幅一处赭金。
// 动效约定（class）：
//   d     线条，按 DOM 顺序“描”出来（stroke-dashoffset）
//   f     淡入（描完约 60% 时开始，依次错开）
//   a     赭金强调，最后淡入
//   halo  光晕，随强调出现，之后缓慢呼吸
//   sway  轻轻横向漂（旗、风线）
//   pulse 声波一类，依次明暗
//   bob   上下轻浮（水滴）
//   spin  极缓慢转动（标志环）
//   travel 琥珀点沿 data-path 指定的曲线走完
const INK = "#E9E4D8", AMB = "#E8B66A", BG = "#151A21", PANEL = "#1D242D";

const ringDots = (cx, cy, r, n, rad, attrs = "", first = "") =>
  Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / n;
    const x = (cx + r * Math.cos(a)).toFixed(1), y = (cy + r * Math.sin(a)).toFixed(1);
    return `<circle class="f" cx="${x}" cy="${y}" r="${rad}" ${i === 0 && first ? first : attrs}/>`;
  }).join("");

const pt = (cx, cy, r, deg) => {
  const a = (deg * Math.PI) / 180;
  return [(cx + r * Math.cos(a)).toFixed(1), (cy + r * Math.sin(a)).toFixed(1)];
};

export const ILLUS = {
  // 对话气泡：同事路过，“我再想想”
  bubble: `
<path class="d" d="M60 296 H340" stroke-opacity=".35"/>
<rect class="d" x="214" y="186" width="106" height="72" rx="6" stroke-opacity=".5"/>
<path class="d" d="M267 258 V282 M244 282 H290" stroke-opacity=".5"/>
<path class="d" d="M70 56 H208 A24 24 0 0 1 232 80 V118 A24 24 0 0 1 208 142 H128 L92 170 V142 H70 A24 24 0 0 1 46 118 V80 A24 24 0 0 1 70 56 Z"/>
<circle class="f" cx="100" cy="99" r="6" fill="${INK}" stroke="none" fill-opacity=".8"/>
<circle class="f" cx="139" cy="99" r="6" fill="${INK}" stroke="none" fill-opacity=".8"/>
<circle class="a" cx="178" cy="99" r="6" fill="${AMB}" stroke="none"/>`,

  // 念头一个接一个，越长越大
  grow: `
<circle class="halo" cx="300" cy="170" r="84" stroke-opacity=".14"/>
<circle class="halo" cx="300" cy="170" r="104" stroke-opacity=".08"/>
<path class="d" d="M82 170 H138 M196 170 H236" stroke-dasharray="" stroke-opacity=".45"/>
<circle class="d" cx="70" cy="170" r="12" fill="none"/>
<circle class="d" cx="170" cy="170" r="30" stroke-opacity=".8"/>
<circle class="d" cx="300" cy="170" r="64" stroke-opacity=".65"/>
<circle class="f" cx="300" cy="170" r="42" stroke-opacity=".25"/>
<circle class="a" cx="70" cy="170" r="6" fill="${AMB}" stroke="none"/>`,

  // 同一句话，两个世界
  twoworlds: `
<path class="d" d="M200 52 V268" stroke-dasharray="" stroke-opacity=".25"/>
<circle class="d" cx="136" cy="160" r="82" stroke-opacity=".65"/>
<circle class="d" cx="264" cy="160" r="82" stroke="${AMB}"/>
<circle class="f" cx="136" cy="160" r="7" fill="${INK}" stroke="none" fill-opacity=".85"/>
<circle class="a" cx="264" cy="160" r="7" fill="${AMB}" stroke="none"/>
<circle class="halo" cx="264" cy="160" r="26" stroke="${AMB}" stroke-opacity=".45"/>`,

  // 同一间办公室，三个世界
  three: `
<path class="d" d="M40 262 H360" stroke-opacity=".3"/>
<circle class="d" cx="78" cy="160" r="52" stroke-opacity=".6"/>
<circle class="d" cx="200" cy="160" r="52" stroke-opacity=".6"/>
<circle class="d" cx="322" cy="160" r="52" stroke-opacity=".6"/>
<circle class="f" cx="78" cy="160" r="6" fill="${INK}" stroke="none" fill-opacity=".8"/>
<circle class="f" cx="322" cy="160" r="6" fill="${INK}" stroke="none" fill-opacity=".8"/>
<circle class="a" cx="200" cy="160" r="6" fill="${AMB}" stroke="none"/>`,

  // 一个人的周末夜
  room: `
<path class="d" d="M40 292 H360" stroke-opacity=".45"/>
<rect class="d" x="64" y="52" width="124" height="148" rx="4" stroke-opacity=".7"/>
<path class="d" d="M126 52 V200 M64 126 H188" stroke-opacity=".4"/>
<path class="d" d="M156 82 A20 20 0 1 0 170 118 A15 15 0 0 1 156 82 Z" stroke-opacity=".8"/>
<path class="d" d="M70 292 V246 H218 V292 M70 246 V222 H98 V246" stroke-opacity=".6"/>
<path class="d" d="M286 292 H334 M310 292 V186" stroke-opacity=".7"/>
<path class="d" d="M280 186 L292 140 H328 L340 186 Z"/>
<path class="a" d="M280 186 L292 140 H328 L340 186 Z" fill="${AMB}" fill-opacity=".14" stroke="none"/>
<circle class="halo" cx="310" cy="190" r="52" fill="${AMB}" fill-opacity=".05" stroke="none"/>
<circle class="a" cx="310" cy="166" r="5" fill="${AMB}" stroke="none"/>`,

  // 事件 → 念头 → 世界
  flow: `
<circle class="d" cx="62" cy="160" r="14" stroke-opacity=".7"/>
<path class="d" d="M86 160 H138 M130 152 L138 160 L130 168" stroke-opacity=".5"/>
<circle class="d" cx="178" cy="160" r="26" stroke="${AMB}"/>
<path class="d" d="M214 160 H252 M244 152 L252 160 L244 168" stroke-opacity=".5"/>
<circle class="d" cx="326" cy="160" r="60" stroke-opacity=".6"/>
<circle class="f" cx="326" cy="160" r="40" stroke-opacity=".25"/>
<circle class="f" cx="326" cy="160" r="20" stroke-opacity=".15"/>
<circle class="a" cx="178" cy="160" r="7" fill="${AMB}" stroke="none"/>`,

  // 山、寺、月：智顗与天台
  mountain: `
<path class="d" d="M18 286 L110 160 L158 218 L246 82 L330 214 L382 286" stroke-opacity=".8"/>
<path class="d" d="M18 286 H382" stroke-opacity=".3"/>
<path class="d" d="M60 240 L110 206 L176 262" stroke-opacity=".3"/>
<path class="d" d="M104 160 V146 M92 146 H128 M98 146 L110 130 L122 146" stroke-opacity=".7"/>
<path class="d" d="M286 128 C296 120, 310 120, 322 126" stroke-opacity=".3"/>
<circle class="a" cx="318" cy="64" r="16" fill="${AMB}" stroke="none"/>
<circle class="halo" cx="318" cy="64" r="32" stroke="${AMB}" stroke-opacity=".4"/>`,

  // 标志：一点、三环
  mark: `
<g class="spin" data-deg="-24"><circle class="d" cx="200" cy="160" r="46" stroke-opacity=".9"/></g>
<g class="spin" data-deg="18"><circle class="d" cx="200" cy="160" r="78" stroke-opacity=".6"/></g>
<g class="spin" data-deg="-12"><circle class="d" cx="200" cy="160" r="112" stroke-opacity=".35"/></g>
<circle class="a" cx="200" cy="160" r="10" fill="${AMB}" stroke="none"/>
<circle class="halo" cx="200" cy="160" r="22" stroke="${AMB}" stroke-opacity=".5"/>`,

  // 十种状态：一圈十个点
  ten: `
<circle class="d" cx="200" cy="160" r="100" stroke-opacity=".2"/>
${ringDots(200, 160, 100, 10, 12, `fill="${INK}" fill-opacity=".7" stroke="none"`, `fill="${AMB}" stroke="none"`)}
<circle class="f" cx="200" cy="160" r="5" fill="${INK}" stroke="none" fill-opacity=".8"/>`,

  // 互具：十个点，每个点又围着十个点
  ten100: (() => {
    const big = Array.from({ length: 10 }, (_, i) => pt(200, 160, 100, -90 + i * 36));
    const rings = big.map(([x, y], i) =>
      `<circle class="f" cx="${x}" cy="${y}" r="18" stroke-width="3" stroke-dasharray="0 11.31" ${i === 0 ? `stroke="${AMB}"` : `stroke-opacity=".65"`}/>`).join("");
    const cores = big.map(([x, y], i) =>
      `<circle class="f" cx="${x}" cy="${y}" r="6" ${i === 0 ? `fill="${AMB}" stroke="${AMB}"` : `fill="${BG}"`}/>`).join("");
    return `<circle class="d" cx="200" cy="160" r="100" stroke-opacity=".18"/>${rings}${cores}
<circle class="f" cx="200" cy="160" r="16" stroke-opacity=".5"/><circle class="f" cx="200" cy="160" r="5" fill="${INK}" stroke="none"/>`;
  })(),

  // 十如是：一个核心，十个侧面
  facets: (() => {
    const spokes = Array.from({ length: 10 }, (_, i) => {
      const a = -90 + i * 36, [x1, y1] = pt(200, 160, 44, a), [x2, y2] = pt(200, 160, 92, a);
      return `<path class="d" d="M${x1} ${y1} L${x2} ${y2}" stroke-opacity=".6"/>`;
    }).join("");
    const ends = Array.from({ length: 10 }, (_, i) => {
      const [x, y] = pt(200, 160, 106, -90 + i * 36);
      return `<circle class="f" cx="${x}" cy="${y}" r="7" ${i === 0 ? `stroke="${AMB}"` : `stroke-opacity=".7"`}/>`;
    }).join("");
    return `<circle class="d" cx="200" cy="160" r="30"/>${spokes}${ends}<circle class="a" cx="200" cy="160" r="8" fill="${AMB}" stroke="none"/>`;
  })(),

  // 三世间：身心、众生、环境
  layers: (() => {
    const mid = Array.from({ length: 8 }, (_, i) => {
      const [x, y] = pt(200, 160, 78, -90 + i * 45);
      return `<circle class="f" cx="${x}" cy="${y}" r="5" fill="${INK}" fill-opacity=".6" stroke="none"/>`;
    }).join("");
    const ticks = Array.from({ length: 24 }, (_, i) => {
      const [x1, y1] = pt(200, 160, 118, i * 15), [x2, y2] = pt(200, 160, 128, i * 15);
      return `M${x1} ${y1} L${x2} ${y2}`;
    }).join(" ");
    return `<circle class="d" cx="200" cy="160" r="36" stroke-opacity=".8"/><circle class="d" cx="200" cy="160" r="78" stroke-opacity=".45"/>
${mid}<circle class="d" cx="200" cy="160" r="118" stroke-opacity=".25"/><path class="f" d="${ticks}" stroke-opacity=".3"/>
<circle class="a" cx="200" cy="160" r="9" fill="${AMB}" stroke="none"/>`;
  })(),

  // 一天之内，走好几个来回
  path: `
<path class="f" d="M24 250 H376 M24 170 H376 M24 90 H376" stroke-dasharray="2 9" stroke-opacity=".28"/>
<path id="daypath" class="d" d="M30 250 C84 250, 96 90, 160 90 S226 220, 276 188 S330 90, 372 84" stroke-opacity=".85"/>
<circle class="f" cx="30" cy="250" r="5" fill="${INK}" stroke="none" fill-opacity=".6"/>
<circle class="f" cx="160" cy="90" r="5" fill="${INK}" stroke="none" fill-opacity=".6"/>
<circle class="f" cx="372" cy="84" r="5" fill="${INK}" stroke="none" fill-opacity=".6"/>
<circle class="travel a" data-path="daypath" r="9" cx="30" cy="250" fill="${AMB}" stroke="none"/>`,

  // 误解：被划掉的一张卡
  myth: `
<rect class="d" x="96" y="60" width="208" height="200" rx="14" stroke-opacity=".7"/>
<path class="d" d="M128 112 H236 M128 148 H272 M128 184 H210" stroke-opacity=".35"/>
<path class="a" d="M118 224 L282 96" stroke="${AMB}" stroke-width="5"/>`,

  // 给这一念找邻居
  neighbors: (() => {
    const near = [[-150, 96], [-95, 112], [-35, 100], [25, 110], [85, 98], [150, 108]].map(([deg, r]) => pt(200, 160, r, deg));
    const lines = near.map(([x, y]) => `<path class="d" d="M200 160 L${x} ${y}" stroke-dasharray="" stroke-opacity=".28"/>`).join("");
    const dots = near.map(([x, y]) => `<circle class="f" cx="${x}" cy="${y}" r="9" stroke-opacity=".8"/>`).join("");
    return `${lines}<circle class="d" cx="200" cy="160" r="28" stroke="${AMB}"/>${dots}<circle class="a" cx="200" cy="160" r="10" fill="${AMB}" stroke="none"/>`;
  })(),

  // 暂停键
  pause: `
<circle class="halo" cx="200" cy="160" r="116" stroke-opacity=".12"/>
<circle class="d" cx="200" cy="160" r="90" stroke-opacity=".75"/>
<rect class="a" x="166" y="116" width="24" height="88" rx="6" fill="${AMB}" stroke="none"/>
<rect class="a" x="210" y="116" width="24" height="88" rx="6" fill="${AMB}" stroke="none"/>`,

  // 七天，七个点
  seven: `
<path class="d" d="M40 230 H360" stroke-opacity=".3"/>
${Array.from({ length: 7 }, (_, i) => `<circle class="d" cx="${58 + i * 47}" cy="170" r="17" stroke-opacity=".7"/>`).join("")}
${Array.from({ length: 6 }, (_, i) => `<circle class="f" cx="${58 + i * 47}" cy="170" r="6" fill="${INK}" fill-opacity=".75" stroke="none"/>`).join("")}
<circle class="a" cx="340" cy="170" r="7" fill="${AMB}" stroke="none"/>
<path class="d" d="M58 230 V240 M105 230 V240 M152 230 V240 M199 230 V240 M246 230 V240 M293 230 V240 M340 230 V240" stroke-opacity=".4"/>`,

  // 一盏灯：不是让你一个人硬扛
  lantern: `
<path class="d" d="M200 36 V68" stroke-opacity=".6"/>
<path class="d" d="M164 68 H236 L226 92 H174 Z" stroke-opacity=".8"/>
<path class="d" d="M174 92 C148 132 148 192 174 232 H226 C252 192 252 132 226 92"/>
<path class="d" d="M168 232 H232 V250 H168 Z" stroke-opacity=".8"/>
<path class="d" d="M60 292 H340" stroke-opacity=".35"/>
<path class="a" d="M200 118 C190 138, 184 150, 184 166 A16 16 0 0 0 216 166 C216 150, 210 138, 200 118 Z" fill="${AMB}" stroke="${AMB}"/>
<circle class="halo" cx="200" cy="164" r="62" fill="${AMB}" fill-opacity=".06" stroke="none"/>
<circle class="halo" cx="200" cy="164" r="40" fill="${AMB}" fill-opacity=".08" stroke="none"/>`,

  // ── 取自方向稿 ──
  overtime: `
<circle class="halo" cx="226" cy="187" r="54" fill="${AMB}" fill-opacity=".04" stroke="none"/>
<circle class="halo" cx="226" cy="187" r="34" fill="${AMB}" fill-opacity=".07" stroke="none"/>
<path class="d" d="M40 300 H360" stroke-opacity=".5"/>
<path class="d" d="M52 300 V198 H108 V300" stroke-opacity=".55"/>
<path class="d" d="M300 300 V150 H356 V300" stroke-opacity=".55"/>
<path class="d" d="M120 300 V76 H290 V300"/>
<g class="f" stroke-opacity=".3"><path d="M68 218 H80 M86 218 H98 M68 240 H80 M86 240 H98 M316 172 H328 M334 172 H346 M316 194 H328 M334 194 H346 M316 216 H328 M334 216 H346"/></g>
<g class="f" stroke-opacity=".5">${[96, 136, 176, 216, 256].flatMap(y => [138, 176, 214, 252].map(x => [x, y])).filter(([x, y]) => !(x === 214 && y === 176) && !(x === 214 && y === 96 && false) && !(y === 176 && x === 214)).filter(([x, y]) => !(y === 176 && x === 214)).map(([x, y]) => `<rect x="${x}" y="${y}" width="24" height="22" rx="2"/>`).join("")}</g>
<circle class="d" cx="330" cy="62" r="16" stroke-opacity=".8"/>
<rect class="a" x="214" y="176" width="24" height="22" rx="2" fill="${AMB}" stroke="${AMB}"/>
<circle class="a" cx="226" cy="185" r="3.5" fill="${BG}" stroke="none"/>
<path class="a" d="M219 198 Q219 192 226 192 Q233 192 233 198 Z" fill="${BG}" stroke="none"/>`,

  phone: `
<rect class="d" x="150" y="58" width="100" height="200" rx="18"/>
<path class="d" d="M186 72 H214" stroke-opacity=".5"/>
<circle class="d" cx="200" cy="124" r="24" stroke-opacity=".7"/>
<path class="f" d="M178 170 H222 M186 186 H214" stroke-opacity=".45"/>
<circle class="f" cx="172" cy="226" r="12" stroke-opacity=".6"/>
<path class="d pulse" d="M262.3 46.2 A36 36 0 0 1 285.9 76.9" stroke-opacity=".8"/>
<path class="d pulse" d="M270.5 23.6 A60 60 0 0 1 309.8 74.8" stroke-opacity=".55"/>
<path class="d pulse" d="M293 5.5 A86 86 0 0 1 335.7 72.5" stroke-opacity=".35"/>
<path class="d" d="M60 296 H340" stroke-opacity=".35"/>
<circle class="a" cx="200" cy="124" r="5" fill="${AMB}" stroke="none"/>
<circle class="a" cx="228" cy="226" r="12" stroke="${AMB}"/>`,

  flag: `
<path class="d" d="M130 58 V292"/>
<path class="d" d="M98 292 H164" stroke-opacity=".6"/>
<circle class="f" cx="130" cy="54" r="4" fill="${INK}" stroke="none"/>
<g class="sway" data-dx="6">
<path class="f" d="M134 70 C170 56, 200 92, 238 74 S292 60, 312 76 V138 C290 124, 262 152, 232 138 S170 124, 134 140 Z" fill="${PANEL}"/>
<circle class="a" cx="222" cy="106" r="6" fill="${AMB}" stroke="none"/>
<circle class="halo" cx="222" cy="106" r="14" stroke="${AMB}" stroke-opacity=".55"/>
</g>
<g class="sway" data-dx="-8">
<path class="d" d="M28 108 C52 98, 76 118, 100 108" stroke-opacity=".5"/>
<path class="d" d="M18 150 C48 138, 80 162, 112 150" stroke-opacity=".4"/>
<path class="d" d="M34 192 C58 184, 80 200, 104 192" stroke-opacity=".3"/>
<path class="d" d="M326 100 C342 94, 358 106, 374 100" stroke-opacity=".35"/>
</g>`,

  tree: `
<path class="d" d="M112 292 C118 262, 150 250, 186 252 C226 246, 276 258, 288 292 Z" fill="none" stroke-opacity=".8"/>
<path class="d" d="M200 252 C194 220, 212 192, 200 160"/>
<path class="d" d="M203 196 C180 184, 160 164, 142 136" stroke-opacity=".8"/>
<path class="d" d="M198 172 C182 160, 172 146, 166 124" stroke-opacity=".8"/>
<path class="d" d="M205 200 C232 188, 254 168, 270 140" stroke-opacity=".8"/>
<path class="d" d="M200 168 C222 156, 238 142, 244 118" stroke-opacity=".8"/>
<path class="d" d="M200 160 C198 138, 204 112, 214 90" stroke-opacity=".8"/>
<g class="f" stroke-opacity=".4"><circle cx="140" cy="132" r="6"/><circle cx="164" cy="118" r="6"/><circle cx="176" cy="144" r="6"/><circle cx="152" cy="152" r="6"/></g>
<g class="a"><circle cx="272" cy="136" r="6" fill="${AMB}" stroke="${AMB}"/><circle cx="246" cy="114" r="6" fill="${AMB}" stroke="${AMB}"/><circle cx="236" cy="142" r="6" fill="${AMB}" stroke="${AMB}"/><circle cx="262" cy="160" r="6" fill="${AMB}" stroke="${AMB}"/><circle cx="216" cy="88" r="6" fill="${AMB}" stroke="${AMB}"/><circle cx="206" cy="110" r="6" fill="${AMB}" stroke="${AMB}"/></g>`,

  drop: `
<ellipse class="d" cx="200" cy="250" rx="130" ry="24" stroke-opacity=".45"/>
<ellipse class="d" cx="200" cy="250" rx="84" ry="15" stroke-opacity=".3"/>
<path class="f" d="M200 184 V238" stroke-dasharray="2 9" stroke-opacity=".6"/>
<g class="bob a"><path d="M200 84 C200 84, 176 124, 176 144 A24 24 0 0 0 224 144 C224 124, 200 84, 200 84 Z" fill="${AMB}" stroke="${AMB}"/>
<path d="M190 146 A12 12 0 0 0 198 158" stroke="${BG}" stroke-opacity=".55"/></g>`,
};
