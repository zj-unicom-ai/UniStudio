# 国际视野参考工程

本目录是完整可复制的 HyperFrames 工程。已经包含动态地球、原 v3 自然标题进场、固定六秒片尾、品牌 Logo、切页/片尾音效、GSAP 3.14.2 和 Noto 中文字体。没有依赖分享者的文件路径。样例三段 WAV 是静音轨，便于无 TTS 环境验证画面与音效；不是国标视野样音。

## 先运行样例

需要 Node.js 22+ / npm、Python 3、FFmpeg / FFprobe 和 HyperFrames 可用的浏览器。首次 CLI 运行通过 npx 下载固定版本 HyperFrames 0.8.133；网络/账号/额度仍按工具本身要求。

```sh
npm run compose
npm run check
npm run render -- --allow-demo --output renders/template-demo.mp4
```

这会生成无旁白的样例 MP4、完整首页封面 PNG、poster 播放页以及字幕。音效在切页与片尾正常播放。`npm run dev` 可打开编辑预览；完成后用 `npx --yes hyperframes@0.8.133 preview --stop` 停止。

## 制作新一期

复制本目录到新项目后修改 `story-data.json` 与 `voice-requests.json`。保留 `base_css`，替换 `scenes` 的画面内容、`scene_titles`、`date_label`、`source_line`，以及 `scene_boundaries`（每页第一段旁白在 segments 中的零基索引）。段数不限。

配音可任选一种：

- 导入音频：按 `segments[].id` 命名，例如 `assets/voice-guobiao/00.wav`。用真实旁白替换静音轨，运行 `npm run compose -- --narration`。
- 使用已配置的授权 TTS：运行 `python3 scripts/generate_voiceover.py --url YOUR_SPEECH_ENDPOINT --voice YOUR_VOICE --model YOUR_MODEL`。如需 API key，通过 `TTS_API_KEY` 环境变量提供；不要写进仓库。适配器请求 WAV；不同服务的字段如不兼容，应调整请求或直接导入 WAV。

然后执行 `npm run compose`、`npm run check`、`npm run render -- --output renders/episode.mp4`。默认生成同名 `_封面.png` 和 `_播放页.html`。WAV 的真实时长决定场景和字幕时间；音频缺失时直接报错，不能用估算冒充同步。

## 完整封面与动效

保持原 v3 的开场上移淡入、标题遮罩揭开，独立封面从视频 **0.7 秒**处提取，完整显示首页标题与信息。封面 PNG 不要求与视频第 0 帧相同，以免牺牲用户已确认的开场动效。发布平台请选择导出的完整 PNG，播放页也绑定它作为 poster。

## 固定片尾

`compositions/gangge-ai-outro.html` 和 `compositions/gangge-ai-outro/` 的 Logo、音效已完整包含；资源均相对工程根目录。不要只复制 HTML 而遗漏附属素材。更新日期/内容无需修改片尾组件。

Noto 替代原机苹方，字形与原视频存在少量差别；结构、地球、开场和品牌组件沿用原工程。详细第三方来源见 THIRD_PARTY_NOTICES.md。
