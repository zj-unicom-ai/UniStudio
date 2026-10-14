#!/usr/bin/env python3
"""AI Weekly News Roundup 模板构建器。

读取指定的 episode JSON，校验后生成各页面的 standalone / sub-composition 两套 HTML，
并（可选）编排根 index.html 完整样片。

用法：
  python3 scripts/build.py b --data data/my-episode.json
  python3 scripts/build.py all     # 默认读取 data/sample-episode.json
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "templates"))

from common import validate_episode, set_branding, DataError  # noqa: E402


def load_data(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate_episode(data)
    set_branding(data.get("branding"))
    return data


def write_pair(name, standalone, sub):
    sp = os.path.join(ROOT, "standalone", f"{name}.html")
    cp = os.path.join(ROOT, "compositions", f"{name}.html")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(standalone)
    with open(cp, "w", encoding="utf-8") as f:
        f.write(sub)
    print(f"  {name}: standalone/{name}.html, compositions/{name}.html")


def build_b(data):
    import page_b
    print("构建 B 资讯主页：")
    total = len(data["items"])
    for i, it in enumerate(data["items"]):
        res = page_b.render_b(it, i + 1, total, data["date"])
        write_pair(res["comp_id"], res["standalone"], res["sub"])


def build_a(data):
    import page_a
    print("构建 A 本周目录：")
    res = page_a.render_a(data)
    write_pair(res["comp_id"], res["standalone"], res["sub"])


def build_e(data):
    import page_e
    print("构建 E 结尾页：")
    res = page_e.render_e(data)
    write_pair(res["comp_id"], res["standalone"], res["sub"])


def build_c(data):
    import page_c
    print("构建 C 三句话拆解：")
    total = len(data["items"])
    for i, it in enumerate(data["items"]):
        if "C" in it["layout"]:
            res = page_c.render_c(it, i + 1, total, data["date"])
            write_pair(res["comp_id"], res["standalone"], res["sub"])


def build_d(data):
    import page_d
    print("构建 D 数据对比：")
    total = len(data["items"])
    for i, it in enumerate(data["items"]):
        if "D" in it["layout"]:
            res = page_d.render_d(it, i + 1, total, data["date"])
            write_pair(res["comp_id"], res["standalone"], res["sub"])


def build_covers(data):
    import cover_h, cover_v
    print("构建封面：")
    res = cover_h.render_cover_h(data)
    write_pair(res["comp_id"], res["standalone"], res["sub"])
    res = cover_v.render_cover_v(data)
    write_pair(res["comp_id"], res["standalone"], res["sub"])


TRANS = 0.3  # 转场扫出占用的开场延迟


def load_voice():
    """Load optional user-supplied narration metadata from the project root."""
    vp = os.path.join(ROOT, "voice-manifest.json")
    if not os.path.exists(vp):
        return {}
    with open(vp, encoding="utf-8") as f:
        return {m["id"]: m for m in json.load(f)}


def build_transition():
    import transition
    res = transition.render_transition()
    cp = os.path.join(ROOT, "compositions", "trans.html")
    with open(cp, "w", encoding="utf-8") as f:
        f.write(res["sub"])
    return res


def write_transition(index):
    import transition
    res = transition.render_transition(index)
    cp = os.path.join(ROOT, "compositions", f"trans-{index}.html")
    with open(cp, "w", encoding="utf-8") as f:
        f.write(res["sub"])
    return res


def build_shots(data):
    """渲染全部镜头（sub-composition，带 prefix），返回镜头信息列表。"""
    import cover_h, page_a, page_b, page_c, page_d, page_e
    total = len(data["items"])
    date = data["date"]
    shots = []

    r = cover_h.render_cover_h(data, prefix=0)
    write_pair(r["comp_id"], r["standalone"], r["sub"])
    shots.append(r)

    r = page_a.render_a(data, prefix=TRANS)
    write_pair(r["comp_id"], r["standalone"], r["sub"])
    shots.append(r)

    for i, it in enumerate(data["items"]):
        r = page_b.render_b(it, i + 1, total, date, prefix=TRANS)
        write_pair(r["comp_id"], r["standalone"], r["sub"])
        shots.append(r)
        if "D" in it["layout"]:
            r = page_d.render_d(it, i + 1, total, date, prefix=TRANS)
            write_pair(r["comp_id"], r["standalone"], r["sub"])
            shots.append(r)
        if "C" in it["layout"]:
            r = page_c.render_c(it, i + 1, total, date, prefix=TRANS)
            write_pair(r["comp_id"], r["standalone"], r["sub"])
            shots.append(r)

    r = page_e.render_e(data, prefix=TRANS)
    write_pair(r["comp_id"], r["standalone"], r["sub"])
    shots.append(r)
    return shots


def assemble(data):
    print("构建全部页面并编排完整样片：")
    import cover_v
    vertical_cover = cover_v.render_cover_v(data)
    write_pair(vertical_cover["comp_id"], vertical_cover["standalone"], vertical_cover["sub"])
    shots = build_shots(data)

    # 计算各页面 clip 的 start / duration
    page_clips = []
    cursor = 0.0
    for i, r in enumerate(shots):
        start = 0.0 if i == 0 else cursor
        dur = r["duration"]
        w, h = r.get("width", 1920), r.get("height", 1080)
        page_clips.append((r["comp_id"], start, dur, w, h))
        cursor = round(start + dur, 3)

    # 转场 clip，跨相邻页面边界；每个生成独立文件
    trans_clips = []
    for i in range(len(page_clips) - 1):
        boundary = page_clips[i + 1][1]
        trans_clips.append((boundary - TRANS, 0.6, i))
        write_transition(i)

    total_dur = round(cursor, 3)

    def host(cid, start, dur, w, h, name):
        return (
            f'<div id="{name}" data-composition-id="{cid}" '
            f'data-composition-src="compositions/{cid}.html" '
            f'data-start="{start}" data-duration="{dur}" '
            f'data-width="{w}" data-height="{h}"></div>'
        )

    page_html = "\n".join(
        host(c, s, d, w, h, name=f"host-{i}")
        for i, (c, s, d, w, h) in enumerate(page_clips)
    )
    trans_html = "\n".join(
        host(f"trans-{i}", s, d, 1920, 1080, name=f"tr-{i}")
        for s, d, i in trans_clips
    )

    voice = load_voice()
    audio_html = "\n".join(
        f'<audio id="voice-{c}" src="{voice[c]["path"]}" '
        f'data-start="{round(s + (0.2 if i == 0 else 0.35), 3)}" '
        f'data-duration="{voice[c]["duration_s"]}" data-track-index="10"></audio>'
        for i, (c, s, d, w, h) in enumerate(page_clips) if c in voice
    )
    if audio_html:
        print(f"旁白已接入：{audio_html.count('<audio')} 段")

    index = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=1920,height=1080"/>
<script src="assets/vendor/gsap.min.js"></script>
</head>
<body>
<div id="root" class="bg" data-composition-id="seq" data-width="1920"
     data-height="1080" data-duration="{total_dur}">
{page_html}
{audio_html}
{trans_html}
</div>
<script>
const tl = gsap.timeline({{paused:true}});
window.__timelines['seq'] = tl;
</script>
</body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    print(f"完整样片已编排：index.html，总时长 {total_dur}s")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build an editorial video from episode JSON")
    parser.add_argument("target", nargs="?", default="all",
                        choices=("b", "a", "e", "core", "pages", "cover", "all"))
    parser.add_argument("--data", default="data/sample-episode.json",
                        help="episode JSON path (relative to the project or absolute)")
    args = parser.parse_args()
    target = args.target
    data_path = args.data if os.path.isabs(args.data) else os.path.join(ROOT, args.data)
    try:
        data = load_data(data_path)
    except DataError as e:
        print(f"数据校验失败：{e}")
        sys.exit(1)

    if target == "b":
        build_b(data)
    elif target == "a":
        build_a(data)
    elif target == "e":
        build_e(data)
    elif target == "core":
        build_a(data)
        build_b(data)
        build_e(data)
    elif target == "pages":
        build_covers(data)
        build_a(data)
        build_b(data)
        build_c(data)
        build_d(data)
        build_e(data)
    elif target == "cover":
        build_covers(data)
    elif target == "all":
        assemble(data)
    else:
        print(f"未知目标：{target}")
        sys.exit(1)

    print("构建完成。")


if __name__ == "__main__":
    main()
