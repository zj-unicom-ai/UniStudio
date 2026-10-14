"""E 结尾页。

墨蓝底 + 网格。左侧：本周收尾 / 告别 / 关注提示；右侧：一句话回顾列表。
"""
from __future__ import annotations
from common import (
    F_DISPLAY, F_MONO, INK, HI, MIST, MARGIN,
    logo_html, progress_all_on, fmt_date_dot, build_page, brand,
)

D = 10


def page_css(total: int) -> str:
    if total <= 5:
        pad, li_font, li_gap, head_font = "42px 50px", 36, 21, 27
    elif total <= 8:
        pad, li_font, li_gap, head_font = "32px 44px", 28, 13, 25
    else:
        pad, li_font, li_gap, head_font = "26px 40px", 24, 8, 23
    return f"""
#root {{ background:{INK}; color:#fff;
  background-image:
    linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px),
    linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px);
  background-size:77px 77px;
}}

/* 左侧 */
.e-main {{ position:absolute; left:{MARGIN}px; top:240px; }}
.e-main h4 {{
  margin:35px 0 0; font-family:{F_DISPLAY}; font-weight:400;
  font-size:184px; line-height:1.05;
}}
.e-main h4 .e-line {{ display:block; }}
.e-main h4 .hl {{ background:{HI}; color:{INK}; padding:0 19px 7px; }}
.e-main p {{ margin-top:58px; font-size:48px; font-weight:700; }}
.e-main .m {{
  margin-top:19px; font-family:{F_MONO}; font-size:31px;
  color:{MIST}; letter-spacing:.06em;
}}

/* 右侧回顾 */
.e-recap {{
  position:absolute; right:{MARGIN}px; top:250px; width:{691 if total <= 5 else 760}px;
  border:4.8px solid rgba(255,255,255,.28);
  padding:{pad};
}}
.e-recap .t {{ font-family:{F_MONO}; font-size:{head_font}px; letter-spacing:.1em; color:{HI}; }}
.e-recap ol {{
  list-style:none; margin:23px 0 0; padding:0;
  display:flex; flex-direction:column; gap:{li_gap}px;
}}
.e-recap li {{ display:flex; gap:27px; font-size:{li_font}px; font-weight:500; line-height:1.45; align-items:baseline; }}
.e-recap li b {{ font-family:{F_MONO}; color:{HI}; flex:none; }}
"""


def render_e(data: dict, prefix: float = 0, suffix: float = 0):
    comp_id = "e-end"
    total = len(data["items"])
    date_dot = fmt_date_dot(data["date"])

    left = f"""
<div class="e-main">
  <span class="chip">本周收尾</span>
  <h4>
    <span class="e-line">本周就</span>
    <span class="e-line">盘到<span class="hl">这儿</span></span>
  </h4>
  <p>{brand('closing_next')}</p>
  <div class="m">{brand('closing_follow')}</div>
</div>
"""

    items = []
    for i, s in enumerate(data["recap"]):
        items.append(f'<li><b>{i+1:02d}</b><span>{s}</span></li>')
    recap = f"""
<div class="e-recap">
  <div class="t">一句话回顾</div>
  <ol>{"".join(items)}</ol>
</div>
"""

    body = f"""
<div class="bar">
  {logo_html()}
  <span class="src">{date_dot} {data['weekday']}</span>
</div>
{left}
{recap}
{progress_all_on(total)}
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

tl.set(q('.bar'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.prog'), {{autoAlpha:0}}, 0);
tl.set(q('.e-main .chip'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.e-main h4 .e-line'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.e-main p'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.e-main .m'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.e-recap li'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.e-recap .t'), {{autoAlpha:0}}, 0);

tl.to(q('.bar'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.prog'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.1});
tl.to(q('.e-main .chip'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p});
tl.to(q('.e-main h4 .e-line:nth-child(1)'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.2});
tl.to(q('.e-main h4 .e-line:nth-child(2)'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.28});
tl.to(q('.e-main p'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.5});
tl.to(q('.e-main .m'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.6});
tl.to(q('.e-recap .t'), {{autoAlpha:1, duration:0.4, ease:'power3.out'}}, {p+0.9});
"""
    for i in range(total):
        js += (
            f"tl.to(q('.e-recap li:nth-child({i+1})'), "
            f"{{autoAlpha:1, y:0, duration:0.4, ease:'power3.out'}}, {round(p+1.0+0.15*i,3)});\n"
        )
    js += f"\nwindow.__timelines['{comp_id}'] = tl;\n"

    standalone, sub = build_page(comp_id, page_css(total), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
