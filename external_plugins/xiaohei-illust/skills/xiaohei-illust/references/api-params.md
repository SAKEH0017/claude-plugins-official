# minimax text_to_image API 参数

`mcp__minimax__text_to_image` 调用推荐配置。

## 推荐参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `prompt` | 见下方模板 | 英文 prompt,完整描述场景 + 风格规则 |
| `aspect_ratio` | `16:9` | 强制 16:9 |
| `num_images` | `1` | 一次只生成一张,失败重试,绝不批量后挑 |
| `style` (若支持) | `illustration` 或 `sketch` | 倾向插画/素描风,避免 photoreal |

## Prompt 完整模板

将 Shot List 转 API prompt:

```
[SCENE]
<场景描述,用 1-2 句话讲清楚画面内容>

[CHARACTER]
IP character "小黑" (Xiaohei): solid black silhouette body in egg/oval form,
two tiny white dot eyes, thin stick legs, blank expression,
wearing nothing, NO hat/glasses/clothes/mouth/eyebrows,
currently <小黑动作>.

[CHINESE LABELS]
Chinese labels (handwritten, red #D63055, max 4 chars each):
- <标签1> at <位置>
- <标签2> at <位置>

[STYLE RULES - STRICT]
16:9 horizontal, pure white #FFFFFF background.
Minimalist hand-drawn sketch, Chinese article illustration.
Black ink line art, weight 1-2px, slightly sketchy.
ONLY black + red/orange. NO shading, NO gradient, NO 3D, NO photoreal.
NO emoji, NO watermark, NO frame, NO border.
Heavy negative space dominates. Single core concept. Max 3 visual elements.
```

## 调优经验

- **API 偶发中文拼错**:在 prompt 末尾追加 `verify each Chinese character is well-formed (no malformed glyphs)` 可减少约 30% 错字
- **小黑人像渲染成普通人**:在 [CHARACTER] 段加 `pure flat silhouette, no facial features except dot eyes, no body details`
- **留白不足**:在 [STYLE] 段加 `margins of 200px on all sides, vast majority of frame is empty white`
- **颜色污染**:在 [STYLE] 段加 `palette locked to: #FFFFFF background, #000000 lines, #D63055 text only`

## 输出处理

API 返回 base64 PNG。

包装成 SVG:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%">
  <image href="data:image/png;base64,<BASE64>" width="1600" height="900"/>
</svg>
```

同时落盘独立 `.png` 副本。

## 失败兜底

如 API 报错或返回非图像:

1. 不要立刻重试 5 次 — 1 次重试,如仍失败则停下
2. 报告给用户,提供已构造的 prompt 文本(用户可粘贴到即梦/豆包/Midjourney)
3. 检查 MCP 连接:用 `mcp__MiniMax__web_search` 或类似确认 minimax 服务在线