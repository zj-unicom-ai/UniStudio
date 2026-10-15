# AI 操作流程

以下命令均从当前仓库根目录执行，参数中的 ID 使用 CLI 实际返回值，工程名自行取不重复的名称。命令输出 JSON；环境或业务检查失败时退出码为 1。网页服务可与 CLI 独立启停，CLI 完成后数据仍会保留。

## 1. 环境与模板

```sh
python3 scripts/unistudio.py templates
python3 scripts/unistudio.py publishers
python3 scripts/unistudio.py doctor --template ai-news-image-switch-brief-vertical
```

若缺配置，复制 `config/unistudio.example.json` 为 `unistudio.local.json` 后按现有服务填写；不覆盖已有配置。`doctor` 不安装、不启停服务、不生成探测语音。它检查 Python/Node/npm/FFmpeg、已有 HyperFrames 命令、TTS 健康接口和选中模板的 LFS 指针。浏览器渲染能力、模板固定版本及具体 TTS 模型/声线仍须在实际构建、检查、预览和配音时验证。

`hyperframes_command` 用于环境预检；模板执行命令与版本使用各自 package.json。若远程 HyperFrames 只有 HTTP 服务而当前环境没有可运行的模板渲染命令，应先接入能执行模板的运行器，不能仅凭远程健康检查就声称可渲染。

## 2. 创建工程

```sh
python3 scripts/unistudio.py new \
  --template ai-news-image-switch-brief-vertical \
  --name 20261015-demo \
  --brief '把用户提供的资讯及四张图片制作成无旁白竖屏快报'
```

`new` 强制运行选中模板的环境检查，通过后才复制工程和登记任务。可选 `--platform wechat-channels` 提前指定目标平台；未指定时在发布阶段选择。返回 `id`、`project_dir` 和 `producing` 状态。保存 task ID，后续始终更新同一记录。

复制略过输出、缓存、node_modules、.env、Git 与模板 preview；其余模板文件整体保留。读取新工程中的模板说明，修改本期数据、文案、来源和素材。`UNISTUDIO-BRIEF.md` 记录本次需求，模板旧 BRIEF 只作为版式参考。刚哥模板复制 `assets/template-project`，其使用说明还要阅读外层模板 README / USAGE / SKILL。

## 3. 配音、构建与渲染

优先复用用户已配置的 TTS。统一适配器支持 OpenAI-compatible speech + PCM WAV：

```sh
python3 scripts/unistudio.py tts \
  --text-file productions/projects/20261015-demo/content/narration.txt \
  --output productions/projects/20261015-demo/assets/audio/voiceover.wav
```

此命令是实际合成，会使用配置的服务。返回音频实测时长、采样率和声道数；不会推断模板段落或自动调整时间线。分段模板逐段合成，将 WAV 放到模板要求的路径，再运行对应 manifest/timing 脚本。需要特定采样格式时用 FFmpeg 转换。非兼容服务按模板已有适配器调用，参数使用当前用户配置，不改成作者旧的私有 ID。

| 模板 | 关键音频衔接 |
| --- | --- |
| 图片快报 | 不生成旁白，保留 BGM |
| 科技产品 Promo | 不生成旁白，保留 BGM；替换示例品牌、参数与日期，并从成片截取完整封面 |
| 沃资讯 | 新配音放 `assets/audio/voiceover-female-news-fast.wav`，运行 `scripts/build-envelope.py` 后 build |
| 数字人资讯 | `assets/voice/<段落ID>.wav`，更新 voice-manifest 与 timing；新开场白须重新生成口型 |
| 刚哥国际视野 | 按 voice-requests 分段写 `assets/voice-guobiao/`，更新 manifest/voice-mode，再 compose |
| AI 周见 | WAV 按 composition ID 放 `assets/audio/`，运行 `scripts/make_voice_manifest.py` |
| 一念三千 | 分段写 `assets/audio/<段落ID>.wav`，更新 voice-manifest 和 timing，保持文案与段落对应 |
| 光影党史 | 分章 WAV 写入 `output/voice-m5/S01….wav`，运行 `scripts/assemble_m5_audio.py` 合并并生成配乐，再按 ASR 时码运行 `scripts/build_m5_timeline.py` 重排镜头与字幕 |

构建、检查、预览和渲染命令按该模板 README/USAGE 执行。必须检查真实画面与音频；`ffprobe` 和文件存在不代表内容正确。渲染后把最终 MP4 和完整封面放在工程 `deliver/` 下，保留工程中的 SOURCES 和制作记录。

## 4. 登记到任务看板

```sh
python3 scripts/unistudio.py ready \
  --id task-实际ID \
  --video productions/projects/20261015-demo/deliver/video.mp4 \
  --cover productions/projects/20261015-demo/deliver/cover.png \
  --title '本期短标题' --description '定稿发布描述' \
  --topics AI 科技 \
  --review-note '构建和检查通过；已预览开场、转场和片尾，封面完整，音轨正常'
```

该命令核验文件归属、非空、视频流、时长和音轨，记录成片与封面 SHA-256，并将任务更新为 `ready`。检查说明必须反映真正做过的检查。重复执行更新同一任务，不新增记录；已领取或已提交任务不能覆盖。音轨存在不会自动证明配音不是静音占位，AI 仍需试听。

```sh
python3 scripts/unistudio.py list --status ready
python3 scripts/unistudio.py show --id task-实际ID
python3 scripts/unistudio.py production-failed --id task-实际ID --note '配音服务失败，尚未完成渲染'
```

网页 `http://127.0.0.1:8610/#/tasks` 的任务看板只展示“待发布”和“已发布”两种状态，并允许手动切换。`ready` 显示为待发布；`published` 和 `platform_pending` 均显示为已发布。原始平台状态仍保存在任务记录中，网页分组不会伪造平台已通过审核。网页每 15 秒同步数据。

## 5. 按平台发布并回写

1. 用户明确要求发布后，查 ready 列表，根据用户给定日期、任务或范围筛选。制作请求本身不授权外发。
2. 用 `publishers` 查平台注册，再读其实际 SKILL.md。不存在对应 Skill 时停止该平台的发布，不套用别的平台选择器。
3. 检查本机配置的账号、可选合集和原创设置，整理视频、封面、定稿字段和排期。缺失项先补齐；不要抢先领取然后无限等待。
4. 领取单条，保存本次令牌；同平台会话逐条执行。领取还会核对文件是否变化、是否已经向相同平台账号提交过同一成片。

```sh
python3 scripts/unistudio.py claim --id task-实际ID --platform wechat-channels
```

5. 按 Skill 操作真实平台并核对登录账号。当前授权已覆盖提交且字段齐全时直接执行；不为重复确认而停下。发布本身不由 claim 命令执行。
6. 将本条平台回读文本或截图存入 `productions/projects/<工程>/publish/`，再回写：

```sh
python3 scripts/unistudio.py complete \
  --id task-实际ID --token 本次返回的claim_token \
  --status platform_pending --note '管理列表本条显示审核中，标题和封面一致' \
  --evidence productions/projects/20261015-demo/publish/verification.txt
```

`--status` 支持 `draft_saved` / `scheduled` / `platform_pending` / `published` / `failed` / `needs_human`；可用 `--post-url` 保存作品链接。scheduled 的 note 记录完整时区时间。真实证据由 AI 读取平台后保存，不能为了让命令通过而编造。审核中的任务在任务看板归入“已发布”展示分组，但记录状态仍为 `platform_pending`。

## 6. 中断与审核回查

正常审核回查可以保留原令牌执行 complete；令牌遗失、进程中断或旧数据导入后，先读取当前平台列表，再用显式恢复命令：

```sh
python3 scripts/unistudio.py reconcile --id task-实际ID \
  --status published --note '回查本条，审核通过且已公开；标题与封面一致' \
  --evidence productions/projects/20261015-demo/publish/recheck.txt
```

只有平台已证实从未提交，或明确失败且无作品/排期/草稿残留时，才可以 `reconcile --status ready`，并附此结论的证据。结果不明保留 `needs_human`。服务没有超时自动重试，防止已提交作品被重复发布。恢复会使旧令牌失效。

## 7. 旧看板迁移与本地服务

当前任务服务源码位于 `task_service/`，运行数据库位于 `productions/state/tasks.db`。历史版本把旧服务和运行数据放在被忽略的 `productions/pipeline/`；当前服务不依赖或自动修改该目录。如果存在旧 JSON 镜像，可显式导入：

```sh
python3 scripts/unistudio.py import-legacy --source productions/pipeline/publish-queue.json
```

按 ID 幂等导入，不覆盖新库已有记录；原始数据不变，越界媒体路径不公开，进行中的旧会话转为需人工核验。旧库若比镜像新，先用旧工具导出最新镜像再导入。不要把运行数据提交到 Git。

`python3 web/serve.py` 默认直接读取新库；迁移期间如需浏览旧服务媒体，可用 `--legacy-upstream 127.0.0.1:8898` 代理旧服务（旧参数 `--pipeline` 仍作为兼容别名）。该模式网页显示旧上游，CLI 写新库；除迁移期间只读查看外不要混用，以免看板与操作数据源不同。

API 只读：`GET /api/health`、`/api/templates`、`/api/publishers`、`/api/records`、`/api/stats`。领取令牌和本机配置不对网页暴露。`/projects/<工程>/deliver/<文件>` 支持视频 Range。所有写入走 CLI，不对网页暴露执行模型或发布外部内容的接口。
