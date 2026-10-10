#!/usr/bin/env python3
"""
score_anchors.py — 段落打分启发式

读取文章(文件路径或 stdin),按段落切分,对每段调用
score_anchor() 打分,输出 top-K 候选给后续 Shot List 步骤。

用法:
    python score_anchors.py <article.md> [--top-k 8] [--json-out candidates.json]
    cat article.md | python score_anchors.py --top-k 5
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# Windows 默认 CP936 stdin/stdout 会把 UTF-8 中文解码成"看着对但字节错"
# 的字符串,导致所有 PROCESS_WORDS 命中 0;强制 UTF-8 即可。
for _stream in (sys.stdin, sys.stdout, sys.stderr):
    reconfigure = getattr(_stream, "reconfigure", None)
    if not reconfigure:
        continue
    try:
        reconfigure(encoding="utf-8")
    except OSError:
        pass


# ---------- 启发式输入 ----------------------------------------------------

# 中文"过程信号"词 — 出现通常表示段落描述了一个可拆解的流程
PROCESS_WORDS = {
    "首先", "然后", "接着", "之后", "最后", "再", "接下来",
    "第一步", "第二步", "第三步", "第一步", "步骤",
    "流程", "顺序", "依次", "经过", "穿过",
}

# 对比/转折词 — 段落含成对概念时常适合可视化(对比图)
CONTRAST_WORDS = {
    "但是", "然而", "但是", "不过", "反之", "相反",
    "对比", "比起", "比", "优于", "弱于",
    "旧", "新", "之前", "之后", "传统", "现代",
}

# 隐喻/类比信号 — 段落含比喻时通常值得配图
METAPHOR_WORDS = {
    "像", "如同", "好比", "类似", "犹如", "仿佛",
    "如同", "是", "好比", "相当于", "就像",
}

# 抽象词 — 这些词密度过高的段落不适合配图
ABSTRACT_WORDS = {
    "感受", "心情", "情绪", "体会", "感悟", "哲学",
    "意义", "价值", "本质", "内核", "心态",
}


# ---------- TODO: 核心打分函数 --------------------------------------------

def score_anchor(paragraph: str) -> float:
    """
    TODO(user): 实现段落"可视化价值"打分启发式。

    返回 [0.0, 1.0] 的浮点数,越高代表该段越适合配插图。
    返回 0.0 代表该段是情绪/抽象段落,不适合配图。

    设计提示:
      - 不要追求完美,可结合多个简单信号求加权:
          * 词数(50-200 字最佳,过短/过长扣分)
          * 视觉化实体密度(具体名词多 → 高分)
          * 过程信号词命中数(PROCESS_WORDS)
          * 对比信号词命中数(CONTRAST_WORDS)
          * 隐喻信号词命中数(METAPHOR_WORDS)
          * 抽象信号词命中数(ABSTRACT_WORDS → 扣分)
          * 是否包含数字/列表符号(流程图信号)

      - 权衡:
          * 信号越多 → 越确定但越死板
          * 信号越少 → 越依赖后续 Shot List 的 LLM 评审
          * 建议从 3-4 个信号开始,跑几条文章看效果

      - 调试:
          * 可以先让函数打印各项得分,再合并
          * 跑完一段后肉眼对照"应该配图吗"

    输入:一整段纯文本(可能含换行,但不含 markdown 标题/列表)
    输出:0.0-1.0 浮点数
    """
    # 1) 长度门控:20-400 字适合配图,过短/过长直接 0
    n = len(paragraph)
    if n < 20 or n > 400:
        return 0.0

    # 2) 信号计数(每词出现 1 次 +1)
    process = sum(1 for w in PROCESS_WORDS if w in paragraph)
    contrast = sum(1 for w in CONTRAST_WORDS if w in paragraph)
    metaphor = sum(1 for w in METAPHOR_WORDS if w in paragraph)
    abstract = sum(1 for w in ABSTRACT_WORDS if w in paragraph)

    # 3) 加权求和 — 权重是业务判断,可随意调
    score = 0.3 + 0.2 * process + 0.2 * contrast + 0.15 * metaphor - 0.4 * abstract

    # 4) 夹紧到 [0, 1]
    return max(0.0, min(1.0, score))


# ---------- 段落切分 ----------------------------------------------------

HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


def split_paragraphs(text: str) -> list[dict]:
    """
    按 H2/H3 切分大段,再按空行切分段落。
    返回 [{"id": "p1", "text": "...", "heading": "..."}, ...]
    """
    blocks: list[dict] = []
    current_heading = ""

    # 先按 markdown 标题切块
    parts = HEADING_RE.split(text)
    # re.split with capture group yields: [pre, "#", "title", body, "#", "title", body, ...]
    i = 0
    pid = 0
    if parts and parts[0].strip():
        # 文章开头无标题的内容
        body = parts[0]
        sub_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        for p in sub_paragraphs:
            pid += 1
            blocks.append({"id": f"p{pid}", "text": p, "heading": current_heading})
        i = 1

    while i + 2 < len(parts):
        title = parts[i + 1]
        body = parts[i + 2]
        current_heading = title.strip()
        sub_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        for p in sub_paragraphs:
            pid += 1
            blocks.append({"id": f"p{pid}", "text": p, "heading": current_heading})
        i += 3

    return blocks


# ---------- 主流程 ------------------------------------------------------

def read_article(source: str | None) -> str:
    """从文件路径或 stdin 读取文章全文。"""
    if source and source != "-":
        return Path(source).read_text(encoding="utf-8")
    return sys.stdin.read()


def rank(text: str, top_k: int) -> list[dict]:
    paragraphs = split_paragraphs(text)
    scored: list[dict] = []
    for p in paragraphs:
        try:
            s = float(score_anchor(p["text"]))
        except NotImplementedError:
            raise
        except Exception as e:  # 单段打分失败不该让整个脚本崩
            print(f"[warn] {p['id']} score failed: {e}", file=sys.stderr)
            s = 0.0
        scored.append({**p, "score": round(s, 3)})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "score_anchors").split("\n")[0])
    parser.add_argument("source", nargs="?", default="-",
                        help="文章路径,或 '-' 表示 stdin (默认)")
    parser.add_argument("--top-k", type=int, default=8,
                        help="返回候选数(默认 8)")
    parser.add_argument("--json-out", type=str, default=None,
                        help="可选,把结果写到 JSON 文件")
    args = parser.parse_args(list(argv) if argv else None)

    text = read_article(args.source)
    top = rank(text, args.top_k)

    out = json.dumps(top, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(out, encoding="utf-8")
        print(f"[ok] wrote {len(top)} candidates to {args.json_out}", file=sys.stderr)
    else:
        print(out)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except NotImplementedError as e:
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(2)