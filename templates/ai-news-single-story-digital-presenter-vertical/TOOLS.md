# 技术栈与本地依赖

本模板以 HyperFrames 编排竖屏单条资讯节目，封面使用数字人口型。**仅构建、检查、预览或渲染随包样例时，不需要安装语音生成器或 MuseTalk**；换配音或换人物形象时，需要另行生成旁白与封面口型素材。

## 技术与工具

| 技术 / 工具 | 在模板中的用途 | 随包提供 / 本地要求 |
| --- | --- | --- |
| [HyperFrames](https://hyperframes.heygen.com/) `0.8.140` | composition 检查、可 seek 时间线、预览与 MP4 渲染；`compositions/gangge-ai-outro.html` 作为子组合挂载 | 版本固定在 `package.json`；需要本地 Node.js/npm，首次执行 `npx` 会下载 CLI 及运行依赖 |
| HTML、CSS、JavaScript | 页面结构、版式与音画时间线 | 源码随包提供 |
| [GSAP](https://gsap.com/) `3.14.2` | 封面淡入、地球缩放、星圈轨道、标题滑光与翻页转场 | `assets/vendor/gsap.min.js` 已随包提供，无需另装；片尾子组合另带一份同版本副本 |
| Python 3 | `generate_voiceover.py` 调 TTS 并记录 WAV 实测时长；`build_timing.py` 由时长推时间轴；`build_index.py` 生成 composition；`prepare_musetalk_audio.py` 生成封面口型音频 | 脚本只用标准库 + FFmpeg 调用，无 pip 依赖 |
| Node.js / npm | 调用固定版本的 HyperFrames CLI | 需要本地安装 |
| Chromium 与 FFmpeg | 页面渲染与视频编码；FFmpeg 还用于口型音频重采样和透明通道封装 | 按 HyperFrames 运行要求在本机准备 |
| [VoiceStudio](https://github.com/debpalash/VoiceStudio) + [OmniVoice](https://github.com/k2-fsa/OmniVoice) | 示例旁白的语音生成（男播音声线） | 示例 WAV 已放在 `assets/voice/`；VoiceStudio、OmniVoice 模型与声线配置不随模板提供。`voice-requests.json` 里的 `voice` 是作者本机的声线 ID，换环境需替换，或自备 24 kHz 单声道 16-bit WAV |
| [MuseTalk](https://github.com/TMElyralab/MuseTalk) `v1.5` | 让封面人物形象按开场白生成口型同步视频；它不负责从零创建形象 | 示例口型视频 `assets/presenter/host-cover-alpha.webm` 已随包提供；MuseTalk 代码与模型权重不含在模板内 |
| [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC) 可变字体 | 封面、正文与片尾的中英文排版（含 900 字重） | `assets/fonts/NotoSansSC-VF.ttf` 随包提供，采用 SIL Open Font License 1.1，许可证文本见 `assets/fonts/OFL.txt`；片尾也使用该字体，避免依赖外部字体服务 |

HyperFrames 可能提示该字体大于内联上限、将保持文件引用。这是体积提示：字体文件在包内，使用整套模板工程构建和渲染即可解析；不要只复制 `index.html`。

原示例的 MuseTalk 推理由 Apple Silicon 的 MPS 环境完成。上游安装说明推荐 Python 3.10、CUDA 11.7 与 PyTorch 2.0.1，并需另行下载模型权重；不同操作系统与硬件的安装方式不同，请按[上游安装说明](https://github.com/TMElyralab/MuseTalk#installation)核对本机支持情况。只要复用随包的口型视频，就无需配置该环境。

## 样例与新内容所需环境

| 任务 | 需要准备 |
| --- | --- |
| 构建、检查、预览和渲染随包样例 | Python 3、Node.js/npm、HyperFrames CLI 运行环境、Chromium 与 FFmpeg |
| 更换旁白文本或声线 | 本地可用的 TTS（VoiceStudio/OmniVoice 或其他）或录音；输出 24 kHz、单声道、16-bit PCM WAV |
| 为新开场白生成封面口型 | 单独安装 MuseTalk v1.5 及其 Python/PyTorch 依赖、获取模型权重、准备 FFmpeg，并按本机环境填写 `scripts/musetalk-config.example.yaml` |
| 更换人物形象 | 新的正面形象图（`assets/presenter/host-source.png` 位置）与对应的 alpha 遮罩（`host-mask.png` 位置）；遮罩需与原图同坐标系 |

## 随包素材

- `assets/voice/`：示例旁白 WAV，以及由 `prepare_musetalk_audio.py` 生成的封面口型输入（含前置静音）。
- `assets/presenter/host-source.png`：MuseTalk 输入形象；`host-mask.png`：透明合成用的 alpha 遮罩；`host-cover-alpha.webm`：示例口型成品（VP9 + alpha 附加平面）。
- `assets/bg/`：地球写实底图与网络弧线层，两层按拟合圆心对齐，替换任一层都要重新核对节点与光晕坐标（见 `README.md` 图层说明与 `USAGE.md`）。
- `assets/brand/`：栏目 Logo 组合图。
- `assets/sfx/` 与 `compositions/gangge-ai-outro/assets/sfx/`：翻页嗖声与片尾进场音效。
- `SOURCES.md`：示例这一期的事实来源与取舍记录，供写作口径参考。

示例封面底图、人物形象、音色、Logo 与节目音效来自原栏目工程，其权利与模板源码许可分开。公开本模板前，须确认人物肖像/口型视频、样例配音、背景图、Logo、音效以及含有这些素材的预览图和样片均获准再分发，或先替换为明确可分享的素材；当前具体素材清单与待确认项见 [`SOURCES.md`](SOURCES.md)。制作自己的内容时，请换成本人或已获授权的素材，尤其注意人物形象与声音的可商用边界。MuseTalk 代码、模型权重以及 VoiceStudio 的声线数据不随模板分发；使用第三方工具与模型前，请查看各自授权条款。

GSAP 许可说明见随文件保留的版权头与[官方许可页面](https://gsap.com/community/standard-license/)。字体遵循其 OFL 条款（保留版权声明与 `OFL.txt`）。第三方工具与媒体素材各自受其来源条款约束。
