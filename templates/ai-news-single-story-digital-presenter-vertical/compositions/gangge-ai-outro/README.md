# 刚哥聊 AI 固定片尾

这是可直接嵌入 HyperFrames 项目的 1080×1920 子组合，时长 6 秒，带轻柔进场音效并在末帧保持完整画面。

## 安装到一集工程

把以下内容一起复制到新工程，保持相对目录：

- `compositions/gangge-ai-outro.html`
- `compositions/gangge-ai-outro/` 整个目录

确认主工程已加载 GSAP（本工程用 `assets/vendor/gsap.min.js`），然后在主组合中加入：

```html
<div
  id="gangge-ai-outro"
  class="clip"
  data-composition-id="gangge-ai-outro"
  data-composition-src="compositions/gangge-ai-outro.html"
  data-start="片尾开始时间"
  data-duration="6"
  data-track-index="0"
  data-width="1080"
  data-height="1920"
></div>
```

HyperFrames 的外部子组合路径和其内部素材路径都相对项目根目录解析；保留以上文件布局即可正常加载图标和三条音效。

当前预览工程的 `index.html` 已通过该子组合挂载片尾。此模板固定品牌信息、视觉、音效和 6 秒时长；如需修改文案或品牌设计，应更新此母版并同步替换各期副本。
