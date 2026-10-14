#!/usr/bin/env python3
"""极端数据测试：合法边界 + 异常校验。

运行：python3 tests/edge_cases.py
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "templates"))

from common import validate_episode, DataError, LIMITS  # noqa: E402

passed = 0
failed = 0


def base_item(i):
    return {
        "id": f"n-{i}",
        "category": "产品",
        "headline": "某产品上线 AI 新功能，效率明显提升",
        "toc_title": "某产品上线 AI 新功能",
        "highlight": "AI 新功能",
        "summary": "新功能把原来需要手工做的步骤自动完成，目前先向部分用户开放。",
        "source": "示例媒体",
        "image": None,
        "comment": "看一个功能好不好，要看它能不能替你省掉重复劳动。",
        "layout": ["B"],
    }


def episode(n):
    return {
        "date": "2026-10-06",
        "weekday": "周二",
        "episode": 128,
        "items": [base_item(i) for i in range(n)],
        "recap": [f"第{i}条一句话回顾" for i in range(n)],
    }


def check_valid(name, data):
    global passed, failed
    try:
        validate_episode(copy.deepcopy(data))
        passed += 1
        print(f"  ✓ {name}")
    except Exception as e:  # noqa
        failed += 1
        print(f"  ✗ {name} 应合法却报错：{e}")


def check_error(name, data):
    global passed, failed
    try:
        validate_episode(copy.deepcopy(data))
        failed += 1
        print(f"  ✗ {name} 应报错却通过")
    except DataError:
        passed += 1
        print(f"  ✓ {name} 正确报错")


print("== 合法边界 ==")
check_valid("最少 3 条", episode(3))
check_valid("周报 10 条", episode(10))

d = episode(3)
d["items"][0]["highlight"] = ""
check_valid("无 highlight（不划荧光笔）", d)

d = episode(3)
d["items"][0]["headline"] = "字" * LIMITS["headline"]
d["items"][0]["highlight"] = ""
d["items"][0]["summary"] = "摘" * LIMITS["summary"]
d["items"][0]["comment"] = "评" * LIMITS["comment"]
d["items"][0]["toc_title"] = "目" * LIMITS["toc_title"]
check_valid("各字段恰好达到上限", d)

d = episode(3)
d["items"][0]["headline"] = "OpenAI 发布 GPT-5，编码能力增强"
d["items"][0]["toc_title"] = "OpenAI 发布 GPT5"
d["items"][0]["highlight"] = "GPT-5"
check_valid("中英数字混合标题", d)

d = episode(3)
it = d["items"][0]
it["layout"] = ["B", "D"]
it["data"] = {"big": "3.2×", "title": "完成率", "note": "对比",
              "bars": [["旧", 0], ["新", 100]]}
check_valid("D 页 bars 取 0 与 100 边界", d)

print("== 异常校验 ==")
check_error("items 为空", {**episode(3), "items": [], "recap": []})

d = episode(3)
d["items"][0]["headline"] = "字" * (LIMITS["headline"] + 1)
check_error("headline 超长", d)

d = episode(3)
d["items"][0]["highlight"] = "不存在的词"
check_error("highlight 不是连续片段", d)

d = episode(3)
d["items"][0]["layout"] = ["A"]
check_error("layout 缺 B", d)

d = episode(3)
d["items"][0]["layout"] = ["B", "C", "D"]
d["items"][0]["explain"] = {"what": "a", "why": "b", "you": "c"}
d["items"][0]["data"] = {"bars": [["旧", 1], ["新", 2]]}
check_error("layout 同时含 C 和 D", d)

d = episode(3)
d["items"][0]["layout"] = ["B", "D"]
d["items"][0]["data"] = {"bars": [["旧", 50], ["新", 120]]}
check_error("bars 值超过 100", d)

d = episode(3)
d["items"][0]["layout"] = ["B", "D"]
d["items"][0]["data"] = {"bars": [["旧", 50]]}
check_error("bars 不足两条", d)

d = episode(3)
d["items"][0]["layout"] = ["B", "D"]
check_error("含 D 但缺 data", d)

d = episode(3)
d["items"][0]["layout"] = ["B", "C"]
check_error("含 C 但缺 explain", d)

d = episode(3)
d["recap"] = ["a", "b"]
check_error("recap 句数与条数不符", d)

d = episode(3)
d["recap"][0] = "回" * (LIMITS["recap"] + 1)
check_error("recap 单句超长", d)

d = episode(3)
d["items"][1]["id"] = d["items"][0]["id"]
check_error("重复 id", d)

d = episode(3)
d["items"][0]["image"] = "../outside.png"
check_error("配图越过 assets/shots", d)

print(f"\n结果：{passed} 通过，{failed} 失败")
sys.exit(1 if failed else 0)
