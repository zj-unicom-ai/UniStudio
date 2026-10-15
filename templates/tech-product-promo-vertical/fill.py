#!/usr/bin/env python3
"""tech-promo-vertical 模板填充脚本。

用法:
    python3 fill.py <content.json> <out_dir>

行为:
  - 读取本目录 index.html(令牌化模板),用 content.json 的值替换全部 {{TOKEN}};
  - 将 hyperframes.json 与 assets/(hero.jpg / macro.jpg / bgm.mp3) 一并拷入 out_dir;
  - 缺令牌或残留 {{...}} 直接报错退出,保证不会渲出半成品。

替换产品内容只需:改 content.json 的文案 + 用你的产品图覆盖 out_dir/assets/hero.jpg 与 macro.jpg。
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 模板文件位置兼容两种布局: 模板库内为 templates/index.template.html, 独立目录内为 index.html
TEMPLATE = HERE / "templates" / "index.template.html"
if not TEMPLATE.is_file():
    TEMPLATE = HERE / "index.html"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    content_path = Path(sys.argv[1]).resolve()
    out_dir = Path(sys.argv[2]).resolve()

    data = json.loads(content_path.read_text(encoding="utf-8"))
    tpl = TEMPLATE.read_text(encoding="utf-8")

    missing = [m for m in re.findall(r"\{\{(\w+)\}\}", tpl) if m not in data]
    if missing:
        print(f"[fill] 缺少令牌: {', '.join(sorted(set(missing)))}")
        return 1

    out = tpl
    for key, val in data.items():
        out = out.replace("{{%s}}" % key, str(val))

    left = sorted(set(re.findall(r"\{\{(\w+)\}\}", out)))
    if left:
        print(f"[fill] 仍有未替换令牌: {', '.join(left)}")
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(out, encoding="utf-8")
    shutil.copy2(HERE / "package.json", out_dir / "package.json")
    shutil.copy2(HERE / "hyperframes.json", out_dir / "hyperframes.json")

    src_assets = HERE / "assets"
    dst_assets = out_dir / "assets"
    dst_assets.mkdir(parents=True, exist_ok=True)
    if src_assets.is_dir():
        for f in src_assets.iterdir():
            if f.is_file():
                shutil.copy2(f, dst_assets / f.name)

    print(f"[fill] ok -> {out_dir}")
    print("[fill] 下一步: 用产品图覆盖 assets/hero.jpg 与 assets/macro.jpg, 然后 lint/check/render")
    return 0


if __name__ == "__main__":
    sys.exit(main())
