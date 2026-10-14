"""B 资讯主页（每条必用）。

纸白底。顶栏 + 左侧（分类标签 / 标题带荧光笔 / 摘要）+ 右侧（配图框 / 侧栏解读）+ 进度条。
"""
from __future__ import annotations
from common import (
    F_BODY, F_MONO, INK, PAPER, BODY_TEXT, HI, MIST, MARGIN,
    topbar, progress_html, split_headline, render_headline_rows, fmt_date_dot,
    build_page, brand,
)

D = 20  # B 有效时长


def page_css() -> str:
    return f"""
#root {{ background:{PAPER}; color:{INK}; }}

/* 左侧 */
.b-main {{ position:absolute; left:{MARGIN}px; top:240px; width:979px; }}
.b-head {{ margin-top:35px; font-size:79px; font-weight:900; line-height:1.28; color:{INK}; width:979px; }}
.b-head .h-line {{ display:block; }}
.b-summary {{ margin-top:42px; font-size:38px; line-height:1.7; color:{BODY_TEXT}; width:979px; }}
.b-summary .s-line {{ display:block; }}

/* 配图框 */
.b-shot {{
  position:absolute; right:{MARGIN}px; top:240px; width:643px; height:362px;
  background:#fff; border:4.8px solid {INK}; box-shadow:17px 17px 0 {INK};
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  overflow:hidden;
}}
.b-shot img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.b-shot .ph-tag {{ font-family:{F_MONO}; font-weight:700; font-size:28px; color:#5C6773; }}
.b-shot .ph-ratio {{ font-family:{F_MONO}; font-size:23px; color:#5C6773; margin-top:10px; }}

/* 侧栏解读 */
.b-say {{
  position:absolute; right:{MARGIN}px; top:639px; width:643px;
  background:{INK}; color:#fff; padding:42px 46px;
  box-shadow:17px 17px 0 {HI};
}}
.b-say .say-body {{ font-size:36px; line-height:1.6; font-weight:500; }}
.b-say .say-tag {{
  position:absolute; top:-20px; left:32px;
  background:{HI}; color:{INK}; font-family:{F_MONO}; font-weight:700;
  font-size:32px; padding:2px 14px;
}}
"""


def render_b(item: dict, idx: int, total: int, date: str,
             prefix: float = 0, suffix: float = 0):
    comp_id = f"b-{item['id']}"
    date_dot = fmt_date_dot(date)
    src = f"来源 {item['source']} · {date_dot}"
    cnt = f"第 {idx} 条 <i>/</i> {total:02d}"

    # 标题（按行 + 荧光笔）
    hrows = split_headline(item["headline"], item.get("highlight", ""), 12.0)
    head_html = render_headline_rows(hrows)

    # 摘要（按行，约 25 全角字）
    srows = split_headline(item["summary"], "", 25.0)
    summ_html = render_headline_rows(srows).replace("h-line", "s-line")
    # 摘要行不需要 hl
    summ_html = "".join(
        f'<span class="s-line">{"".join(t for t, _ in row)}</span>' for row in srows
    )

    # 配图
    image = item.get("image")
    if image:
        shot = f'<div class="b-shot"><img src="__ASSETS__/shots/{image}" alt=""/></div>'
    else:
        shot = (
            '<div class="b-shot">'
            '<span class="ph-tag">配图 / 截图区</span>'
            '<span class="ph-ratio">16:9</span>'
            '</div>'
        )

    body = f"""
{topbar(src, cnt)}
<div class="b-main">
  <span class="chip dk">{item['category']}</span>
  <div class="b-head">{head_html}</div>
  <div class="b-summary">{summ_html}</div>
</div>
{shot}
<div class="b-say">
  <span class="say-tag">{brand('comment_label')}</span>
  <div class="say-body">{item['comment']}</div>
</div>
{progress_html(idx, total)}
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

// 初始状态（时间 0，CSS 不带 transform，避免冲突）
tl.set(q('.bar'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.prog'), {{autoAlpha:0}}, 0);
tl.set(q('.b-main .chip'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.b-head .h-line'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.b-summary .s-line'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.b-shot'), {{autoAlpha:0, y:16}}, 0);
tl.set(q('.b-say'), {{autoAlpha:0, x:80}}, 0);
tl.set(q('.hl-bg'), {{scaleX:0}}, 0);

// 进场
tl.to(q('.bar'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.prog'), {{autoAlpha:1, duration:0.4, ease:'power2.out'}}, {p+0.1});
tl.to(q('.b-main .chip'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.1});
"""

    # 标题各行错开
    for i in range(len(hrows)):
        js += (
            f"tl.to(q('.b-head .h-line:nth-child({i+1})'), "
            f"{{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {round(p+0.2+0.08*i,3)});\n"
        )

    # 荧光笔
    js += (
        f"tl.to(q('.hl-bg'), {{scaleX:1, duration:0.5, ease:'power3.out'}}, {p+1.2});\n"
    )

    # 摘要各行错开
    for j in range(len(srows)):
        js += (
            f"tl.to(q('.b-summary .s-line:nth-child({j+1})'), "
            f"{{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {round(p+2.0+0.08*j,3)});\n"
        )

    # 配图
    js += (
        f"tl.to(q('.b-shot'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p+2.6});\n"
    )
    # 侧栏解读
    js += (
        f"tl.to(q('.b-say'), {{autoAlpha:1, x:0, duration:0.5, ease:'power3.out'}}, {p+10.0});\n"
    )
    js += f"\nwindow.__timelines['{comp_id}'] = tl;\n"

    css = page_css()
    standalone, sub = build_page(comp_id, css, body, js, duration)
    return {
        "comp_id": comp_id,
        "duration": duration,
        "standalone": standalone,
        "sub": sub,
        "D": D,
    }
