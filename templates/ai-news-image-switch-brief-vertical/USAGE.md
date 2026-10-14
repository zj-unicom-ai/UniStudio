# 使用方法

## 1. 准备环境

- Node.js 22+ 与 npm。
- HyperFrames CLI `0.6.46`：由 `npm run` 脚本通过 `npx` 调用，首次运行需要网络下载。
- Chromium、FFmpeg 与 ffprobe：按 HyperFrames 当前环境要求安装；FFmpeg/ffprobe 用于视频渲染、抽取封面和验证成片规格。
- Python 3：运行内容填充脚本；仅使用标准库。

所有命令都从本模板文件夹内执行，不依赖作者电脑的绝对路径。

## 2. 替换本期内容

1. 复制 `data/sample-episode.json`，例如 `data/my-episode.json`。
2. 修改 `title`、`subtitle`、`footerKicker` 和 `footerLines`。标题最多 12 个字符，副标题最多 16 个字符，摘要 1–3 行且每行最多 21 个字符。
3. 把新图片放到 `assets/images/`，在 `images` 中填写唯一 `id`、相对路径和说明文字。每期可放 1–8 张图片。
4. 默认音乐是 `assets/audio/dynamic-bgm.mp3`。样例配置中的 `bgmDuration` 记录这段音乐的长度，构建脚本会自动从 0 秒开始重复它，直到覆盖 18.3 秒成片。更换成不同长度的 BGM 时，更新 `bgmDuration`；无需修改视觉时长。
5. 在 `beats` 中设置图片切换时间和对应图片 id。第一条必须从 0 秒开始，后续时间严格递增并小于 `duration`；同一张图片可以在多个节拍重复使用。
6. 构建：

   ```bash
   python3 scripts/build_episode.py data/my-episode.json
   ```

   这会校验本地素材、文案长度和节拍，然后生成 `index.html`。路径写相对本模板目录的路径，不使用绝对路径或 `..`。

## 3. 转场与画面布局

- `transitionDeck` 支持 `zoom`（中心快速放大）、`push`（侧向推入）、`tilt`（轻微旋转弹入）。转场列表会按 `transitionSeed` 做确定性打乱；相同数据每次预览和渲染顺序相同。默认节拍较快，转场持续约 0.3 秒。
- 图片只能在中央框内变化；背景、标题和底部信息面板保持静态。请使用主体清晰、适合横向裁切的图片。
- 更改构图或转场时间时，同时检查 CSS 画框尺寸和 JSON 节拍；不要用 `Math.random()`，以保持可 seek 渲染的一致性。
- 全息背景图可以替换为 9:16 图片；当前文件约 1088 × 1920，会按画布填充。

## 4. 检查、预览和渲染

```bash
npm run build
npm run check
npm run dev
npm run render -- --quality high --output out/my-ai-news.mp4
```

`npm run dev` 会启动 Studio 预览；确认背景、标题、摘要、转场和 BGM 循环后再渲染。默认输出为 1080 × 1920、30 fps、18.3 秒。`out/` 用于个人输出，不会被 Git 跟踪。

`npm run render` 会生成 MP4、从视频 0.5 秒处抽取的完整首页封面 PNG，以及引用该视频和封面的播放页 HTML。渲染脚本会用 ffprobe 检查画幅、帧率、音轨和时长；交付前仍需目视检查封面、图片切换和片尾。

## 5. 示例内容

默认画面展示 Google EmbeddingGemma 2 的多模态搜索概念。样片里的“用语音找视频瞬间”是画面文案，不代表有语音播报；它是概念演示，不是 Google 应用截图、实时搜索或性能测试。事实来源和素材出处见 [`SOURCES.md`](SOURCES.md)。
