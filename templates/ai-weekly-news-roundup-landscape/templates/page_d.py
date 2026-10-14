"""D 数据对比。

纸白底。左侧：大数字（结论）+ 标题 + 说明；右侧：对比条形图，旧版本墨蓝、新版本黄色。
数字滚动与条形图生长用 proxy onUpdate，seek 安全。
"""
from __future__ import annotations
import re
from common import (
    F_MONO, PAPER, INK, HI, BODY_TEXT, MARGIN,
    topbar, progress_html, fmt_date_dot, build_page,
)

D = 10


def _visual_units(s: str) -> float:
    return sum(0.55 if ord(c) < 0x2000 else 1.0 for c in s)


def page_css(big: str = "0.0") -> str:
    # 大数字宽度自适应：约 780px 内不换行不重叠
    units = _visual_units(big)
    num_font = 320 if units * 320 <= 780 else max(180, int(780 / units / 5) * 5)
    return f"""
#root {{ background:{PAPER}; color:{INK}; }}

/* 左侧大数字 */
.d-big {{ position:absolute; left:{MARGIN}px; top:230px; }}
.d-big .num {{
  margin:70px 0 0; font-family:{F_MONO}; font-weight:700;
  font-size:{num_font}px; line-height:1; letter-spacing:-.04em;
  white-space:nowrap; max-width:800px;
}}
.d-big .num mark {{
  background:linear-gradient(transparent 60%,{HI} 60% 96%,transparent 96%);
  color:inherit;
}}
.d-big h4 {{ margin:55px 0 0; font-size:54px; font-weight:900; line-height:1.3; max-width:653px; }}
.d-big p {{ margin-top:23px; font-size:35px; color:{BODY_TEXT}; max-width:653px; }}

/* 右侧图表 */
.d-chart {{
  position:absolute; right:{MARGIN}px; top:259px; width:845px;
  background:#fff; padding:46px 50px; box-shadow:6px 6px 0 {INK};
}}
.d-chart .t {{ font-family:{F_MONO}; font-size:27px; letter-spacing:.08em; color:#5C6B78; }}
.bar-r {{ margin-top:42px; }}
.bar-r .l {{ display:flex; justify-content:space-between; font-weight:700; font-size:36px; }}
.bar-r .l .v {{ font-family:{F_MONO}; }}
.bar-r .tr {{ margin-top:15px; height:69px; background:#E3E8E6; }}
.bar-r .fl {{ display:block; height:100%; width:100%; background:{INK}; transform-origin:left center; }}
.bar-r.new .fl {{ background:{HI}; box-shadow:inset 0 0 0 3px {INK}; }}
.d-chart .ex {{ margin-top:46px; font-family:{F_MONO}; font-size:25px; color:#5C6B78; line-height:1.5; }}
"""


def render_d(item, idx, total, date, prefix: float = 0, suffix: float = 0):
    comp_id = f"d-{item['id']}"
    dd = item.get("data")
    if not dd:
        raise ValueError(f"D 页 {item['id']} 缺少 data 字段")

    date_dot = fmt_date_dot(date)
    src = f"来源 {item['source']} · {date_dot}"
    cnt = f"第 {idx} 条 <i>/</i> {total:02d}"

    mm = re.match(r"^([\d.]+)(.*)$", dd["big"])
    if not mm:
        raise ValueError(f"D 页大数字无法解析：{dd['big']}")
    big_num = float(mm.group(1))
    big_suffix = mm.group(2)
    big_dec = len(mm.group(1).split(".")[1]) if "." in mm.group(1) else 0

    bars = dd["bars"]
    bar_html = []
    for bi, (label, val) in enumerate(bars):
        if not (0 <= val <= 100):
            raise ValueError(f"D 页 {item['id']} bar 值越界：{val}")
        cls = "bar-r new" if bi == len(bars) - 1 else "bar-r"
        bar_html.append(
            f'<div class="{cls}"><div class="l"><span>{label}</span><span class="v" id="v-{bi}">0</span></div>'
            f'<div class="tr"><div class="fl" id="fl-{bi}"></div></div></div>'
        )

    body = f"""
{topbar(src, cnt)}
<div class="d-big">
  <span class="chip dk">数据</span>
  <div class="num"><mark id="big-num">0.0{big_suffix}</mark></div>
  <h4>{dd['title']}</h4>
  <p>{dd['note']}</p>
</div>
<div class="d-chart hard">
  <div class="t">{dd.get('chart', '相对值 / %')}</div>
  {"".join(bar_html)}
  <div class="ex">{dd.get('ex', '数据来源见顶栏来源标注')}</div>
</div>
{progress_html(idx, total)}
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

tl.set(q('.bar'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.prog'), {{autoAlpha:0}}, 0);
tl.set(q('.d-big .chip'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.d-big .num'), {{autoAlpha:0}}, 0);
tl.set(q('.d-big h4'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.d-big p'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.d-chart'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.fl'), {{scaleX:0}}, 0);

tl.to(q('.bar'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.prog'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.1});
tl.to(q('.d-big .chip'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p});
tl.to(q('.d-big .num'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.3});
tl.to(q('.d-big h4'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.3});
tl.to(q('.d-big p'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.4});
tl.to(q('.d-chart'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p+0.5});

const big = {{v:0}};
const bigEl = root.querySelector('#big-num');
tl.to(big, {{v:{big_num}, duration:0.8, ease:'power2.out',
  onUpdate:()=>{{ bigEl.textContent = big.v.toFixed({big_dec}) + '{big_suffix}'; }} }}, {p+0.8});
"""
    for bi, (label, val) in enumerate(bars):
        js += f"""
const p{bi} = {{v:0}};
const vEl{bi} = root.querySelector('#v-{bi}');
const flEl{bi} = root.querySelector('#fl-{bi}');
tl.to(p{bi}, {{v:{val}, duration:0.8, ease:'power2.out',
  onUpdate:()=>{{
    vEl{bi}.textContent = Math.round(p{bi}.v);
    gsap.set(flEl{bi}, {{scaleX: p{bi}.v/100}});
  }} }}, {p+0.8});
"""
    js += f"\nwindow.__timelines['{comp_id}'] = tl;\n"

    standalone, sub = build_page(comp_id, page_css(dd["big"]), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
