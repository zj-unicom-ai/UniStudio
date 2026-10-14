"""横版封面（1920×1080）。

墨蓝底 + 网格 + 同心波纹。顶部标签/logo，中部大标题与副标，右侧日期戳，底部黄色滚动条。
"""
from __future__ import annotations
from common import (
    F_DISPLAY, F_MONO, INK, HI, MIST, BLUE, MARGIN,
    logo_html, fmt_date_dot, build_page, brand,
)

D = 3.5


def page_css() -> str:
    return f"""
#root {{
  background:{INK}; color:#fff;
  background-image:
    linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px),
    linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px);
  background-size:77px 77px;
}}

.waves {{
  position:absolute; right:-269px; top:50%; width:1190px; aspect-ratio:1;
  border-radius:50%;
  background:repeating-radial-gradient(circle,transparent 0 44px,rgba(58,116,255,.7) 44px 46px);
  -webkit-mask-image:radial-gradient(circle,#000 18%,transparent 68%);
  mask-image:radial-gradient(circle,#000 18%,transparent 68%);
}}

.c-top {{ position:absolute; left:{MARGIN}px; top:88px; right:{MARGIN}px;
  display:flex; justify-content:space-between; align-items:center; }}

.c-title {{ position:absolute; left:{MARGIN}px; top:288px; }}
.c-title .t1 {{ font-family:{F_DISPLAY}; font-size:259px; line-height:1;
  letter-spacing:.01em; display:flex; align-items:center; gap:27px; }}
.c-title .t1 .ai {{ background:{HI}; color:{INK}; padding:0 27px 12px; font-family:{F_DISPLAY}; line-height:1.05; }}
.c-title .sub {{ margin-top:61px; font-size:52px; font-weight:700; max-width:768px; line-height:1.5; }}
.c-title .sub mark {{ background:linear-gradient(transparent 55%,rgba(255,210,63,.9) 55% 95%,transparent 95%); color:#fff; }}
.c-title .sub2 {{ margin-top:23px; font-size:33px; color:{MIST}; }}

.c-stamp {{ position:absolute; right:134px; top:326px; width:461px;
  border:6px solid {HI}; padding:38px 46px; background:rgba(15,30,46,.82);
  box-shadow:19px 19px 0 {BLUE}; }}
.c-stamp .d {{ font-family:{F_MONO}; font-weight:700; font-size:154px; line-height:1; color:{HI}; letter-spacing:-.02em; }}
.c-stamp .w {{ margin-top:23px; font-weight:700; font-size:40px; }}
.c-stamp .n {{ font-family:{F_MONO}; font-size:27px; color:{MIST}; margin-top:12px; letter-spacing:.06em; }}

.ticker {{ position:absolute; left:0; right:0; bottom:0; height:100px;
  background:{HI}; color:{INK}; display:flex; align-items:center;
  white-space:nowrap; overflow:hidden;
  font-family:{F_MONO}; font-weight:700; font-size:33px; letter-spacing:.14em; }}
.ticker span {{ padding-left:38px; }}
"""

def render_cover_h(data: dict, prefix: float = 0, suffix: float = 0):
    comp_id = "cover-h"
    total = len(data["items"])
    date_dot = fmt_date_dot(data["date"])

    body = f"""
<div class="waves"></div>
<div class="c-top">
  <span class="chip">{brand('cover_label')}</span>
  {logo_html()}
</div>
<div class="c-title">
  <div class="t1"><span>{brand('name')}</span><span class="ai">{brand('accent')}</span></div>
  <div class="sub">{brand('cover_subtitle')}</div>
  <div class="sub2">{brand('cover_tagline')}</div>
</div>
<div class="c-stamp">
  <div class="d">{date_dot}</div>
  <div class="w">{data['weekday']} · 本周 {total} 条</div>
  <div class="n">第 {data['episode']} 期</div>
</div>
<div class="ticker"><span>{(brand('ticker') + ' · ') * 3}</span></div>
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

tl.set(q('.waves'), {{yPercent:-50, scale:.98}}, 0);
tl.set(q('.c-top'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.c-title .t1'), {{autoAlpha:0, y:40}}, 0);
tl.set(q('.c-title .sub'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.c-title .sub2'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.c-stamp'), {{autoAlpha:0, x:40}}, 0);
tl.set(q('.ticker'), {{yPercent:100}}, 0);

tl.to(q('.c-top'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.c-title .t1'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p+0.2});
tl.to(q('.c-title .sub'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.5});
tl.to(q('.c-title .sub2'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.65});
tl.to(q('.c-stamp'), {{autoAlpha:1, x:0, duration:0.5, ease:'power3.out'}}, {p+0.5});
tl.to(q('.waves'), {{scale:1.05, duration:3, ease:'sine.inOut'}}, {p+0.2});
tl.to(q('.ticker'), {{yPercent:0, duration:0.4, ease:'power3.out'}}, {p+0.7});
tl.to(q('.ticker span'), {{x:-160, duration:2.4, ease:'none'}}, {p+1.0});

window.__timelines['{comp_id}'] = tl;
"""

    standalone, sub = build_page(comp_id, page_css(), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
