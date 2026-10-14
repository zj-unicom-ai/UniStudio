"""页面转场（0.6 秒）。

一块黄色从左扫入盖住画面（0.3s），盖住瞬间换页，再向右扫出（0.3s）。
作为独立 clip，跨在两个页面的交界处：start = 交界时刻 - 0.3，duration = 0.6。
每个转场实例使用唯一 comp_id（trans-N），避免同 comp 多次实例化时脚本找不到 root。
"""
from __future__ import annotations
from common import HI, build_page

D = 0.6


def page_css() -> str:
    return f"""
.trans-block {{ position:absolute; inset:0; background:{HI}; }}
"""


def render_transition(index: int, prefix: float = 0, suffix: float = 0):
    comp_id = f"trans-{index}"
    body = '<div class="trans-block"></div>'
    duration = round(prefix + D + suffix, 3)
    p = prefix
    js = f"""
const root = document.querySelector('[data-composition-id="{comp_id}"]');
const block = root.querySelector('.trans-block');
const tl = gsap.timeline({{paused:true}});

tl.set(block, {{xPercent:-100}}, 0);
tl.to(block, {{xPercent:0, duration:0.3, ease:'power2.in'}}, {p});
tl.to(block, {{xPercent:100, duration:0.3, ease:'power2.out'}}, {p+0.3});

window.__timelines['{comp_id}'] = tl;
"""
    standalone, sub = build_page(comp_id, page_css(), body, js, duration)
    return {"comp_id": comp_id, "duration": duration, "standalone": standalone, "sub": sub, "D": D}
