# 使用方法

命令都在本模板目录内执行。示例素材（配音、口型视频、底图、字体）已随包提供，只跑样例不需要安装 VoiceStudio、OmniVoice 或 MuseTalk。

## 1. 准备工程

| 需要 | 说明 |
| --- | --- |
| Node.js 22+ | 通过 `npx` 拉取固定版本的 HyperFrames CLI（首次需要网络） |
| Python 3 | 构建脚本只用标准库，无 pip 依赖 |
| Chromium、FFmpeg 与 ffprobe | HyperFrames 渲染、封面抽帧和成片规格检查所需，按官方要求准备；ffprobe 随 FFmpeg 提供 |

```bash
npm run check          # 直接检查随包样例
npm run dev            # 浏览器预览
```

## 2. 替换文案

全部内容字段集中在 `data/sample-episode.json`（复制成自己的文件后同步改 `scripts/build_timing.py`、`scripts/build_index.py`、`scripts/prepare_musetalk_audio.py` 顶部的文件名）：

| 字段 | 用在哪 |
| --- | --- |
| `date` | 封面日期卡、来源行 |
| `cover.em` / `cover.lines[]` | 封面主标题（第一行英文强调行 + 一到两行中文主句） |
| `cover.slogan` | 封面副标语 |
| `cover.keywords[]` | 封面三个关键词标签 |
| `stories[].kicker` | 页眉下方的栏目标，如 `01 / 发布` |
| `stories[].title` | 页面大标题（建议 4–8 字） |
| `stories[].facts[]` | 2–3 条事实要点 |
| `stories[].stat` | 大数字数据卡 `{value, label, note}`；填 `null` 时该页改为整页要点排版（示例第 5 页） |
| `stories[].source` | 页脚来源行 |
| `stories[].voice` | 对应 `assets/voice/` 里的 WAV 文件名（不含扩展名） |

页数可增减，构建脚本按数组长度生成页面与转场。标题过长时封面主标题会自动缩号（`fitHeadline()`），正文页标题建议控制在 8 字内。

## 3. 生成配音

`voice-requests.json` 保存分段文本与 TTS 参数（`model`、`voice` 声线配置 ID、`language`、`speed`）。

```bash
python3 scripts/generate_voiceover.py            # 全部分段
python3 scripts/generate_voiceover.py 02-price   # 只重生成某一段
```

脚本默认连接本机 VoiceStudio。使用者须先把 `voice-requests.json` 的 `voice` 字段替换成自己有权使用的声线 ID。更换环境时，可用 VOICE_API_URL 指向 OpenAI 兼容的语音接口，并按服务要求设置可选的 VOICE_API_KEY；不兼容该接口时，直接自备 WAV：

- 格式要求：24 kHz、单声道、16-bit PCM
- 不使用 TTS 时，把各段 WAV 放进 `assets/voice/`，再按真实时长更新 `voice-manifest.json` 的 `duration_s`

## 4. 重建时间轴与 composition

```bash
npm run build      # build_timing.py → approved-timing.json → build_index.py → index.html
```

`build_timing.py` 顶部是一组可调常量：封面起播点、翻页重叠、每页留白、片尾时长。全片长度由 WAV 实测时长推出，因此**第 3 步与第 4 步的顺序不能颠倒**——先有最终配音，再构建时间轴。

## 5. 替换封面口型（只在换配音或换形象时需要）

数字人只出现在封面，所以只有开场白这一段需要口型素材，约 14 秒。

```bash
python3 scripts/prepare_musetalk_audio.py
```

生成 `assets/voice/cover-musetalk-input-16k.wav`：已按 `intro_voice_start` 前置静音，与 composition 里音频轨的起播位置对齐。

用 MuseTalk v1.5 推理（配置写法见 `scripts/musetalk-config.example.yaml`，代码与权重需自行安装）：

- `video_path` → `assets/presenter/host-source.png`（正面人物图）
- `audio_path` → 上一步的 16 kHz WAV

推理得到带背景的 MP4 后，用随包的 alpha 遮罩转成透明 WebM，封面才能压在地球底图之上：

```bash
ffmpeg -y -i host-cover-musetalk.mp4 -i assets/presenter/host-mask.png \
  -filter_complex "[0:v][1:v]alphamerge,format=yuva420p[v]" \
  -map "[v]" -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 3M -auto-alt-ref 0 \
  assets/presenter/host-cover-alpha.webm
```

`host-mask.png` 是人物 alpha 遮罩（与 `host-source.png` 同坐标系、留了画布内边距）。换人物形象时需重新生成这张遮罩，否则透明通道会错位。

## 6. 检查、预览与渲染

```bash
npm run check                                  # 静态 + 无头浏览器门禁
npx --yes hyperframes@0.8.140 snapshot --at 2,20,101 -o snapshots
npm run render -- --output out/my-episode.mp4
```

`npm run render` 会在 MP4 旁生成完整首页封面 PNG（默认取视频 2 秒处）和带 poster 的播放页 HTML，并用 ffprobe 校验 1080 × 1920、30 fps、时长和音轨。交付前仍需目视核对封面、正文页、片尾及音画同步。

渲染前至少核对三帧：封面（第 0 帧应为干净暗场，人和版式一起淡入）、正文页、片尾。

## 常见问题

| 现象 | 原因与处理 |
| --- | --- |
| 封面嘴型比声音早约 0.8 秒 | 口型音频没有前置 `intro_voice_start` 的静音。重跑 `prepare_musetalk_audio.py` 后再推理 |
| 检查报 `clip_media_fit`（音频比槽位短/长） | `voice-manifest.json` 与 WAV 不一致。重跑第 3 步，或直接按 WAV 实测值修正，再 `npm run build` |
| 正文页之间出现文字重影 | 页眉已抽成常驻层，若把页眉写回页面内，翻页交叠期会双层叠字 |
| 只有形象人浮在黑底上 | 透明口型视频是独立合成图层，遮罩压不住它；`#presenter` 需要自己跟随开场淡入（工程已这样处理） |
| 标题被裁或换行 | 封面主标题按 `white-space: nowrap` + 自动缩号处理；正文页标题过长请改文案而不是改字号 |
| 中文渲染成系统字体 | `assets/fonts/NotoSansSC-VF.ttf` 未随工程移动，字体声明为 `font-display: block`，缺文件会回退 |
| 以为透明通道坏了 | ffprobe 会报 `yuv420p`，ffmpeg 自带的 vp9 解码器也不读 WebM 的 alpha 附加平面。验证要强制走 libvpx 解码：`ffmpeg -c:v libvpx-vp9 -i host-cover-alpha.webm -frames:v 1 -pix_fmt rgba check.png`，或直接看渲染结果 |
