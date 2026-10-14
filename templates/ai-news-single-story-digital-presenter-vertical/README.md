# AI News Single-Story Digital Presenter — Vertical

**竖屏单条 AI 资讯深度拆解：封面数字人口型开场白、正文分段旁白与信息卡片、六秒固定片尾。**

[▶ 查看完整样片](preview/full-sample.mp4) · [使用方法](USAGE.md) · [工具与素材](TOOLS.md) · [样例来源](SOURCES.md) · [Skill](SKILL.md)

<p align="center"><img src="preview/cover.png" width="280" alt="深蓝地球封面上，标题下方有日期卡与关键词标签，右下方为口播中的数字人"></p>

## 画面预览

| 正文数据页 | 观察页（无数据卡） | 固定片尾 |
| --- | --- | --- |
| ![带大数字数据卡的正文页](preview/story-page.png) | ![三条观察要点的正文页](preview/insight-page.png) | ![品牌片尾子组合](preview/outro.png) |

## 适用场景

适合每天围绕**一条**AI 热点做深度解读的竖屏栏目：把一个事件拆成发布、价格、评测、生态、观察等切面逐页展开，由固定形象在封面念出开场白，进入正文后交给版式与数据卡承载信息。

本模板聚焦一条新闻的多页深度解读；如果只需要图片快切、BGM 且不需要旁白，可使用仓库中的 AI News Image-Switch Brief。

## 模板规格

- **画幅：** 1080 × 1920，30 fps；示例约 1 分 44 秒
- **结构：** 封面（示例 13.7 秒，含数字人口型）→ 5 页正文 → 6 秒固定片尾
- **节奏：** 每页时长由该段旁白 WAV 的实测长度推导，改文案或换配音后重新构建即自动对齐
- **视觉：** 深蓝地球底图、青蓝科技线、固定页眉、掠光式转场、标题下沿滑光、星圈双光点沿轨运行
- **技术：** HyperFrames `0.8.140`、GSAP、Python 3；示例旁白由 VoiceStudio + OmniVoice 生成，封面口型由 MuseTalk v1.5 生成
- **运行：** 本地构建、检查、预览与渲染；复用样例不需安装语音生成器或 MuseTalk

## 开始使用

安装 Skill 时，把本模板完整目录复制到 ~/.codex/skills/ai-news-single-story-digital-presenter/，或项目的 .agents/skills/ai-news-single-story-digital-presenter/；不要只复制 SKILL.md。

在本目录执行：

```bash
# 按 USAGE.md 直接编辑 data/sample-episode.json，并替换配音与口型素材
npm run build && npm run check
npm run render -- --output out/my-episode.mp4
```

页数可按内容增减（示例为 5 页），正文页与封面共用同一套版式与动效；片尾是独立的子组合，时长固定 6 秒。

## 包含内容

| 路径 | 作用 |
| --- | --- |
| `index.html` | 构建产物，可直接检查与渲染 |
| `data/sample-episode.json` | 一期节目的全部文案字段 |
| `voice-requests.json` | 分段旁白文本与 TTS 参数 |
| `scripts/` | 配音生成、时长测量、时间轴与 composition 构建、口型音频准备 |
| `compositions/gangge-ai-outro.html` | 系列固定片尾子组合（含自带进场音效） |
| `assets/` | 地球底图、品牌标识、主持人素材、示例配音与口型视频、字体、GSAP、音效 |
| `preview/` | 真实渲染的封面、正文、片尾画面与完整样片 |
| `approved-timing.json` / `voice-manifest.json` | 示例的时间轴与 WAV 实测时长 |

## Skill 与交付脚本

SKILL.md 提供可安装的制作流程；scripts/new_project.py 创建干净工程副本；scripts/render_delivery.py 在渲染后导出完整首页封面 PNG 和播放页 HTML。

## 许可与样例素材

模板代码按本目录 [`LICENSE`](LICENSE) 中的 MIT 许可提供；字体与 GSAP 保留各自条款。样例人物、配音、背景、Logo、音效及含这些素材的预览成片有独立权利范围，再发布前请查看 [`SOURCES.md`](SOURCES.md) 与 [`TOOLS.md`](TOOLS.md) 并完成授权核对。
