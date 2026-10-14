"""C 三句话拆解（用于需要多讲一层的条目）。

纸白底。顶部：标签 + 提问式标题；下方三栏：WHAT / WHY / YOU。
"""
from __future__ import annotations
from common import (
    F_BODY, F_MONO, PAPER, BLUE, INK, HI, BODY_TEXT, MARGIN,
    topbar, progress_html, fmt_date_dot, build_page,
)

D = 10
COLS = [
    ("WHAT", "发生了什么", "what"),
    ("WHY", "为什么重要", "why"),
    ("YOU", "和你有什么关系", "you"),
]


def page_css() -> str:
    return f"""
#root {{ background:{PAPER}; color:{INK}; }}

.c-h {{ position:absolute; left:{MARGIN}px; right:{MARGIN}px; top:221px; }}
.c-h h4 {{ margin:27px 0 0; font-size:63px; font-weight:900; line-height:1.3; }}
.c-h h4 mark {{ background:linear-gradient(transparent 55%,{HI} 55% 94%,transparent 94%); color:inherit; }}

.c-cols {{
  position:absolute; left:{MARGIN}px; right:{MARGIN}px; top:405px;
  display:grid; grid-template-columns:repeat(3,1fr); gap:46px;
}}
.c-col {{
  background:#fff; padding:38px 42px 42px; min-width:0;
  box-shadow:6px 6px 0 {INK};
}}
.c-col .k {{ font-family:{F_MONO}; font-weight:700; font-size:28px; letter-spacing:.1em; color:{BLUE}; }}
.c-col h5 {{ margin:15px 0 0; font-size:52px; font-weight:900; line-height:1.2; }}
.c-col p {{ margin:27px 0 0; font-size:36px; line-height:1.6; color:{BODY_TEXT}; }}
"""


def render_c(item, idx, total, date, prefix: float = 0, suffix: float = 0):
    comp_id = f"c-{item['id']}"
    explain = item.get("explain")
    if not explain:
        raise ValueError(f"C 页 {item['id']} 缺少 explain 字段")

    date_dot = fmt_date_dot(date)
    src = f"来源 {item['source']} · {date_dot}"
    cnt = f"第 {idx} 条 <i>/</i> {total:02d}"

    c_title = f"{item['toc_title']}，到底意味着什么"
    c_title = c_title.replace("意味着什么", "<mark>意味着什么</mark>")

    cols = []
    for k, h5, key in COLS:
        if key not in explain:
            raise ValueError(f"C 页 {item['id']} explain 缺少 {key}")
        cols.append(
            f'<div class="c-col"><div class="k">{k}</div>'
            f'<h5>{h5}</h5><p>{explain[key]}</p></div>'
        )

    body = f"""
{topbar(src, cnt)}
<div class="c-h">
  <span class="chip dk">三句话拆解</span>
  <h4>{c_title}</h4>
</div>
<div class="c-cols">{"".join(cols)}</div>
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
tl.set(q('.c-h .chip'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.c-h h4'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.c-col'), {{autoAlpha:0, y:32}}, 0);

tl.to(q('.bar'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.prog'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.1});
tl.to(q('.c-h .chip'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p});
tl.to(q('.c-h h4'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.2});
"""
    for i in range(3):
        js += (
            f"tl.to(q('.c-col:nth-child({i+1})'), "
            f"{{autoAlpha:1, y:0, duration:0.35, ease:'power3.out'}}, {round(p+1.0+0.25*i,3)});\n"
        )
    js += f"\nwindow.__timelines['{comp_id}'] = tl;\n"

    standalone, sub = build_page(comp_id, page_css(), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
