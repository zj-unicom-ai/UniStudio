---
name: gangge-ai-international-vision
description: 使用随包参考工程制作“刚哥聊 AI｜国际视野”竖屏视频，保留动态地球、自然开场和完整品牌片尾，交付 MP4、完整封面 PNG 和播放页。用户要求用国际视野模板生成视频或修改该系列时使用。
---

# 刚哥聊 AI｜国际视野

本 skill 自带可复制的参考工程，不需要分享者电脑上的项目、模板或品牌素材。用户当前要求优先；保持已确认的系列风格。

## 开始新项目

1. 根据用户给定的稿件、资料包、链接或主题整理内容。只有输入目录中实际存在项目说明时才读取；没有 `AGENTS.md`、brief、分镜或来源文档也可以从零开始。
2. 先读取随包 [参考工程说明](assets/template-project/README.md)，再用 `python3 <本skill目录>/scripts/new_project.py <新项目目录>` 复制整个 [参考工程](assets/template-project/)。不覆盖旧工程，不重新凭文字描述仿造模板，不遗漏品牌组件的资源目录。
3. 检查 Node.js 22+ / npm、Python 3、FFmpeg/FFprobe 与浏览器能力。参考工程使用固定 HyperFrames 0.8.133；首次通过 npx 获取。缺少依赖时说明具体项并给出当前系统的安装指引，不把 skill 安装等同于渲染工具已安装。

## 修改内容与旁白

- `story-data.json`：替换本期标题、日期、来源行、场景 HTML 和场景标题；保留 `base_css`、地球和品牌视觉。`scene_boundaries` 是每页首段旁白在 segments 中的零基索引。
- `voice-requests.json`：替换分段稿，编号与 `assets/voice-guobiao/<id>.wav` 对应。新工程中的 WAV 是静音演示，不能当成正式配音。
- 用使用者实际可用的授权 TTS，或直接导入分段 WAV。可选适配器 `scripts/generate_voiceover.py` 的 endpoint、model、voice 均由使用者配置；不依赖分享者的 VoiceStudio 地址、profile 或密钥。原机“国标视野”是用户确认的声线，其他机器仅在确实拥有同一声线时使用，否则说明需要配置自己的声线。
- 导入真实 WAV 后执行 `npm run compose -- --narration`。时间线按 WAV 实际时长构建；缺音频时报错，不使用估算代替。没有旁白能力时先做稿件与画面工程；只有用户接受无旁白版本时才交付静音版本。
- 事实与评论分开，在 `SOURCES.md` 记录来源、日期和限定。无法读取给定链接时请用户提供正文，不编造事实；日期不明时不把资料写成当日新闻。

## 固定视觉与完整封面

- 1080×1920、30fps；保留深蓝底、低对比度动态地球、原 v3 的轻微上移淡入及标题遮罩揭开。品牌片尾、Logo、三段片尾音效和翻页音效已经随工程包含，末帧完整保持。
- **每期必须另外输出完整版本的首页封面 PNG（1080×1920）**，完整显示标题、日期和主要视觉信息，能独立用于平台发布。默认从 MP4 **0.7 秒**处提取标题入场已完成的画面。视频保留原开场，封面不强制等于第 0 帧；播放页以完整 PNG 作为 poster。
- 附带 Noto 中文字体与原 OFL 许可证，以便其他系统保持稳定排版。它替代原机苹方，字形略有差别；需要逐帧完全相同时，使用者须自行提供同一字体及配音条件。详细视觉说明见 [视觉基准](references/visual-style.md)。

## 检查与交付

运行 `npm run check`，修复错误；检查开场 0–0.8 秒、正文、完整封面和固定片尾。使用 `npm run render -- --output renders/<名称>.mp4` 同时生成 MP4、`_封面.png`、`_播放页.html`，字幕在 `renders/subtitles.srt`。用 ffprobe 核验 1080×1920、30fps、时长与音轨；目视确认封面完整、音画同步、最终帧无空白。

仅验证模板时可 `npm run render -- --allow-demo`，该样例有背景音效但无旁白，不能冒充正式有声作品。交付时单独列出 MP4、完整封面、播放页与源工程路径，并注明配音条件或仍缺少的依赖。

随包工程的资源来源及权利说明见 [THIRD_PARTY_NOTICES.md](assets/template-project/THIRD_PARTY_NOTICES.md)。公开仓库权限与素材许可证遵循使用者的授权；使用 skill 不表示已授权向外发布视频或仓库。
