# 技术栈与本地依赖

本模板是一个纯 HTML/CSS/GSAP 的 HyperFrames 竖屏产品 Promo 工程,不调用云端生成服务;填充脚本为纯 Python 标准库。

## 技术与工具

| 技术 / 工具 | 用途 | 随包提供 / 本地要求 |
| --- | --- | --- |
| [HyperFrames](https://hyperframes.heygen.com/) `0.8.138` | 编排、检查、预览和渲染视频 | 版本固定于 `package.json`;`npx --yes` 首次运行时下载 CLI |
| `@hyperframes/core` `0.8.138` | HyperFrames composition 运行时 | 固定为 npm 开发依赖 |
| HTML、CSS、JavaScript | 六页场景、版式、时间线与内容 | `index.html`(示例)与 `templates/index.template.html`(令牌化)随包提供 |
| [GSAP](https://gsap.com/) `3.14.2` | 全部入场/环境/掠光动效 | 经 jsDelivr CDN 引入,不随包;遵守 GSAP 官方标准许可 |
| Python `3`(标准库) | `fill.py` 把 `content.*.json` 填充进令牌化模板 | 需要本地 Python3,无第三方依赖 |
| Node.js `22+`、npm | 调用 HyperFrames CLI | 需要本地安装;首次获取 CLI 需要网络 |
| Chromium、FFmpeg | 运行检查、预览与 MP4 导出 | 按 HyperFrames 当前环境要求在本机准备 |

本模板不需要 TTS、数字人或模型权重;渲染 26.5s 竖屏样片在硬件 GPU 下约 20s(`PRODUCER_BROWSER_GPU_MODE=hardware`)。

## 内容生成与媒体

- **语音:** 未使用 TTS 或语音生成;样片只有配乐、无旁白。加旁白需自行接入 TTS 并做 ducking。
- **数字人:** 未使用数字人框架或数字人视频。
- **产品画面:** `assets/hero.jpg` 与 `assets/macro.jpg` 为 **AI 生成的虚构品牌占位图**(随包提供,已裁除生成水印)。替换为自己产品图时请确认品牌与肖像/专利外观的展示权限;规格建议见 `USAGE.md` 第 2 节。
- **图像 / 视频生成:** 制作新内容不需要图像生成工具;占位图仅用于演示视觉系统。
- **背景音乐:** `assets/bgm.mp3` 随包提供,为 Mixkit 免费授权曲《Trap Electro Vibes》(id 126),从 10s 裁 26.5s 并加淡入淡出;授权说明见 [`THIRD_PARTY_LICENSES/MIXKIT.md`](THIRD_PARTY_LICENSES/MIXKIT.md)。换曲请沿用可公开分享且适用于目标用途的音频。

## 第三方素材与许可

| 文件 / 素材 | 来源与说明 |
| --- | --- |
| GSAP `3.14.2`(CDN) | 动效运行库;使用条款见 [`THIRD_PARTY_LICENSES/GSAP-Standard-License.md`](THIRD_PARTY_LICENSES/GSAP-Standard-License.md) |
| Noto Sans SC / Archivo / JetBrains Mono | Google Fonts CDN 引入,均为 SIL OFL 1.1 开源字体,不随包;见 [`THIRD_PARTY_LICENSES/FONTS.md`](THIRD_PARTY_LICENSES/FONTS.md) |
| `assets/bgm.mp3` | Mixkit 免费授权曲,可商用;见 [`THIRD_PARTY_LICENSES/MIXKIT.md`](THIRD_PARTY_LICENSES/MIXKIT.md) |
| `assets/hero.jpg`、`assets/macro.jpg` | AI 生成的虚构品牌占位产品图,按仓库根目录许可随模板分发 |

仓库根目录的 MIT 许可不取代上述第三方条款。使用者应在修改及再发布前查看本文件和第三方许可说明。
