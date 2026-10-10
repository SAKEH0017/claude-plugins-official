---
name: xiaohei-illust
description: This skill should be used when the user asks to "为博客文章生成手绘插图", "用小黑风格画插画", "为文章配几个 16:9 插图", "xiaohei illustration", "生成认知锚点可视化", "Generate hand-drawn illustrations for this blog post", "Draw in Xiaohei style", or mentions 小黑/手绘配图/文章插画. Reads a Chinese article (file path, URL, or pasted Markdown), extracts 3-5 "cognitive anchors" worth illustrating, and generates 16:9 white-background hand-drawn Chinese-style illustrations featuring the Xiaohei IP character via the minimax text-to-image API. Outputs `.svg` (with embedded PNG) and standalone `.png` files to `assets/<article-slug>-illustrations/`.
version: 0.1.0
---

# 小黑 Skill — 为中文博客生成手绘配图 / Generate Hand-Drawn Illustrations for Blog Articles

> **本 Skill 双语**:中文为主,英文在下。Frontmatter 的 `description` 是中英混合触发短语,任意语言用户说对应关键词都能命中。
>
> **This skill is bilingual**: Chinese primary below, English mirror further down. The `description` in frontmatter mixes Chinese and English trigger phrases, so users in either language will activate it.

---

## 中文版(主)

为中文博客文章生成 16:9 白底手绘风格插图,使用小黑 IP 角色。生成走 `mcp__minimax__text_to_image` API,产物既保留 `.svg` 容器也保留独立 `.png`。

### 适用场景

- 知识科普 / 方法论类博客文章需要内文配图
- 个人品牌统一视觉风格需求
- 想用 AI 自动读懂文章、再生成对应插图(而非关键词抽卡)

### 不适用

- 封面海报 / 头图(本 skill 假设一图一概念,用于正文)
- 单图密集布局 / 信息图
- 商业产品图(不允许)

### 工作流(6 步)

#### Step 1. 读文章

接收用户输入的文章来源。三种合法形式:

1. 文件路径:如 `D:/blogs/dns-flow.md`
2. URL(让 LLM 自己联网抓)
3. 直接粘贴的 Markdown 文本

读取后,按段落(或 H2 章节)切分为候选单元。

#### Step 2. 评分候选段落

调用 `scripts/score_anchors.py` 对每个候选单元打分,过滤出 top-K(默认 K=8)交给下一步。

**核心业务逻辑在 `scripts/score_anchors.py` 的 `score_anchor()` 函数里** —— 这是决定"哪段值得画"的关键启发式。

执行:

```bash
python scripts/score_anchors.py <文章路径> --top-k 8
```

输出 JSON:`[{"paragraph_id": "p3", "text": "...", "score": 0.82}, ...]`

#### Step 3. 拟定 Shot List(LLM)

读取 Step 2 的 top-K,挑选 3-5 个"认知锚点"形成最终 Shot List。每个 Shot 必须包含:

- **概念名**:2-6 字
- **段落引用**:原始段落首句或关键句
- **场景描述**:一句话描述视觉场景(用什么比喻)
- **小黑动作**:小黑在这个场景里做什么、姿态如何(规则:移除小黑,构图应崩溃)
- **中文标签**:2-4 个标签,每个 2-4 字,**严禁超出 4 字**
- **风格强调**:16:9 白底 + 黑色细线条 + 极简中文 + 大量留白

#### Step 4. 构造 minimax prompt

对每个 Shot,构造英文 prompt 模板(API 对英文 prompt 稳定性更好):

```
16:9 horizontal, pure white background. Minimalist hand-drawn sketch style.
Black ink line art, weight 1-2px, slightly sketchy, NO shading, NO gradients.
Negative space dominates.

Required IP character "小黑" (Xiaohei): solid black silhouette body,
two small white dot eyes, thin stick legs, blank expression,
must be actively performing the core action (composition breaks if removed).

Scene: <场景描述>
Xiaohei pose: <小黑动作>
Chinese labels (handwritten, thin red #D14): <标签1> <标签2> <标签3>
Heavy whitespace. Only black ink + red/orange Chinese annotations.
No other colors. No frame, no border.
```

**API 参数建议**(详见 `references/api-params.md`):

- aspect_ratio: `16:9`
- num_images: 1(失败可重试,绝不批量生成后挑)

#### Step 5. 调用 API 并落盘

对每个 Shot 调用 `mcp__minimax__text_to_image`,得到图片 base64。

落盘:

```
assets/<article-slug>-illustrations/
├── shot-1.svg      # 含 <image href="data:image/png;base64,..."> 的容器
├── shot-1.png      # 独立 PNG,方便博客/Notion 直接嵌入
├── shot-2.svg
├── shot-2.png
├── ...
└── manifest.json   # 列出每个 shot 的 prompt + 段落引用 + 文件路径
```

#### Step 6. 风格合规自检

对每个输出 PNG 做肉眼检查(用户自行确认)。如出现以下问题,标记需重生成:

| 问题 | 重生成 prompt 补丁 |
|------|------------------|
| 小黑角色缺失或变成普通人 | 显式追加 "MUST contain IP character Xiaohei, solid black silhouette body" |
| 中文标签超出 5 字 | 强制缩减,追加 "verify each Chinese label is ≤4 characters" |
| 颜色污染(蓝色/绿色出现) | 追加 "ONLY black + red/orange, no blue/green/yellow/purple" |
| 构图拥挤 / 留白不足 | 追加 "single core concept, max 3 visual elements, dominant whitespace" |
| 中文错字 | 重生成一次,如仍错字换更短的同义词 |

**接受 AI 随机性**:同输入多次出图会不同,对 1-2 张不满意的局部重生成即可,不要全图重做。

### 视觉约束(必须复述进每个 prompt)

这些不是建议,是规则:

1. **比例**:16:9(`1600×900`)
2. **背景**:纯白 `#FFFFFF`,无边框无外框
3. **线条**:黑色 `#000000`,1-2px,略潦草(手绘感)
4. **IP 角色**:小黑必出场,具体规格见 `references/ip-character.md`
5. **中文标签**:每个 2-4 字,手写感,红色或橙色(主红 `#D63055` / 橙 `#E67E22`),楷体或近似手写体
6. **留白**:画面 60%+ 为空白
7. **无填充色块**:除标签和角色身体外,不允许大面积色块

详细风格指南见 `references/visual-style.md`。

### 不适用 / 反模式

- 单 Shot 多概念(违反"一图一概念"原则)
- 抽象情感段落(没有视觉隐喻)
- 商业产品图
- 装饰性封面

### 失败兜底

如果 minimax MCP 未连接或 API 返回失败:

1. 先告诉用户 MCP 状态
2. 提供 prompt 模板供用户在其他工具(豆包 / 即梦 / Midjourney)使用
3. 生成的产物是 prompt 文本而非图片文件

### 附加资源

- `references/ip-character.md` - 小黑角色详细规格
- `references/visual-style.md` - 完整视觉约束 + 反例
- `references/shot-list-examples.md` - 完整 Shot List 范例
- `references/api-params.md` - minimax text_to_image 参数推荐
- `scripts/score_anchors.py` - 段落打分启发式

---

## English Version (Mirror)

Generate 16:9 white-background hand-drawn illustrations for Chinese blog articles using the Xiaohei IP character. Image generation goes through the `mcp__minimax__text_to_image` API; outputs include both `.svg` containers and standalone `.png` files.

### When to Use

- Knowledge / methodology blog posts that need inline illustrations
- Maintaining a consistent personal-brand visual style
- Letting AI read an article and produce matching illustrations (rather than random-keyword generation)

### When NOT to Use

- Cover posters or hero images (this skill assumes one concept per image, designed for body text)
- Single dense layouts / infographics
- Commercial product illustration

### Workflow (6 Steps)

#### Step 1. Read the Article

Accept the article source in three forms:

1. File path, e.g. `D:/blogs/dns-flow.md`
2. URL (let the LLM fetch)
3. Pasted Markdown

Split into paragraph-level candidate units.

#### Step 2. Score Candidates

Run `scripts/score_anchors.py` to score each candidate, default top-K=8.

**The core heuristic lives in `score_anchor()` inside `scripts/score_anchors.py`** — this decides "which paragraph is worth illustrating."

```bash
python scripts/score_anchors.py <article-path> --top-k 8
```

Output JSON: `[{"paragraph_id": "p3", "text": "...", "score": 0.82}, ...]`

#### Step 3. Build Shot List

Read the top-K, pick 3-5 "cognitive anchors" to form the final Shot List. Each Shot must include:

- **Concept name**: 2-6 characters
- **Source quote**: the original paragraph's key sentence
- **Scene description**: one sentence describing the visual scene
- **Xiaohei action**: what Xiaohei does in the scene (rule: removing Xiaohei must break the composition)
- **Chinese labels**: 2-4 labels, each 2-4 characters, **never exceeding 4**
- **Style emphasis**: 16:9 white background + black thin lines + minimal Chinese + heavy whitespace

#### Step 4. Build minimax Prompt

For each Shot, build an English prompt template (the API works more consistently with English):

```
16:9 horizontal, pure white background. Minimalist hand-drawn sketch style.
Black ink line art, weight 1-2px, slightly sketchy, NO shading, NO gradients.
Negative space dominates.

Required IP character "小黑" (Xiaohei): solid black silhouette body,
two small white dot eyes, thin stick legs, blank expression,
must be actively performing the core action (composition breaks if removed).

Scene: <scene description>
Xiaohei pose: <action>
Chinese labels (handwritten, thin red #D14): <label 1> <label 2> <label 3>
Heavy whitespace. Only black ink + red/orange Chinese annotations.
No other colors. No frame, no border.
```

**API parameters** (see `references/api-params.md`):

- `aspect_ratio`: `16:9`
- `num_images`: 1 (retry on failure, never batch-pick)

#### Step 5. Call API and Save

Call `mcp__minimax__text_to_image` per Shot, receive base64.

Save to:

```
assets/<article-slug>-illustrations/
├── shot-1.svg      # container with <image href="data:image/png;base64,...">
├── shot-1.png      # standalone PNG for direct blog/Notion embedding
├── ...
└── manifest.json   # per-shot prompt + source quote + file path
```

#### Step 6. Style Compliance Self-Check

Visually verify each PNG. Mark for regeneration if:

| Issue | Prompt patch |
|-------|--------------|
| Xiaohei missing or generic human | Append "MUST contain IP character Xiaohei, solid black silhouette body" |
| Chinese label > 5 chars | Shorten + append "verify each Chinese label is ≤4 characters" |
| Color contamination (blue/green) | Append "ONLY black + red/orange, no blue/green/yellow/purple" |
| Composition crowded | Append "single core concept, max 3 visual elements, dominant whitespace" |
| Chinese typo | Regenerate once; if still wrong, swap to a shorter synonym |

**Accept AI randomness**: identical inputs may produce different outputs across runs. Re-roll problematic shots individually.

### Hard Visual Constraints

These are non-negotiable rules, repeated in every prompt:

1. **Aspect**: 16:9 (`1600×900`)
2. **Background**: pure white `#FFFFFF`, no frame or border
3. **Lines**: black `#000000`, 1-2px, slightly sketchy (hand-drawn feel)
4. **IP character**: Xiaohei must appear — see `references/ip-character.md` for full spec
5. **Chinese labels**: 2-4 chars each, handwritten, red `#D63055` or orange `#E67E22`
6. **Whitespace**: 60%+ of frame is blank
7. **No fill blocks**: only labels and the Xiaohei body may carry solid color

Full style guide: `references/visual-style.md`.

### Anti-Patterns

- One Shot, multiple concepts (violates "one concept per image")
- Abstract emotional paragraphs (no visual metaphor)
- Commercial product imagery
- Decorative cover artwork

### Failure Fallback

If the minimax MCP is offline or the API fails:

1. Tell the user about the MCP status
2. Provide prompt text for use in other tools (Doubao / Jimeng / Midjourney)
3. The output becomes prompt text, not image files

### Additional Resources

- `references/ip-character.md` — Xiaohei character spec
- `references/visual-style.md` — full visual constraints + anti-examples
- `references/shot-list-examples.md` — 3 complete Shot List examples
- `references/api-params.md` — minimax text_to_image parameter recommendations
- `scripts/score_anchors.py` — paragraph scoring heuristic