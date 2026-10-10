# 视觉风格完整约束

本文件是 SKILL.md "视觉约束" 节的展开版,只在生成 prompt 时按需查阅。

## 强制规则(每张图都必须满足)

### 1. 比例与画布

- 16:9,`viewBox` 等价 1600×900
- 无外框、无边框、无装饰线条
- 纯白背景 `#FFFFFF`,**不是米色、不是浅灰、不是 off-white**

### 2. 线条

- 颜色:`#000000` 或 `#120F0F`(几乎黑)
- 笔触:1-2px,潦草/手绘感,允许线条粗细微变化
- 禁止:矢量直线、贝塞尔平滑曲线、几何完美对齐
- **严禁阴影**(no shading,no gradient,no shadow)

### 3. 颜色

只允许 2 种颜色:

- 黑色 `#000000`(主线 + 小黑身体)
- 红色 `#D63055` 或橙色 `#E67E22`(中文标签)

**禁止**:蓝色、绿色、紫色、黄色、棕色、灰色(除黑色外任何色)。所有色块必须二选一。

### 4. 中文标签

- 每个 2-4 字,**严禁超出 4 字**(API 容易拼错)
- 楷体或近似手写体(不要宋体、不要黑体、不要 emoji)
- 主红 `#D63055` 或 橙 `#E67E22`
- 字号:角色身高的 1/8-1/10
- 位置:标签靠近所指对象,不与小黑重叠

### 5. 留白

- 画面 60% 以上为纯白空白
- 元素数量:核心元素 ≤ 3 个 + 小黑 = 总 ≤ 4 个视觉实体
- 元素不要挤在画面中央,允许偏左/偏右以制造视觉节奏

### 6. IP 小黑(详见 `ip-character.md`)

- 每张图必须有,且只有一个
- 必须执行场景核心动作(构图规则)
- 严格遵循 IP 规格,无装饰

## 风格关键词(放进 prompt)

```
minimalist hand-drawn sketch style, Chinese article illustration, 
16:9 horizontal composition, pure white background, 
black ink line art, weight 1-2px, slightly sketchy, 
dominant whitespace, only black + red/orange accents, 
NO shading, NO gradients, NO 3D, NO realism, NO photoreal
```

## 反例(常见错误图描述)

为避免重复出错,以下是常见反面图:

- **"动画风"**:3D 渲染感、亮色填充、卡通大眼睛 —— 错。一律扁平纯线稿。
- **"产品海报风"**:居中大 logo + 多行宣传文字 —— 错。本图为内容配图,无文字墙。
- **"PPT 风"**:矩形方框 + 箭头 + 列表项 —— 错。线条要潦草,不要规则几何。
- **"水彩风"**:渐变背景、水彩晕染 —— 错。只允许纯白。
- **"涂鸦娃娃风"**:Q 版大眼睛、彩色棒棒糖、笑脸 —— 错。小黑无表情。
- **"插画师风格"**:多色配色、艺术字 —— 错。本图只有黑+红/橙。

## Prompt 中如何避免错误

每个 prompt 末尾追加"否定清单":

```
Style rules (STRICT):
- ONLY black ink + red/orange Chinese labels. NO other colors.
- NO shading, NO gradient, NO 3D, NO photoreal.
- NO hat/glasses/clothes on Xiaohei.
- NO emoji, NO ASCII art, NO watermark.
- Pure white #FFFFFF background. No frame, no border.
- Single core concept. Max 3 visual elements + Xiaohei.
- Verify each Chinese character is well-formed (no malformed glyphs).
```

## 自检 checklist(生成后人工确认)

- [ ] 16:9?
- [ ] 纯白背景?
- [ ] 只有黑+红/橙?
- [ ] 有小黑角色?
- [ ] 小黑在做核心动作?
- [ ] 中文标签 2-4 字?
- [ ] 留白 ≥ 60%?
- [ ] 没有标题/边框/水印?

任何一项不满足,重生成。