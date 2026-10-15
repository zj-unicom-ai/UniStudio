# 沃资讯｜日期版模板

这是一个数据驱动的 9:16 单条科技新闻模板，按日期版视觉稿制作，默认使用深蓝光束背景、至少四张图片、女播报快节奏音色和青蓝图片转场。当前目录也包含一条 AA-Robotics 样片配置，可直接预览；原创概念图会明确标为“示意图”。

## 生成当前样片

```bash
python3 scripts/generate_voiceover.py
python3 scripts/build-envelope.py
npm run build
npm run check
npx --yes hyperframes@0.8.158 preview --background
npx --yes hyperframes@0.8.158 preview --status
```

VoiceStudio 需要在本机 `http://localhost:3900` 运行。固定使用已保存音色「女播报快节奏」（c5a1e453）、OmniVoice、中文、语速 1.0、broadcast 预设和固定 seed。脚本先核对音色名称与 ID；找不到时停止，不自动替换通用女声。生成脚本不会保存或覆盖音色档案。

工程固定使用 `hyperframes@0.8.158`，相关 npm 脚本显式固定版本，避免随机器全局 CLI 改变。GSAP 3.14.2 随工程本地加载，预览和渲染不请求 CDN。

## 制作下一期

1. 编辑 `data/episode.json` 中的栏目日期、标题、副标题、图片时间点和摘要段。
2. 将至少四张本地 SVG/PNG/JPG 放进 `assets/images/`，在 JSON 的 `imageAssets` 中登记，再在 `imageTimeline` 中按旁白语义设置时间。原创概念图要标注为示意图；新闻照片需要记录可核验来源和授权状态。
3. 编辑 `content/narration.txt`，生成 `assets/audio/voiceover-female-news-fast.wav`；脚本也会保存配音参数到 `assets/audio/voiceover-metadata.json`。
4. 重新计算音频包络、构建 HTML，并运行项目检查：

   ```bash
   python3 scripts/build-envelope.py
   npm run build
   npm run check
   ```

5. 预览后按审核结果执行 `npm run render`。渲染视频默认保存到 `renders/沃资讯-日期版.mp4`；渲染完成后，模板会从完整首帧同步输出 `renders/沃资讯-日期版-封面.png`。如果通过 `--output` 指定了其他视频路径，封面也会放在同目录并使用相同文件名。

## 文件职责

- `data/episode.json`：每期数据和时间点。
- `content/narration.txt`：中文旁白稿。
- `assets/images/`：冻结在项目内的本地新闻图或原创示意图。
- `assets/backgrounds/reference-date-clean-v1.png`：由日期版视觉稿清理出的纯背景；`visualStyle.backgroundPath` 可替换背景素材。
- `assets/audio/`：旁白、VoiceStudio 元数据和离线 RMS 包络。
- `templates/index.template` + `scripts/build.mjs`：生成可寻帧 composition。
- `BRIEF.md`、`DESIGN.md`、`SOURCES.md`：创作 brief、画面约定和来源核验记录。

## 来源与当前样片说明

当前样片依据用户提供的新闻摘要制作。AA-Robotics v0.1 的原始发布页和首批结果尚未核实；没有编造具体任务名、成绩或模型排名。四张中间主图是原创示意图，不是评测原图或真实测试现场。核实来源后再用于正式发布。

日期由 `publishDate` 固定提供，不读取系统时钟。Composition 使用本地媒体、固定 seed 和可 seek 时间轴，不依赖渲染时网络请求。

## 依赖

- Node.js + npm
- `hyperframes@0.8.158`（项目脚本固定）
- GSAP 3.14.2（本地随包）
- Python 3 标准库
- 本机 VoiceStudio OmniVoice 服务
- GSAP 核心可用标准许可：[GSAP Standard License](https://gsap.com/standard-license)

## 图片动效

至少四张图片，每张按 `imageTimeline` 入场。首帧完整显示品牌、标题、副标题、首图和摘要，便于视频默认预览与另存封面；首图从完整可见状态轻推近，后续图片侧滑并配合青蓝扫光转场。`motion.imageEntranceSec` 控制首图推近，`imageTransitionSec` 控制后续侧滑与扫光，`imageScaleTo` 控制阅读期间的缓慢推进。默认分别为 0.65 秒、0.52 秒和 1.04 倍。Registry 原组件保存在 `compositions/components/`，实际改编代码在 `templates/index.template`。

片尾在旁白结束后保留全画面 0.8 秒，不做淡黑。
