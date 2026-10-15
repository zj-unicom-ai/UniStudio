# UniStudio · AI 视频创作工作台

UniStudio 是由数字员工驱动的视频创作工作台。重复繁琐的制作交给数字员工 7×24 小时完成，成片自动送达各内容平台，时间留给创作本身。

把项目交给 AI，告诉它**制作什么内容、使用哪个视频模板**，即可在已配置的环境中制作成片，并自动登记到任务看板。之后再说“把看板里的待发布视频发布到视频号”，AI 会读取项目中的发布 Skill、操作对应平台，并回写实际发布状态。

UniStudio 由浙江联通 zj-unicom-ai 团队维护，提供 HyperFrames 视频模板、AI 操作规范、本地任务看板和可扩展的发布技能。运行 AI 的工具与模型由使用者选择；本仓库不内置 AI 推理服务。

## 使用前提

**制作视频要求当前运行环境已经具备 HyperFrames 和可用的 TTS 服务。** 本项目复用这些服务，不负责安装或部署语音模型。还需 Python 3.10+、Node.js 22+、npm、FFmpeg/FFprobe，以及 HyperFrames 所需浏览器环境。各模板保留自己的 HyperFrames 版本，首次运行固定版本脚本可能需要网络；版本以模板 package.json 为准。

- TTS 默认适配 OpenAI-compatible `/v1/audio/speech`，WAV 输出。其他协议可接入适配服务，或按模板说明调用已有服务后导入 WAV。
- 声线必须是当前服务支持且获准使用的声线，不能直接照搬示例的私有 ID。`doctor` 检查健康接口，实际模型/声线由首次配音验证。
- 无旁白模板保留 BGM-only。TTS 是制作环境前提，不会强行给无旁白模板加口播。
- 数字人开场的新口型另需 MuseTalk 等服务；仅 HyperFrames + TTS 不包含口型推理能力。
- 浏览看板或发布已有成片不需要重新检查 TTS。发布视频号另需真实 Chrome、`agent-browser` 和用户完成登录。

## 快速开始

从仓库根目录执行：

```sh
cp config/unistudio.example.json unistudio.local.json
# 编辑本机配置：已有 HyperFrames 命令、TTS 地址、model、voice；如需发布，再填目标账号
python3 scripts/unistudio.py doctor
python3 web/serve.py
```

浏览器打开 [本地工作台](http://127.0.0.1:8610/)。**只需一个网页服务**，内置任务 API，首次启动自动创建空看板和 `productions/state/tasks.db`。`--no-open` 关闭自动打开，`--port` 换端口；无需旧版任务服务目录。

`hyperframes_command` 是当前环境可用的命令数组，例如 `["hyperframes"]` 或 `["npx", "--no-install", "hyperframes"]`。预检不会下载或安装 CLI。TTS 健康接口不是 `/health` 时改 `health_path`；密钥通过配置指定的环境变量传入，不写进仓库。`unistudio.local.json` 已被 Git 忽略。

## 直接对 AI 说

让 AI 先读根目录 `AGENTS.md`（兼容入口另有 `CLAUDE.md`），再给出需求：

> 读这个项目的 AGENTS.md。用“无旁白图片快报”模板，把这段资讯和四张图片做成竖屏视频，完成后更新任务看板。

> 用“沃资讯”模板，根据这段新闻制作一期视频。配音使用本机配置的 TTS 模型和声线，成片登记为待发布。

> 把任务看板中待发布的视频发布到视频号，使用配置里的账号，发布后更新看板。

> 检查看板里平台审核中的视频，回读视频号状态并更新，别重复提交。

**网页负责浏览、预览和查看任务状态；AI 在当前会话执行制作与发布。** 网页不会自行启动 AI。需要全天无人值守时，在自己的 AI 运行器中另行配置定时调度和授权；仓库本身不启动定时任务。

## 视频模板

| 模板 ID | 内容 | 画幅 |
| --- | --- | --- |
| `ai-news-image-switch-brief-vertical` | 单条资讯图片快切，无旁白 | 9:16 |
| `woshi-news-vertical` | 沃资讯日期版，配音与四图轮播 | 9:16 |
| `tech-product-promo-vertical` | 科技产品宣传，六页固定结构、无旁白 | 9:16 |
| `ai-news-single-story-digital-presenter-vertical` | 单条资讯数字人深度解读 | 9:16 |
| `gangge-ai-international-vision` | 刚哥聊 AI，地球视觉与字幕 | 9:16 |
| `ai-weekly-news-roundup-landscape` | 多条 AI 周报 | 16:9 |
| `idea-explainer-landscape` | 长篇观点解说 | 16:9 |
| `guangying-dangshi-motion-lesson-landscape` | 光影党史长篇党课，SVG 代码动画 | 16:9 |

机器目录为 `templates/catalog.json`，可运行 `python3 scripts/unistudio.py templates` 查看路径和依赖提示。模板只读；新视频复制到 `productions/projects/<工程>/` 制作，成片与封面放 `deliver/`。

## 任务与发布

```text
制作中 producing → 待发布 ready → 发布中 publishing
                                  ├─ 草稿 draft_saved
                                  ├─ 已排期 scheduled
                                  ├─ 平台审核中 platform_pending
                                  └─ 失败 failed / 需人工介入 needs_human
```

任务看板只显示“待发布”和“已发布”两种状态；`platform_pending` 与 `published` 都归入“已发布”分组。平台审核状态仍原样保存在任务记录中，供回查真实发布结果。

AI 用 `new` 创建工程和任务，渲染检查后用 `ready` 登记成片；发布用 `claim` 原子领取，回读平台后用 `complete` 回写。领取凭证、防重复内容检查和平台会话互斥用于避免并发重复提交。中断或结果不明须先核验，不能自动退回待发布重发。

目前仅提供 [视频号发布 Skill](skills/publish-wechat-channels/SKILL.md)。其他平台只有添加实际 Skill 并登记到 `skills/publishers.json` 后才能使用。发布规则读取用户本机账号配置，不固定合集或强制声明原创。

完整命令、TTS 接法与恢复流程见 [AI 操作流程](docs/AI-WORKFLOW.md)，扩展平台见 [发布技能契约](docs/PUBLISHER-CONTRACT.md)。已有旧看板可按操作流程显式导入，旧数据不会自动改写。

仓库版本号、变更记录与发版步骤见 [发版规范](docs/RELEASE.md) 和 [更新日志](CHANGELOG.md)。

## 目录

```text
AGENTS.md                    # AI 执行入口
config/unistudio.example.json # 本机配置示例
scripts/unistudio.py          # 环境检查、工程、配音、任务与发布状态 CLI
task_service/                # 当前任务服务源码（Python 标准库）
web/                         # 工作台页面与单入口服务
templates/catalog.json       # 视频模板目录
skills/publishers.json       # 实际可用的发布技能目录
productions/                 # 被忽略的本机产物：projects/、state/tasks.db
```

验证：`python3 -m unittest discover -s tests -v`。新增模板见 [模板标准](TEMPLATE-STANDARD.md)。若资源是 Git LFS 指针，先执行 `git lfs pull`。模板源码、字体、图片、声音、品牌及人物素材的授权分别见各模板 `LICENSE` / `SOURCES.md`，根目录 MIT 不覆盖第三方媒体资产。

## License

[MIT](LICENSE) · Copyright (c) 2026 zj-unicom-ai contributors
