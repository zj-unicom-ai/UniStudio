# 来源记录 · 2026-10-08 · Anthropic 补齐 Claude 5.5 家族

## 主事件页

- 事件：Anthropic 发布 Sonnet 5.5 与 Haiku 5.5，下调缓存读取价
- 聚合页：https://aihot.news/story/94903954-cf87-48d8-89a6-eff5deefeaa0
- 抓取时间：2026-10-08（浏览器渲染取原文，curl 直取被 403 拦截）
- 页面自述规模：71 篇报道 / 29 个报道来源 / 19 个事件进展；最近一次更新 10 月 8 日 06:26；页面标注"热点榜第 1 名"
- 页面标注"AI 根据报道生成"的综述段落仅作导航，本文所有数字均回到单条报道核对

## 已确认事实（官方一手）

| 事实 | 出处 |
| --- | --- |
| Sonnet 5.5 于 9 月 28 日发布，Claude 5.5 家族第二款模型，比 Sonnet 5 快 30% 以上，多数工作成本最多降 30%，定价维持输入 $2 / 输出 $10 每百万 token | Anthropic Newsroom，2026-09-28 08:00 |
| Terminal-Bench 4.0 得分 70.6%，Sonnet 5 为 10.3% | MarkTechPost / Rohan Paul，9 月 29 日 |
| Sonnet 5.5 成为 claude.ai 免费档位模型 | Simon Willison 博客，9 月 29 日 06:07 |
| Haiku 5.5 于 10 月 7 日发布，官方称迄今最便宜、最快、能力最强的小模型，平均运行成本比 Haiku 4.5 低约 75% | Anthropic Newsroom，10 月 7 日；Claude，10 月 8 日 02:01 |
| Sonnet 5.5 缓存读取价 $0.20 → $0.10 每百万 token（减半），官方称长期运行任务成本因此再降约 20% | Claude，10 月 8 日 02:01 |
| Haiku 5.5 定价：10 万 token 以内输入 $0.10 / 输出 $0.50 / 缓存读取 $0.01；超过 10 万 token 升至 $0.50 / $2.50；Haiku 4.5 为输入 $1.00 / 输出 $5.00 | Claude 定价表报道，10 月 8 日 02:01 |
| Haiku 5.5 支持 1M token 上下文、128k 最大输出、首个带 effort 参数与自适应思考的 Haiku | Claude Platform 开发者版本说明，10 月 7 日 |
| 上线渠道：Claude 平台、Claude Code、AWS、Google Cloud、Azure；Sonnet 5.5 另有 Cursor、OpenRouter；Haiku 5.5 另有 OpenRouter、OpenCode、Devin、Arena | 各家公告，9 月 29 日—10 月 8 日 |

## 第三方评测（非官方结论，需归因）

- Artificial Analysis：Sonnet 5.5 智能指数 56 分，排第 2，仅次于 Opus 5.5 (max)，max effort 下比 Sonnet 5 高 18 分（9 月 29 日 02:31）。Haiku 5.5 得 43 分，一年内比上一代 Haiku 提升 26 分（10 月 7 日）。该机构同时提示 Haiku 5.5 的成本数据尚未计入超 10 万 token 的阶梯涨价。
- Arena：Agent Arena 中 Sonnet 5.5 (Max) 排第 3、净提升 +12.5%，Chat 类别 +15.6% 排第 1；单任务中位成本 $2.74，比排第 2 的 Opus 5.5（$1.58）高约 73%，未进入 Pareto 前沿（10 月 3 日 03:33）。Code Arena: WebDev 中 Sonnet 5.5 (High) 以 1699 分排第 4（9 月 30 日 02:15）。
- Cognition：Haiku 5.5 在 FrontierCode 1.1 得分 58.4%，每任务成本约为 Sonnet 5 的八分之一（10 月 8 日 05:15）。属厂商自测。

## 破坏性变更与不确定性

- Claude Platform 版本说明记载：Haiku 5.5 上 manual extended thinking 返回 400 错误，为 Haiku 4.5 编写的代码可能失效（10 月 6 日 08:00 条目）。
- 部分媒体把 10 万 token 以内的降幅写作"最高达 90%"，与官方"平均约 75%"口径不同，本片刻意只采用官方"平均低约 75%"，未使用 90% 表述。
- "最便宜、最快、能力最强"均为 Anthropic 官方自我定位，旁白中已加"官方称"限定。
- 榜单排名会随投票量变化，Arena 数据为 10 月 3 日快照。

## 本期未采用的信息

- Max / Team 计划新增每月 API credits（与主线价格话题关联弱）
- 公众号实测对比（代码动画、3D 等主观评测，不足以作为事实陈述）
- 热度走势图数值（503 / 518，属平台内部指标）

## 样例媒体与再分发状态

以下是模板可运行样例的一部分。它们不受本仓库 MIT 代码许可自动覆盖；发布模板、封面截图或完整样片前，需确认对应权利，或替换为来源和授权可证明的素材。

| 路径 | 用途 | 当前记录 / 发布前处理 |
| --- | --- | --- |
| `assets/bg/earth-base.png`、`assets/bg/earth-network.png` | 正文与封面底图 | 来自原栏目工程；本包未记录原始来源与再分发许可，需确认或替换 |
| `assets/presenter/host-source.png`、`host-mask.png`、`host-cover-alpha.webm` | 数字人原始形象、遮罩及口型视频 | 来自原栏目工程；需确认人物肖像、口型合成与公开分发许可，或改用获准形象 |
| `assets/voice/*.wav` | 样例旁白和口型输入音频 | 由原 VoiceStudio / OmniVoice 工作流生成；需确认对应声音/声线与音频的公开分发范围，或换成获准声音 |
| `assets/brand/logo-lockup.png`、片尾组合及其音效资源 | 栏目标识与固定片尾 | 用户此前明确允许该品牌 Logo 与片尾音效进入公开仓库；授权不转让商标权，也不表示第三方背书 |
| `assets/sfx/page-whoosh.mp3` | 正文翻页音效 | 来自原栏目工程；目前未记录其来源及公开分发许可，需确认或替换 |
| `preview/cover.png`、`preview/*.png`、`preview/full-sample.mp4` | 文档预览图和样片 | 含上述示例媒体的衍生交付物；授权未确认前不要公开发布，清理或重制后再分享 |
| `assets/fonts/NotoSansSC-VF.ttf` | 中文字体 | SIL OFL 1.1；原文随包保留在 `assets/fonts/OFL.txt` |
| `assets/vendor/gsap.min.js` | 动画运行库 | 保留 GSAP 原版权头与适用许可说明，见 `TOOLS.md` |

样例事实来源仍按本文件前文记录；事实来源署名与画面媒体许可是两项独立检查。
