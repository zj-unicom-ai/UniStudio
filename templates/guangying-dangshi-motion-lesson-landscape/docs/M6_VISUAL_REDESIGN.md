# EP01 M6 画面重制

## 本版方向

按用户反馈，M6 不再用 Huashu 插画模板承担全片视觉。所有画面直接由 HyperFrames composition 驱动 SVG 绘制，画面事件跟随旁白所讲内容变化。31 个叙事视觉段各自使用对应的历史对象、地点关系、组织结构、时间线或决策关系；不把同一套动画只换文案后重复使用。年份串联只在开篇与片尾回扣一次。

本版复用 M5 的 130 段字幕数据、旁白和音乐，保持文稿、旁白、字幕文字和声音不变。视频时长为 729.78 秒（12:09.78），1920×1080、25 fps。M5 成片和 M4 成片保留不覆盖。

## 封面

片头 0–4 秒默认展示独立设计的党课封面，明确写出主题“从石库门到遵义：在探索中寻找中国革命的道路”、时间范围 1921—1935 和授课人 Walton。封面在最后 0.8 秒淡出；原旁白、字幕与正文画面时序不变。矢量源文件为 `assets/EP01_M6_cover.svg`，独立 PNG 为 `output/EP01_M6_cover.png`；含封面成片为 `output/EP01_M6_cover_final.mp4`，原 M6 无封面成片保留。

## 特别复核

- 10 秒处按当时旁白同时显示 1921、1927、1929、1935 四个年份；年份节点遮住连接线，避免线条划过文字。此处不再出现“上海”地点标签或与之重叠的窗框图形。
- 56 秒处不使用左上角红包块搭配紧邻正文的重复说明牌构图；字幕区与画面内容留有独立空间。
- 上海转嘉兴南湖只画地点关系和水纹，不画容易被误读成 1921 年原船的船形。后续红船场景明确标注“非 1921 年原船”。
- 会址建筑、路线、组织结构、会议文书均标注为示意，不冒充历史照片、原始图表或按比例地图。

## 输出与检查

- Composition：`compositions/EP01_M6.html`
- 党课封面：`assets/EP01_M6_cover.svg`，`output/EP01_M6_cover.png`
- 场景数据：`src/episode-scenes-m6.js`
- SVG 绘制与可寻址动效：`src/graphics-m6.js`
- 新成片：`output/EP01_M6_final.mp4`（H.264/AAC，1920×1080，25 fps，729.8 秒，约 38.2 MB）
- 含封面成片：`output/EP01_M6_cover_final.mp4`（H.264/AAC，1920×1080，25 fps，729.8 秒，约 38.4 MB；封面默认显示于开头）
- 封面版严格检查：`output/m6-cover-review/hyperframes-check.json`；封面转场和 10 秒、56 秒抽帧见 `output/m6-cover-review/` 与 `output/m6-cover-encoded-review/`。严格检查 10 个时间点，lint/runtime/layout 均无错误或警告，对比度 30/30 通过。
- 审阅帧和联系表：`output/m6-review-final/`
- 编码后关键帧：`output/m6-final-encoded-review/`
- 严格检查报告：`output/m6-review-final/hyperframes-check.json`
- HyperFrames 严格检查：在 33 个全片时码运行；lint 0 错误/警告，runtime 0 错误/警告，layout 0 错误/警告，对比度 67/67 通过。
- 项目自带 `npm run verify` 仍验证早期 197 镜草案数据，不是 M6 时序验证；M6 使用 HyperFrames check 和逐时码快照审阅。

## 声音许可

“国标视野”沿用 VoiceStudio OmniVoice 检查点，许可为 CC-BY-NC。该版按用户确认用于非商业发布；商业发布前应换用许可匹配的旁白方案。
