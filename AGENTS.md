# UniStudio · 给 AI 的项目入口

用户把仓库交给你后，使用这里的源码完成「选内容与模板 → 制作 → 登记任务看板 → 按要求发布」。所有路径相对当前仓库根目录，不依赖维护者电脑目录。

## 开始工作

- 先读 `README.md` 和 `docs/AI-WORKFLOW.md`。模板目录为 `templates/catalog.json`；发布能力目录为 `skills/publishers.json`。用户说“模型”但上下文是在选视频样式时，按模板理解；若明确要求 TTS/生成模型，则使用其明确选择。运行本项目的 AI 由用户自备，仓库不内置模型账号。
- 制作前运行 `python3 scripts/unistudio.py doctor --template <模板ID>`。**当前运行环境必须已有可用 HyperFrames 和 TTS 服务**，以及 Node.js/npm、FFmpeg/FFprobe。检查失败时说明缺项，停止依赖该环境的制作；不要自行安装、启动模型服务或悄悄换声线。看板浏览和发布已有成片不依赖 TTS。
- 本机配置为 `unistudio.local.json`，参照 `config/unistudio.example.json`。凭据放环境变量。已有配置和用户已明确的参数直接复用，仅问无法推断且影响执行的缺项。
- 使用本机已安装的 HyperFrames 技能（入口 `hyperframes`），并阅读所选模板的 SKILL（若有）、README、USAGE、TOOLS。不要因为选择了固定模板而重新设计整片风格。

## 制作与看板

1. 明确内容、模板及必需素材。用户只给主题时可按模板整理文案；近期事实核对来源并在新工程 SOURCES.md 记录。明确指定的文案、模型、声线和素材优先。
2. 用 `scripts/unistudio.py new` 复制独立工程并登记 `producing`。模板源码只读；所有编辑和生成都在 `productions/projects/<工程>/`。这里附带的 AGENTS、BRIEF、README 继续适用，但样例的主题、声线、服务地址和账号不能覆盖本期用户选择。
3. 使用当前配置的 TTS 生成新旁白（通用 WAV 适配见 `tts` 命令），然后按模板要求生成 manifest、测量时长、构建、检查、预览和渲染。无旁白模板保留 BGM-only；TTS 服务是工作环境前提，不等于每个模板都必须加旁白。数字人口型等额外能力须单独检查，不能用旧样例口型冒充新台词。
4. MP4 与完整封面统一存到该工程 `deliver/`。模板原生渲染到 out/ 或 renders/ 时，检查后复制到 deliver/ 再登记。不能把样片、静音占位、未核验的渲染结果直接当成正式成片。
5. 检查画面、音轨、字幕、开场与结尾，并执行 `ready`。这是制作流程的必需收尾，不能只给用户一个视频链接而漏掉看板更新。服务与 CLI 共用 SQLite，网页每 15 秒读取。失败用 `production-failed` 记下原因，不能把失败任务标为待发布。

## 发布

- 只有用户要求发布才执行。用户说“把任务看板中的待发布视频发到指定平台”已授权本次范围，不再逐条重复询问相同授权；目标账号或范围有歧义才询问缺项。
- 先查 `list --status ready`，按用户范围筛选；根据 `skills/publishers.json` 找实际 Skill 并读取，再 `claim`。目前仅随附视频号 Skill；未登记的平台说明缺少发布能力，不伪造已接入或发布成功。
- 核对登录账号、成片、封面和定稿字段，按 Skill 操作平台。`claim` 返回的令牌用于本次 `complete`，不写进公开文件或聊天交付。
- 回读**本条作品**的真实平台结果，保存工程内证据，再执行 `complete`。审核中仍以 `platform_pending` 保存真实平台状态；任务看板将它归入“已发布”这一展示分组。排期是 `scheduled`，平台审核结果应以任务记录和回读证据为准。
- 提交结果不明先查平台，不自动重发；用 `needs_human` 记录阻塞。会话中断后走显式 `reconcile`，只有证实未提交才恢复 `ready`。不直接改 SQLite、不按超时自动退回队列。

## 修改本仓库时

尊重已有未提交修改。运行数据、账号、凭据、浏览器 profile、成片均不入库。新增模板遵循 `TEMPLATE-STANDARD.md`；新增平台遵循 `docs/PUBLISHER-CONTRACT.md`。验证核心流程用 `python3 -m unittest discover -s tests -v`；不为验证而向真实平台发视频或调用付费 TTS。
