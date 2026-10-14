"""竖版封面（1080×1920）。

墨蓝底 + 网格 + 同心波纹。顶部标签/logo，中部大标题，下方日期戳，底部黄色滚动条。
"""
from __future__ import annotations
from common import (
    F_DISPLAY, F_BODY, F_MONO, INK, HI, BLUE,
    logo_html, fmt_date_dot, build_page, brand,
)

D = 3.5
Wv, Hv = 1080, 1920


def page_css() -> str:
    return f"""
#root {{
  background:{INK}; color:#fff;
  background-image:
    linear-gradient(rgba(255,255,255,.05) 2px, transparent 2px),
    linear-gradient(90deg, rgba(255,255,255,.05) 2px, transparent 2px);
  background-size:54px 54px;
}}

.waves {{
  position:absolute; right:-432px; top:70%; width:1620px; aspect-ratio:1;
  border-radius:50%;
  background:repeating-radial-gradient(circle,transparent 0 30px,rgba(58,116,255,.7) 30px 32px);
  -webkit-mask-image:radial-gradient(circle,#000 18%,transparent 68%);
  mask-image:radial-gradient(circle,#000 18%,transparent 68%);
}}

.c-top {{ position:absolute; left:86px; top:65px; right:86px;
  display:flex; justify-content:space-between; align-items:center; }}
.c-top .chip {{ font-size:43px; padding:11px 32px; }}
.c-top .logo {{ font-size:54px; }}
.c-top .logo b {{ padding:0 13px; margin-left:9px; }}

.cv-title {{ position:absolute; left:86px; right:86px; top:324px; }}
.cv-title .a {{ font-family:{F_DISPLAY}; font-size:292px; line-height:1.02; }}
.cv-title .b {{ display:inline-block; background:{HI}; color:{INK};
  font-family:{F_DISPLAY}; font-size:367px; line-height:1;
  padding:0 43px 22px; margin-top:22px; }}
.cv-title .s {{ margin-top:86px; font-weight:700; font-size:65px; line-height:1.45; }}

.cv-stamp {{ position:absolute; left:86px; bottom:216px;
  font-family:{F_MONO}; font-weight:700; color:{HI}; font-size:173px; line-height:1; }}
.cv-stamp small {{ display:block; font-size:48px; color:#F3F6F8;
  font-family:{F_BODY}; margin-top:22px; font-weight:500; }}

.ticker {{ position:absolute; left:0; right:0; bottom:0; height:119px;
  background:{HI}; color:{INK}; display:flex; align-items:center;
  white-space:nowrap; overflow:hidden;
  font-family:{F_MONO}; font-weight:700; font-size:43px; letter-spacing:.14em; }}
.ticker span {{ padding-left:30px; }}
"""

def render_cover_v(data: dict, prefix: float = 0, suffix: float = 0):
    comp_id = "cover-v"
    total = len(data["items"])
    date_dot = fmt_date_dot(data["date"])

    body = f"""
<div class="waves"></div>
<div class="c-top">
  <span class="chip">{brand('vertical_label')}</span>
  {logo_html()}
</div>
<div class="cv-title">
  <div class="a">{brand('name')}</div>
  <div class="b">{brand('accent')}</div>
  <div class="s">{brand('vertical_subtitle')}</div>
</div>
<div class="cv-stamp">{date_dot}
  <small>{data['weekday']} · 本周 {total} 条 · 第 {data['episode']} 期</small>
</div>
<div class="ticker"><span>{(brand('ticker') + ' · ') * 2}</span></div>
"""

    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const q = (s) => root.querySelectorAll(s);
const tl = gsap.timeline({{paused:true}});

tl.set(q('.waves'), {{scale:.98}}, 0);
tl.set(q('.c-top'), {{autoAlpha:0, y:-20}}, 0);
tl.set(q('.cv-title .a'), {{autoAlpha:0, y:40}}, 0);
tl.set(q('.cv-title .b'), {{autoAlpha:0, y:40}}, 0);
tl.set(q('.cv-title .s'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.cv-stamp'), {{autoAlpha:0, y:24}}, 0);
tl.set(q('.ticker'), {{yPercent:100}}, 0);

tl.to(q('.c-top'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p});
tl.to(q('.cv-title .a'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p+0.2});
tl.to(q('.cv-title .b'), {{autoAlpha:1, y:0, duration:0.5, ease:'power3.out'}}, {p+0.35});
tl.to(q('.cv-title .s'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.6});
tl.to(q('.cv-stamp'), {{autoAlpha:1, y:0, duration:0.45, ease:'power3.out'}}, {p+0.7});
tl.to(q('.waves'), {{scale:1.05, duration:3, ease:'sine.inOut'}}, {p+0.2});
tl.to(q('.ticker'), {{yPercent:0, duration:0.4, ease:'power3.out'}}, {p+0.8});
tl.to(q('.ticker span'), {{x:-140, duration:2.3, ease:'none'}}, {p+1.0});

window.__timelines['{comp_id}'] = tl;
"""

    standalone, sub = build_page(comp_id, page_css(), body, js, duration, width=Wv, height=Hv)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
