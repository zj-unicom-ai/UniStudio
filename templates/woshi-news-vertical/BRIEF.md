---
workflow: general-video
flow: automation
storyboard: "no"
message: "AA-Robotics v0.1 将前沿语言模型带入六轴机械臂的理解、规划与执行测试。"
destination: vertical-social-video
aspect: 1080x1920
language: zh-CN
audience: 关注 AI 与科技资讯的中文短视频观众
length: "约 43 秒，以真实旁白时长为准"
voice: "VoiceStudio 已保存音色「女播报快节奏」（c5a1e453）"
---

## Intent

按「沃资讯快播」品牌规范制作一条竖屏单条新闻视频，呈现 Artificial Analysis 发布 AA-Robotics v0.1 研究预览、测试前沿语言模型控制六轴机械臂在物理世界中的理解、规划和执行能力、首批公布八项任务结果。受众为关注 AI 与科技的中文短视频观众。内容以事实播报为主，并用简短解释说明语言模型从给出建议到实际控制动作之间的差别。

## Assets

- `/Users/wrg/Downloads/科技资讯快播-HyperFrames规范包/` — 视觉、动效、音频和交付规范；概念图只作视觉参照，不作为成片背景。
- 本期新闻事实 — 用户在当前请求中提供的摘要，作为脚本输入；官方八项结果的原始页面尚未独立找到，见 `SOURCES.md`。

## Customizations

- 固定使用 VoiceStudio 已保存音色「女播报快节奏」（profile_id=c5a1e453），通过参考录音克隆生成；默认语速 1.0，不另行设计女声。
- 按规范使用顶部栏目和固定日期、中部至少四张可替换图片，依旁白语义逐张展示、底部语义摘要与连续低亮度科技波形；不加 BGM，让旁白保持清楚。
- 内容数据集中保存在 `data/episode.json`，可复制并替换为下一条资讯。

## Notes

- 画布为 1080×1920、30fps，日期固定为 `2026.10.15`。
- 不显示进度条、计时、倒计时、页码或图片序号；不补造模型成绩、任务名称或测试条件。
- 机械臂及场景图形为原创 SVG 示意图，不代表 Artificial Analysis 的实测照片或界面。
- 暂无可独立核验的官方发布/结果链接；本期按用户给定事实制作审阅稿，发布前应补上原始来源。
