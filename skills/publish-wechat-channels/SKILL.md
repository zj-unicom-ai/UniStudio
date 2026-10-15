---
name: publish-wechat-channels
description: 使用真实 Chrome 和 agent-browser 将 UniStudio 待发布成片发布到微信视频号，支持草稿、定时、发布及状态核验，并把平台实际结果回写任务看板。不制作或渲染视频。
---

# 发布到微信视频号

从仓库根目录执行下文命令。先阅读根目录 `AGENTS.md` 和 `docs/AI-WORKFLOW.md` 的发布部分；本技能负责平台操作，任务领取与回写统一使用 `scripts/unistudio.py`。

## 输入与授权

- 用户说“把看板里的待发布视频发布到视频号”即授权这次范围内的发布。目标账号、平台、任务范围和文案已经确定时，按授权执行，不再逐条索要相同确认。仅“制作视频”不包含发布授权。
- 目标账号、可选合集、是否声明原创来自 `unistudio.local.json` 的 `publishers.wechat-channels`。不得沿用样例中的作者账号、合集或声线；原创声明须与实际素材权利相符。
- 若账号未配置、未登录、当前登录账号不符或缺少必填信息，先准备完整字段，再向用户说明具体缺项。账号不能从头像或历史记录推断。
- 该 Skill 随仓库提供；实际发布依赖当前运行环境里的 `agent-browser`、真实 Chrome 和目标账号登录态。仓库不会自动提供账号或安装这些依赖。

## 从任务看板取数

1. `python3 scripts/unistudio.py list --status ready`，按用户指定范围筛选任务。已有 `scheduled`、`platform_pending`、`published` 或结果不明的任务不可重新发布。
2. 逐条执行 `python3 scripts/unistudio.py claim --id <任务ID> --platform wechat-channels`，保存本次返回的 `claim_token`。同一平台只允许一个 `publishing` 会话，先前会话未收口时停止领取。
3. `video`、`cover`、`project_dir` 是相对仓库根目录的路径；上传前转换成当前机器的绝对路径。只读这些文件，不改模板、不改 SQLite。
4. 核对视频规格、短标题（当前工作流按 16 字检查）、描述、话题、完整封面、可选合集、原创开关及时间。以平台实际限制和校验为准。短标题要改时，先在发布前把内容定稿并重新登记 `ready`，不要在已领取的记录里偷偷改文案。
5. 定时任务需给出带时区的时间。可运行 `python3 skills/publish-wechat-channels/scripts/schedule_publish.py --id <任务ID> --at '2026-10-16T18:00:00+08:00'` 做只读排期预检；该脚本只输出计划，不操作浏览器、不提交也不回写成功。

## 操作平台

具体 iframe、上传、描述编辑、合集、原创弹窗、日期选择和状态判读见 [浏览器工作流](references/wechat-channels-workflow.md)。其中合集名均为示例，以用户配置为准；页面结构变化时重新读取 DOM。

1. 启动专用 Chrome：`bash skills/publish-wechat-channels/scripts/launch_wechat_chrome.sh`，然后单独执行 `agent-browser connect 9333`。复用已启动实例时不关闭共享浏览器。登录通常需要用户在该窗口完成。
2. 打开创建页，读取并核对当前账号，然后在同域 iframe 中上传视频。等待上传和转码完成后填写字段。
3. 使用任务中的完整封面，不能以尚未完成入场动画的首帧代替。合集配置为空时不挂合集；指定合集不存在时只在用户授权创建该合集的情况下创建。原创开关为 false 时不声明原创。
4. 回读并核对标题、描述、话题、封面、可选合集、原创设置和时间。时间组件要真实点击选定日期与小时；只给 input 赋值不会落到组件状态，必须回读完整年月日和时分。
5. 在用户授权范围内执行 `publish` / `schedule` / `draft`。点击后结果不明时先查管理列表，禁止重复点提交。
6. 重载列表，用描述、时间和封面定位**本条**，保存平台原文或截图到工程的 `publish/` 目录。不得拿整页其他作品的状态证明本条成功。

## 回写与中断恢复

```sh
python3 scripts/unistudio.py complete --id <任务ID> --token <本次claim_token> \
  --status platform_pending --note '平台列表：审核中；标题与封面一致' \
  --evidence productions/projects/<工程>/publish/verification.txt
```

按证据填写：草稿已保存 → `draft_saved`；平台明确回显排期 → `scheduled`；审核/转码/发布处理中 → `platform_pending`；本条明确公开且无处理中徽标 → `published`。可附 `--post-url`。跳转成功、上传成功或按钮消失都不能单独证明已发布。

明确失败 → `failed`；登录/页面变化、会话中断、提交结果不明 → `needs_human`，附异常说明和已有证据。每个已领取会话都要收口；凭证遗失时使用 `reconcile`，先查平台再按证据恢复状态，只有证实未提交才能恢复为 `ready`。不因超时自动重发。
