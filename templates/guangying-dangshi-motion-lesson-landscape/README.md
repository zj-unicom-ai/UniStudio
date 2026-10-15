# 光影党史｜动态党课 — Landscape

「光影党史｜动态党课」是横屏长篇党史课件模板：用代码动画与内容驱动的 SVG 图解讲述党史，拒绝静态插画堆砌和匀速缩放。随包样片为 EP01《从石库门到遵义：在探索中寻找中国革命的道路》，9 章、约 130 镜头、12 分 10 秒，旁白字幕按本地 ASR 时码逐句对齐。

[▶ 完整样片（720p 压缩版）](preview/full-sample.mp4) · [封面](preview/cover.png) · [制作 Skill](SKILL.md) · [工程任务书](AGENTS.md)

![EP01 封面](preview/cover.png)

## 适用场景

党史、红色主题与理论教育类长视频（约 10–20 分钟）：专题党课、组织学习栏目、历史事件讲解。画面全部在 HyperFrames 合成内用 SVG 绘制（时间线、史料层次、历史地点、组织关系、会议决策），每一段图解都明确标注为示意，不冒充历史影像；真实档案素材须另行核验来源与授权后才能加入。

## 规格与随包内容

- 1920 × 1080（16:9），25 fps，H.264/AAC；样片成片 12:09.8。
- `compositions/EP01_M6.html`：**当前主线入口**（内容驱动 SVG 画面 + 4 秒封面开场）。
- `compositions/EP01_M5.html`：Canvas 多构图画面版，同旁白时码，作备选视觉语法。
- `compositions/EP01_60s_preview.html` / `index.html` / `index-with-huashu.html`：60 秒样片、原始 20 分钟草案与花叔片段回填入口。
- `content/`：分章口播稿、逐镜时码 JSON、编辑表 CSV、`SOURCES.md` 史料核验记录。
- `src/`：`graphics-m6.js` 可寻址 SVG 场景库、`episode-scenes-m6.js` 场景映射、`episode-data-m5.js` 镜头与 ASR 时码数据，以及 M4/M5 旧版图形源码。
- `media/`：M5 旁白与配乐 WAV（配乐为 `scripts/assemble_m5_audio.py` 生成的原创环境音）、花叔白板片段 5 段。
- `docs/`：视觉/动效规范、分镜规划、验收 QA、各版本复核记录。
- `node_modules/`（GSAP 3.14.2）随模板提供；**新工程复制时会被跳过，先 `npm install`**。字体为思源黑体子集，附 OFL 许可。

## 快速开始

从本目录执行（Node.js 22+、Python 3.10+、FFmpeg、可用浏览器）：

```bash
npm install
npx --yes hyperframes@0.8.152 lint
npx --yes hyperframes@0.8.152 check
npx --yes hyperframes@0.8.152 preview --background          # 浏览器逐帧预览
npx --yes hyperframes@0.8.152 render \
  --composition compositions/EP01_M6.html \
  --output out/EP01_M6_final.mp4 --fps 25 --quality looks
```

不带浏览器环境可先用 `python3 -m http.server 8765` 打开 `preview.html` 拖动查看 20 分钟草案时间轴。渲染结果确认后复制 MP4 与封面 PNG 到工程 `deliver/`，再按 UniStudio 流程登记。封面矢量源为 `assets/EP01_M6_cover.svg`，改标题后导出 PNG 即新一期封面。

## 制作新一期

输入是分章口播稿（`content/EP01_SCRIPT_M5.md` 格式：`## S01｜章名` + `**口播**` 段落）。流程与硬约束见 [SKILL.md](SKILL.md)：分章 TTS 配音 → `scripts/assemble_m5_audio.py` 合并并生成配乐 → ASR 时码 → `scripts/build_m5_timeline.py` 重排镜头与字幕 → 更新场景映射与 SVG 画面 → lint/check/preview/render。随包脚本的章节路径与数量按 EP01 写死，新工程按本期脚本改路径与章数。

## 版本沿革与双引擎

- **M4**（19:53）：204 镜 Canvas 版，旁白按 ASR 时码对齐；媒体文件未随本模板（文稿与时码保留在 `content/`）。
- **M5**（12:09.78）：每章更换构图语汇，缩减花叔片段；随包可渲染。
- **M6**（12:09.8，当前版）：31 段内容驱动 SVG 画面，不依赖花叔；M4/M5 成片与复核记录见 `docs/`。
- 花叔（`huashu-art-motion`）白板片段属可选能力：`bash scripts/bootstrap.sh` 联网安装后用 `scripts/render_huashu.sh` 重渲，`scripts/build_composition.py` 把 MP4 回填到 HyperFrames 视频轨。M6 主线不需要它。

## 史实与授权

- 日期、人物、事件措辞按 `content/SOURCES.md` 核验；示意画面必须标注，禁止凭空生成“现场原片”或历史人物原话。
- 示例旁白使用 VoiceStudio 声线“国标视野”，其 OmniVoice 检查点许可为 **CC-BY-NC，仅限非商业发布**；商用前须更换许可匹配的声线。新内容配音使用当前用户配置的 TTS（`scripts/generate_m5_voice.py` 内置的作者声线与端点仅用于复现样片）。
- 配乐由 `scripts/assemble_m5_audio.py` 确定性生成，属本工程原创。字体 OFL；GSAP 随 npm 依赖分发；花叔片段按原仓库（MIT）及其素材例外条款使用。
