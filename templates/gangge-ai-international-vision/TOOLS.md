# 工具、运行要求与素材来源

| 工具或资源 | 用途 | 随包情况 / 重新生成要求 |
| --- | --- | --- |
| HyperFrames 0.8.133 | composition 检查、预览、渲染 | CLI 经 npx 获取；需 Node.js 22+、npm、浏览器和 FFmpeg |
| Python 3 | 数据生成工程、复制项目、WAV计时、导出封面/播放页、可选TTS适配 | 全部脚本随包；Python 需本机安装 |
| FFmpeg / FFprobe | 编码、封面抽帧及成片规格检查 | 需本机安装并在 PATH 中可用 |
| GSAP 3.14.2 | 可 seek 地球、标题与片尾动画 | 本地 JS 随包，保留原版权头与 GSAP Standard License |
| Noto Sans CJK SC Regular | 确定的中文字体 | OTF与SIL OFL原文随包；替代未分发的苹方字体 |
| 品牌片尾、Logo、音效 | 系列统一收尾和翻页声音 | 实际文件已包含；用户明确允许在公开仓库中提供 |
| 演示 WAV | 无TTS条件下验证时间线 | 随包，Python生成纯静音，不含私人声线 |
| 可选 TTS HTTP 适配器 | 获取正式分段 WAV | 不附模型/权重/账号；endpoint、model、voice由使用者配置，也可自行导入音频 |

样例不使用数字人、口型模型、图片/视频生成或背景音乐。原作品曾使用 VoiceStudio / OmniVoice“国标视野”声线，但本模板没有硬编码该私有 profile，不要求别人安装作者的 VoiceStudio 工程。

字体来源：https://github.com/notofonts/noto-cjk ，许可原文 `THIRD_PARTY_LICENSES/Noto-OFL.txt`。GSAP：https://gsap.com/ ，标准许可 https://gsap.com/community/standard-license/ 。完整资源说明见 `assets/template-project/THIRD_PARTY_NOTICES.md`。源码沿用根仓库 MIT；第三方资源不因模板源码许可而改变各自条款。
