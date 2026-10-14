"""AI Weekly News Roundup landscape template shared components.

包含：
- 设计令牌（颜色 / 字体）与全部共用 CSS
- 数据校验（任务书第 7 节异常处理）
- 共用 HTML 组件：顶栏、标签、进度条、荧光笔、硬边卡片、转场、波纹、滚动条
- 页面包装：standalone（可独立渲染）与 sub-composition（可被 index.html 引用）
"""
from __future__ import annotations
from html import escape
import re

BRANDING = {
    "name": "AI", "accent": "周见",
    "cover_label": "AI 科技周报盘点", "vertical_label": "AI 科技周报",
    "cover_subtitle": "每期 10 条，盘点一周<mark>最值得关注</mark>的 AI 科技",
    "vertical_subtitle": "每期 10 条，盘点一周最值得关注的 AI 科技",
    "cover_tagline": "每周一见，看见 AI 的下一步",
    "ticker": "本周热点 · 模型 · 产品 · 融资 · 政策 · 开源",
    "comment_label": "周见点评",
    "closing_next": "每周一见，看见 AI 的下一步。",
    "closing_follow": "点关注，不错过每周的 AI 科技盘点",
}


def set_branding(values: dict | None) -> None:
    """Set visible series copy for a build; omitted keys keep the sample look."""
    BRANDING.update(values or {})


def brand(key: str) -> str:
    # Only cover_subtitle intentionally permits a single <mark> pair.
    value = str(BRANDING[key])
    if key == "cover_subtitle":
        return escape(value).replace("&lt;mark&gt;", "<mark>").replace("&lt;/mark&gt;", "</mark>")
    return escape(value)

# ---------------------------------------------------------------------------
# 设计令牌
# ---------------------------------------------------------------------------
INK = "#0F1E2E"       # 夜航墨，主背景 / 文字
INK2 = "#182C41"      # 深蓝灰，分层
PAPER = "#EDF0EE"     # 冷纸白，内容页底
HI = "#FFD23F"        # 荧光黄，重点
BLUE = "#3A74FF"      # 信号蓝，线条 / 小标签
MIST = "#8A98A6"      # 雾灰，墨蓝底上辅助文字
BODY_TEXT = "#33475A"  # 纸白底上的摘要文字
TRACK_BG = "#E3E8E6"  # 数据条底槽
WHITE = "#F3F6F8"

F_DISPLAY = "'ZCOOL QingKe HuangYou',sans-serif"
F_BODY = "'Noto Sans SC',sans-serif"
F_MONO = "'JetBrains Mono',monospace"

# 版式常量（px）
W, H = 1920, 1080
MARGIN = 115
CONTENT_TOP = 240
CONTENT_LIMIT = 900
PROG_H = 19

# 文字长度预算（任务书第 6 节）
LIMITS = {
    "headline": 30,
    "summary": 70,
    "comment": 45,
    "toc_title": 14,
    "explain": 40,
    "recap": 14,
    "source": 12,
}


class DataError(Exception):
    """数据 / 版式校验错误。"""


# ---------------------------------------------------------------------------
# 数据校验
# ---------------------------------------------------------------------------
def _len(s) -> int:
    return len(s or "")


def check_length(field: str, text: str, limit: int) -> None:
    """文字超长：不缩字号、不截断，直接报错。"""
    n = _len(text)
    if n > limit:
        raise DataError(
            f"字段 {field} 文字超长：当前 {n} 字，上限 {limit} 字，内容「{text}」。"
            f"请压缩文案，不要自动缩小字号。"
        )


def validate_episode(data: dict) -> None:
    """校验整期数据。"""
    items = data.get("items", [])
    total = len(items)
    if total == 0:
        raise DataError("items 为空，至少需要一条资讯。")

    ids = [it.get("id", "") for it in items]
    if len(set(ids)) != total or any(not re.fullmatch(r"[A-Za-z0-9_-]+", cid) for cid in ids):
        raise DataError("每条资讯须有唯一 id，且只能包含英文字母、数字、连字符或下划线。")

    for i, it in enumerate(items):
        idx = i + 1
        cid = it.get("id", f"第{idx}条")
        image = it.get("image")
        if image and (not isinstance(image, str) or not re.fullmatch(r"[A-Za-z0-9_-]+\.(png|jpg|jpeg|webp)", image, re.I)):
            raise DataError(f"{cid}.image 只接受 assets/shots/ 内的 PNG、JPG 或 WebP 文件名。")

        check_length(f"{cid}.headline 标题", it.get("headline", ""), LIMITS["headline"])
        check_length(f"{cid}.summary 摘要", it.get("summary", ""), LIMITS["summary"])
        check_length(f"{cid}.comment 侧栏解读", it.get("comment", ""), LIMITS["comment"])
        check_length(f"{cid}.toc_title 目录标题", it.get("toc_title", ""), LIMITS["toc_title"])
        check_length(f"{cid}.source 来源", it.get("source", ""), LIMITS["source"])

        # highlight 必须是 headline 的连续片段；允许为空
        hl = it.get("highlight", "")
        if hl:
            if hl not in it.get("headline", ""):
                raise DataError(
                    f"{cid}.highlight「{hl}」不是 headline 的连续片段，"
                    f"无法在标题上对准荧光笔。允许 highlight 为空（不划荧光笔）。"
                )

        # layout：B 必有，C 与 D 互斥
        layout = it.get("layout", [])
        if "B" not in layout:
            raise DataError(f"{cid}.layout 必须包含 B（资讯主页）。")
        if "C" in layout and "D" in layout:
            raise DataError(f"{cid}.layout 同时包含 C 和 D，规范规定只能二选一。")
        if "D" in layout:
            d = it.get("data")
            if not d:
                raise DataError(f"{cid}.layout 含 D，但缺少 data 字段。")
            bars = d.get("bars", [])
            if len(bars) < 2:
                raise DataError(f"{cid}.data.bars 至少需要两条对比数据。")
            for name, v in bars:
                if not (0 <= v <= 100):
                    raise DataError(
                        f"{cid}.data.bars 中「{name}」取值 {v}，必须在 0 到 100 之间。"
                    )
        if "C" in layout:
            ex = it.get("explain")
            if not ex or not all(ex.get(k) for k in ("what", "why", "you")):
                raise DataError(f"{cid}.layout 含 C，需要完整 explain.what/why/you。")
            for k in ("what", "why", "you"):
                check_length(f"{cid}.explain.{k}", ex.get(k, ""), LIMITS["explain"])

    # recap
    recap = data.get("recap", [])
    if len(recap) != total:
        raise DataError(f"recap 句数 {len(recap)} 与资讯条数 {total} 不一致。")
    for i, s in enumerate(recap):
        check_length(f"recap[{i+1}]", s, LIMITS["recap"])


# ---------------------------------------------------------------------------
# 共用 CSS
# ---------------------------------------------------------------------------
def font_css(prefix: str = "../assets/") -> str:
    """@font-face：本地字体。

    standalone 与 sub-composition 都使用工程根目录的 assets/ 路径。
    """
    p = prefix
    return f"""
@font-face {{
  font-family:'ZCOOL QingKe HuangYou';
  src:url('{p}fonts/ZCOOLQingKeHuangYou-Regular.ttf') format('truetype');
  font-weight:400; font-display:block;
}}
@font-face {{
  font-family:'Noto Sans SC';
  src:url('{p}fonts/NotoSansSC-VF.ttf') format('truetype');
  font-weight:100 900; font-display:block;
}}
@font-face {{
  font-family:'JetBrains Mono';
  src:url('{p}fonts/JetBrainsMono-VF.ttf') format('truetype');
  font-weight:100 800; font-display:block;
}}
"""


def common_css() -> str:
    """通用样式：重置、背景、顶栏、标签、logo、进度条、硬边卡片、荧光笔。"""
    return f"""
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; width:100%; height:100%; overflow:hidden; }}
#root {{ position:absolute; inset:0; overflow:hidden; font-family:{F_BODY}; }}

/* 背景 */
.bg-ink {{ background:{INK}; color:{WHITE}; }}
.bg-paper {{ background:{PAPER}; color:{INK}; }}
.grid-bg {{
  background-image:
    linear-gradient(rgba(255,255,255,.045) 2px, transparent 2px),
    linear-gradient(90deg, rgba(255,255,255,.045) 2px, transparent 2px);
  background-size:77px 77px;
}}

/* 顶栏 */
.bar {{
  position:absolute; left:{MARGIN}px; right:{MARGIN}px; top:73px;
  display:flex; justify-content:space-between; align-items:center; gap:24px;
}}
.logo {{ font-family:{F_BODY}; font-weight:900; font-size:40px; letter-spacing:.02em; white-space:nowrap; }}
.logo .logo-main {{ color:inherit; }}
.logo b {{ background:{HI}; color:{INK}; padding:0 9px; margin-left:3px; }}
.bg-paper .logo b {{ background:{INK}; color:{HI}; }}
.bar .src {{
  font-family:{F_MONO}; font-size:27px; letter-spacing:.05em;
  opacity:.62; white-space:nowrap; overflow:hidden;
}}
.bar .cnt {{ font-family:{F_MONO}; font-weight:700; font-size:36px; letter-spacing:.04em; white-space:nowrap; }}
.bar .cnt i {{ font-style:normal; opacity:.45; }}

/* 标签 chip */
.chip {{
  display:inline-block; font-family:{F_MONO}; font-weight:700; font-size:29px;
  letter-spacing:.08em; padding:7px 21px; background:{HI}; color:{INK};
}}
.chip.dk {{ background:{INK}; color:{WHITE}; }}
.chip.ol {{ background:transparent; color:{HI}; box-shadow:inset 0 0 0 3px {HI}; }}
.chip.dk.ol {{ background:transparent; color:{INK}; box-shadow:inset 0 0 0 3px {INK}; }}

/* 荧光笔（关键词） */
.hl-word {{ position:relative; display:inline-block; white-space:nowrap; }}
.hl-bg {{
  position:absolute; inset:0; z-index:0;
  background:linear-gradient(transparent 52%, {HI} 52% 94%, transparent 94%);
  transform-origin:left center;
}}
.hl-text {{ position:relative; z-index:1; }}

/* 硬边卡片 */
.hard {{
  border:4.8px solid {INK}; background:#fff;
  box-shadow:17px 17px 0 {INK};
}}

/* 底部进度条 */
.prog {{
  position:absolute; left:0; right:0; bottom:0; height:{PROG_H}px;
  display:grid; grid-template-columns:repeat(5,1fr); gap:6px;
}}
.prog i {{ background:rgba(15,30,46,.16); }}
.prog i.on {{ background:{INK}; }}
.prog i.cur {{ background:{HI}; box-shadow:inset 0 -4px 0 {INK}; }}
.bg-ink .prog i {{ background:rgba(255,255,255,.14); }}
.bg-ink .prog i.on {{ background:{INK2}; }}
.bg-ink .prog i.cur {{ background:{HI}; box-shadow:inset 0 -4px 0 {INK}; }}
"""


# ---------------------------------------------------------------------------
# 共用 HTML 组件
# ---------------------------------------------------------------------------
def logo_html() -> str:
    return (f'<span class="logo"><span class="logo-main">{brand("name")}</span>'
            f'<b>{brand("accent")}</b></span>')


def topbar(src: str, cnt: str = "") -> str:
    """顶栏：logo + 来源 + 第 N 条 / 总数。"""
    return (
        f'<div class="bar">'
        f'{logo_html()}'
        f'<span class="src">{src}</span>'
        f'<span class="cnt">{cnt}</span>'
        f'</div>'
    )


def progress_html(current: int, total: int) -> str:
    """进度条：已播 on，当前 cur，未播普通。current 从 1 开始；传 0 表示全未亮。"""
    parts = []
    for i in range(1, total + 1):
        if i == current:
            cls = "cur"
        elif i < current:
            cls = "on"
        else:
            cls = ""
        parts.append(f'<i class="{cls}"></i>')
    return f'<div class="prog" style="grid-template-columns:repeat({total},1fr)">{"".join(parts)}</div>'


def progress_all_on(total: int) -> str:
    parts = ['<i class="on"></i>'] * total
    return f'<div class="prog" style="grid-template-columns:repeat({total},1fr)">{"".join(parts)}</div>'


def highlight_word(word: str) -> str:
    """关键词 + 荧光笔背景层。"""
    return (
        f'<span class="hl-word">'
        f'<span class="hl-bg"></span>'
        f'<span class="hl-text">{word}</span>'
        f'</span>'
    )


def headline_with_highlight(headline: str, hl: str) -> str:
    """把标题中的 highlight 片段包上荧光笔，其余原样。"""
    if not hl:
        return headline
    before, after = headline.split(hl, 1)
    return f"{before}{highlight_word(hl)}{after}"


def _char_units(ch: str) -> float:
    """字符视觉宽度：CJK / 全角 = 1，ASCII 半角 = .55。"""
    code = ord(ch)
    if code < 0x2000:
        return 0.55
    return 1.0


def split_headline(headline: str, hl: str, max_units: float = 12.0):
    """按每行约 12 个全角字把标题拆成多行。

    返回：list[ list[ (text, is_hl) ] ]。highlight 词整体不被切断。
    """
    if hl:
        before, after = headline.split(hl, 1)
        segments = [(before, False), (hl, True), (after, False)]
    else:
        segments = [(headline, False)]

    rows, cur, width = [], [], 0.0
    for seg, is_hl in segments:
        if not seg:
            continue
        seg_w = sum(_char_units(c) for c in seg)
        if is_hl:
            # 高亮词整体放，放不下先换行
            if width + seg_w > max_units and cur:
                rows.append(cur)
                cur, width = [], 0.0
            cur.append((seg, True))
            width += seg_w
        else:
            for ch in seg:
                cw = _char_units(ch)
                if width + cw > max_units and cur:
                    rows.append(cur)
                    cur, width = [], 0.0
                cur.append((ch, False))
                width += cw
    if cur:
        rows.append(cur)
    return rows


def render_headline_rows(rows) -> str:
    """把 split_headline 的结果渲染成 block 行（.h-line），含荧光笔。"""
    out = []
    for row in rows:
        spans = []
        for text, is_hl in row:
            if is_hl:
                spans.append(highlight_word(text))
            else:
                spans.append(text)
        out.append(f'<span class="h-line">{"".join(spans)}</span>')
    return "".join(out)


def fmt_date_dot(date: str) -> str:
    """2026-10-06 -> 10.06"""
    m, d = date.split("-")[1], date.split("-")[2]
    return f"{m}.{d}"


def estimate_runtime(data: dict) -> str:
    """按页面有效时长估算成片时长：封面 3.5 + 目录 8 + 结尾 10 + 每条 B 20 + C/D 各 10。"""
    seconds = 3.5 + 8 + 10 + len(data["items"]) * 20
    for it in data["items"]:
        if "C" in it.get("layout", []):
            seconds += 10
        if "D" in it.get("layout", []):
            seconds += 10
    m, s = divmod(int(round(seconds)), 60)
    return f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# 页面包装
# ---------------------------------------------------------------------------
def wrap_standalone(comp_id: str, page_css: str, body: str, page_js: str,
                    duration: float, width: int = W, height: int = H) -> str:
    """standalone 页面：root 直接在 body，资源从工程根目录引用。"""
    body = body.replace("__ASSETS__", "assets")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={width},height={height}"/>
<script src="assets/vendor/gsap.min.js"></script>
<style>
{font_css("assets/")}
{common_css()}
{page_css}
</style>
</head>
<body>
<div id="root" class="bg" data-composition-id="{comp_id}" data-width="{width}"
     data-height="{height}" data-duration="{duration}">
{body}
</div>
<script>
{page_js}
</script>
</body>
</html>
"""


def wrap_sub(comp_id: str, page_css: str, body: str, page_js: str,
             duration: float, width: int = W, height: int = H) -> str:
    """sub-composition：root 在 template 内，可被 index.html 引用。资源用 root-relative。"""
    body = body.replace("__ASSETS__", "assets")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
</head>
<body>
<template>
<style>
{font_css("assets/")}
{common_css()}
{page_css}
</style>
<div id="root" class="bg" data-composition-id="{comp_id}" data-width="{width}"
     data-height="{height}" data-duration="{duration}">
{body}
</div>
<script src="assets/vendor/gsap.min.js"></script>
<script>
{page_js}
</script>
</template>
</body>
</html>
"""


def build_page(comp_id: str, page_css: str, body: str, page_js: str,
               duration: float, width: int = W, height: int = H):
    """同时生成 standalone 与 sub 两种包装。"""
    return (
        wrap_standalone(comp_id, page_css, body, page_js, duration, width, height),
        wrap_sub(comp_id, page_css, body, page_js, duration, width, height),
    )
