# xiaohei-illust

Generate 16:9 white-background hand-drawn Chinese-style illustrations for blog articles using the Xiaohei IP character. Reads the article, extracts 3-5 visual anchors, and produces illustrations via the minimax text-to-image API.

Inspired by [Web3 Village Chief's Xiaohei Skill](https://www.cunzhangblog.com/xiaoheskill) (originally written for Codex/TRAE), adapted for Claude Code.

## Structure

```
xiaohei-illust/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── xiaohei-illust/
│       ├── SKILL.md                # Bilingual instructions (CN primary, EN below)
│       ├── references/             # Detailed style / character / API specs
│       └── scripts/
│           └── score_anchors.py    # Heuristic paragraph scorer
└── README.md
```

## Prerequisites

This plugin requires an external MCP server for image generation:

- **`mcp__minimax__text_to_image`** — the MiniMax MCP server. Install separately; without it the skill will produce prompt text instead of images.

The plugin also expects Python 3.9+ on the user's PATH (only needed if the LLM invokes `scripts/score_anchors.py` directly).

## Installation

Once approved in the official marketplace:

```
/plugin install xiaohei-illust@claude-plugins-official
```

For local development:

```bash
git clone https://github.com/SAKEH0017/claude-plugins-official.git
cp -r claude-plugins-official/external_plugins/xiaohei-illust ~/.claude/plugins/
```

## Usage

The skill activates automatically when the user says any of:

- "为博客文章生成手绘插图" / "Generate hand-drawn illustrations for this blog post"
- "用小黑风格画插画" / "Draw in Xiaohei style"
- "为文章配几个 16:9 插图" / "Add 16:9 illustrations to this article"
- "xiaohei illustration" / "生成认知锚点可视化"

The skill then:

1. Reads the article (file path, URL, or pasted Markdown)
2. Scores paragraphs via `scripts/score_anchors.py` to surface 3-5 visual anchors
3. Builds a Shot List (one concept per image)
4. Calls `mcp__minimax__text_to_image` for each Shot
5. Outputs `.svg` (with embedded PNG) and standalone `.png` files to `assets/<article-slug>-illustrations/`

## Privacy

This plugin:

- Does **not** collect any user data
- Does **not** make network calls beyond the MCP server the user has already configured
- Runs entirely locally except for the image-generation API call (handled by the user's MCP server)
- Stores generated illustrations only in the user's chosen output directory

The paragraph scorer (`scripts/score_anchors.py`) is pure heuristic — no telemetry, no external calls.

## License

MIT — see `LICENSE`.