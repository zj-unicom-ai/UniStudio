# 光影党史｜动态党课 · 制作 Skill

用本模板制作党史/红色主题长视频时，按此 Skill 执行。硬门来自 EP01 制作中用户确认过的要求（见 `AGENTS.md`），不因选题更换而放松。

## 史实硬门

1. 日期、人物、事件措辞和引用逐条核验并记录到工程 `content/SOURCES.md`；新增真实档案须另行检查出处与授权。
2. 代码绘制的纸张是抽象内容结构，不是历史原文扫描；路线、会址、组织图为关系/方向示意，不是行军地图。所有示意画面必须明确标注。
3. 禁止凭空生成看似“现场原片”的会议影像或历史人物原话。

## 风格约束

- 全片统一赤金、墨黑、档案米白；不使用卡通 Q 版角色、紫蓝科技渐变。
- 优先源代码动画（SVG/Canvas）：时间线、史料层次、历史地点、组织关系、会议决策各自成画；每 2–8 秒发生一次有意义的构图或信息变化，禁止平均匀速 zoom、空背景和纯翻页。
- 静态插画不得成为整片主体；相邻章节不得复用同一套动画只换文案。
- 字幕按旁白 ASR 真实时码对齐，使用单一时码图层，避免残影。

## 新一期制作流程

1. **脚本**：按 `content/EP01_SCRIPT_M5.md` 结构写分章口播稿（`## S01｜章名` + `**口播**`），章数自定，同步改脚本里的章数校验。
2. **配音**：分章生成 WAV 写入 `output/voice-m5/S01.wav…`（新工程沿用此目录约定或改脚本路径）。优先用当前用户配置的 TTS：`python3 scripts/unistudio.py tts --text-file <章节txt> --output <章节wav>`；`scripts/generate_m5_voice.py` 可拆分章节文稿，但其中作者声线与端点仅用于复现样片，不得用于新内容。
3. **合流**：`python3 scripts/assemble_m5_audio.py` 合并旁白、生成原创配乐，并更新 `output/voice-m5/manifest.json`。
4. **时码**：用本地 ASR 为分章 WAV 生成词级时码（参考 `scripts/transcribe_m5_voice.py`；`scripts/transcribe_m4_voice_mps.py` 为另一实现）。
5. **时间线**：`python3 scripts/build_m5_timeline.py` 按真实音频时长重排镜头与字幕，更新 `src/episode-data-m5.js`；不强凑固定片长。
6. **画面**：更新 `src/episode-scenes-m6.js` 段落映射与 `src/graphics-m6.js` SVG 场景（或改用 `compositions/EP01_M5.html` 的 Canvas 语法）；封面改 `assets/EP01_M6_cover.svg` 并导出 PNG。
7. **构建与验收**：`npx --yes hyperframes@0.8.152 lint` / `check`（严格模式，lint/runtime/layout 零错误零警告）→ `preview` 人眼核对开场、转场、片尾 → `render` 全片。
8. **交付**：MP4 与完整封面 PNG 放工程 `deliver/`，执行 UniStudio `ready` 登记；检查说明写明实际做过的检查。

## 验收硬门

- 100% 镜头有具体“物 + 动作”；静态插画不成主体；示意与史料严格区分。
- 旁白与字幕按真实时码对齐；样片静音占位不能充当正式配音。
- 只有真正完成 HyperFrames render 并经人眼复核的视频才能登记为成片。
- 商用发布前确认旁白声线许可；随包“国标视野”示例仅限非商用。
