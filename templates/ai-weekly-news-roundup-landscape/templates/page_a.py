"""A 本周目录（开场 10 秒内用完）。

墨蓝底 + 网格。左侧：标签 / 大标题 / 时长更新；右侧：本期目录列表，第一条整行反黄。
"""
from __future__ import annotations
from common import (
    F_DISPLAY, F_BODY, F_MONO, INK, HI, MIST, MARGIN,
    logo_html, progress_html, fmt_date_dot, estimate_runtime, build_page, brand,
)

D = 8


def page_css(total: int) -> str:
    if total <= 5:
        row_padding, row_font = 30, 43
    elif total <= 8:
        row_padding, row_font = 16, 36
    else:
        row_padding, row_font = 10, 31
    return f"""
#root {{ background:{INK}; color:#fff;
  background-image:
    linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px),
    linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px);
  background-size:77px 77px;
}}

/* 左侧 */
.a-left {{ position:absolute; left:{MARGIN}px; top:230px; }}
.a-left h4 {{
  margin:31px 0 0; font-family:{F_DISPLAY}; font-weight:400;
  font-size:173px; line-height:1.02;
}}
.a-left h4 .a-line {{ display:block; }}
.a-left .m {{
  margin-top:58px; font-family:{F_MONO}; font-size:31px;
  color:{MIST}; letter-spacing:.08em; line-height:1.9;
}}
.a-left .m .m-line {{ display:block; }}

/* 右侧列表 */
.a-list {{
  position:absolute; right:{MARGIN}px; top:202px; width:998px;
  display:flex; flex-direction:column;
}}
.a-row {{
  display:grid; grid-template-columns:81px 169px 1fr;
  align-items:center; gap:23px;
  padding:{row_padding}px 31px;
  border-bottom:3px solid rgba(255,255,255,.16);
  font-size:{row_font}px; font-weight:700;
}}
.a-row .n {{ font-family:{F_MONO}; font-weight:700; color:{HI}; font-size:42px; }}
.a-row .chip {{
  width:100%; text-align:center; font-size:25px; padding:6px 0;
}}
.a-row .tt {{ overflow:hidden; }}
.a-row.first {{ background:{HI}; color:{INK}; border-bottom-color:{HI}; }}
.a-row.first .n {{ color:{INK}; }}
.a-row.first .chip {{ background:{INK}; color:{HI}; box-shadow:none; }}
"""


def render_a(data: dict, prefix: float = 0, suffix: float = 0):
    comp_id = "a-toc"
    total = len(data["items"])
    date_dot = fmt_date_dot(data["date"])

    # 左侧
    left = f"""
<div class="a-left">
  <span class="chip">本周目录</span>
  <h4><span class="a-line">本周</span><span class="a-line">盘点 {total} 条</span></h4>
  <div class="m">
    <span class="m-line">预计时长 {estimate_runtime(data)}</span>
  </div>
</div>
"""

    # 列表
    rows = []
    for i, it in enumerate(data["items"]):
        n = f"{i+1:02d}"
        if i == 0:
            rows.append(
                f'<div class="a-row first"><span class="n">{n}</span>'
                f'<span class="chip">{it["category"]}</span>'
                f'<span class="tt">{it["toc_title"]}</span></div>'
            )
        else:
            rows.append(
                f'<div class="a-row"><span class="n">{n}</span>'
                f'<span class="chip ol">{it["category"]}</span>'
                f'<span class="tt">{it["toc_title"]}</span></div>'
            )
    list_html = f'<div class="a-list">{"".join(rows)}</div>'

    body = f"""
<div class="bar">
  {logo_html()}
  <span class="src">{date_dot} {data['weekday']}</span>
</div>
{left}
{list_html}
{progress_html(0, total)}
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

tl.set(q('.bar'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.prog'), {{autoAlpha:0}}, 0);
tl.set(q('.a-left .chip'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.a-left h4 .a-line'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.a-left .m'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.a-row'), {{autoAlpha:0, y:24}}, 0);

tl.to(q('.bar'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.prog'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.1});
tl.to(q('.a-left .chip'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p});
tl.to(q('.a-left h4 .a-line:nth-child(1)'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.2});
tl.to(q('.a-left h4 .a-line:nth-child(2)'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.28});
tl.to(q('.a-left .m'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.4});
"""
    for i in range(total):
        js += (
            f"tl.to(q('.a-row:nth-child({i+1})'), "
            f"{{autoAlpha:1, y:0, duration:0.4, ease:'power3.out'}}, {round(p+0.4+0.1*i,3)});\n"
        )
    js += f"\nwindow.__timelines['{comp_id}'] = tl;\n"

    standalone, sub = build_page(comp_id, page_css(total), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
