# 技术栈与本地依赖

本模板使用 HyperFrames 将单页 HTML composition 渲染为竖屏 MP4；图片、固定文案与 BGM 由 JSON 样例填充，不调用云端生成服务。

## 技术与工具

| 技术 / 工具 | 用途 | 随包提供 / 本地要求 |
| --- | --- | --- |
| HyperFrames `0.6.46` | 检查、预览与渲染 composition | 版本固定于 `package.json`；首次 `npx` 运行时下载 CLI |
| HTML、CSS、JavaScript | 全息背景、中央图片框和计时动画 | `templates/index.template.html` 随包提供 |
| GSAP `3.14.2` | 图片放大、推入和旋转转场 | 从 jsDelivr CDN 加载，不随包；运行检查或渲染时需要网络 |
| Python 3（标准库） | 校验 JSON、生成 `index.html` | 本地安装 Python 3，无第三方依赖 |
| Node.js 22+、npm | 调用 HyperFrames CLI | 本地安装；首次获取 CLI 需要网络 |
| Chromium、FFmpeg、ffprobe | 运行检查、预览、MP4 编码、抽取完整封面与检查输出规格 | 按 HyperFrames 当前环境要求在本机准备；ffprobe 随 FFmpeg 提供 |

## 音频与媒体生成

- **语音：** 未使用旁白、数字人或 TTS。
- **配乐：** `assets/audio/dynamic-bgm.mp3` 是用户指定的音频文件，原文件随包提供。BGM 播满一段后从头重复，直到成片结束；无需配置 VoiceStudio。
- **音效：** 未使用。
- **图片生成：** 制作新一期不要求图像生成工具；可以直接替换 `assets/images/` 中的图片。

## 第三方素材与依赖

图片和 BGM 来源及各自的使用说明见 [`SOURCES.md`](SOURCES.md)。其中 Google DeepMind 页面图片、用户提供的背景图和 BGM 有独立权利范围；仅保留出处不代表取得再分发许可。发布前请按实际用途复核。

GSAP 的许可与说明见 [GSAP 官方许可页面](https://gsap.com/licensing/)。HyperFrames CLI 按其上游项目许可分发；本模板源码许可见仓库根目录的 MIT `LICENSE`。
