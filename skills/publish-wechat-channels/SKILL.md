---
name: publish-wechat-channels
description: 把本地已渲染成片自动发布到微信视频号助手（发表/草稿/定时/状态回读）。当用户说"发视频号""把这条视频发到视频号""视频号定时发布""核验视频号发布状态"，或要求把 uni-ai-video-productions 产出的成片对外发布时使用。不用于公众号文章；不做视频渲染（那是 video-template-producer 的职责）。
---

# 发布视频到微信视频号

把作品 `deliver/` 里的成片发布到视频号助手 `https://channels.weixin.qq.com`（新工程在 `projects/<模板名>/<YYYYMMDD>-<主题>/deliver/`，旧平铺工程在 `projects/<video-name>/deliver/`；按 BRIEF 或用户指定确认是哪一个）。核心难点是登录与 wujie 微前端表单，必须用真实 Chrome 经 CDP 接管，不能用被微信判定为自动化的浏览器。详细操作与踩坑见 [视频号发布工作流](references/wechat-channels-workflow.md)。

## 铁律：用哪个浏览器

- **视频号发布是单线操作。** `scripts/schedule_publish.py` 启动时对 `pipeline/.publish-browser.lock` 加 `flock`，拿不到锁就打印 `SKIP 另一个发布正在进行…` 并以退出码 3 结束——手工发之前先跑 `python3 scripts/schedule_publish.py --lock-check`（FREE / BUSY）确认没人在发，别和定时任务 5191596d-087e-4973-93cf-84711d37fce4（每半小时）抢同一个 create 页。

- **禁止用 browser-use MCP 登录视频号。** 它是 Qoder 内置受管 Chromium，缺 `local-network-access` 权限且带自动化特征，微信快捷登录的 `authorize` 会一直 pending、扫码也报 `connect_qrconnect_checkLogin_fail`。
- **必须用 `agent-browser` 接管一个"真实 Chrome 调试实例"**：本机 Chrome 二进制 + 独立 `--user-data-dir` + `--remote-debugging-port`。真实 Chrome 才信任本机微信客户端、才不带 `navigator.webdriver`，快捷登录能秒回。
- Chrome 136+ 禁止在默认配置开调试端口；用独立 `--user-data-dir` 可与用户日常 Chrome 并存，无需退出主浏览器。

## 发布前必做

1. 只读预检成片，确认满足视频号硬限制（≤4 GiB、3 秒–2 小时、宽高比 1:3–3:1；建议 MP4/H.264、短边≥720、码率≤10 Mbps、≤60 fps、AAC≥128k/≥48 kHz）。有 `ffprobe` 即可自行核对，或复用 `lovstudio/publish-wechat-channels-skill` 的 `check_video.py`。
2. **生成完整封面帧**：视频号默认取视频首帧当封面，而模板封面首帧按设计是"干净暗场"（人和版式随后才淡入），直接用会出现"封面只露一部分/几乎全黑"。渲染后从成片封面段中部取一帧完整画面（标题+主句+关键词+人物都在，约 5–7 秒），存成 `deliver/cover.png`，发布时显式上传这张，别用默认首帧。
   ```bash
   ffmpeg -y -ss 6 -i deliver/<成片>.mp4 -frames:v 1 deliver/cover.png
   ```
3. 取得并确认输入：目标动作（`draft`/`schedule`/`publish`/`status`）、预期视频号名、本地视频绝对路径；`schedule` 需带时区时间。
4. 文案定稿：短标题（**视频号限 16 字**，中英文都按字符计）、描述、话题、封面（用第 2 步生成的完整帧）、**合集**（见第 5 步）、**原创声明（固定勾选）**、位置。未知事实不编造。
5. 定合集归属（按栏目/模板判，不看标题猜）：
   - 《刚哥聊 AI》栏目（`视频创作/刚哥聊AI/<日期>/` 工程产出的成片）→ 合集 **刚哥聊AI**
   - 快播资讯类模板（`ai-news-*`：`ai-news-holographic-image-vertical` 快播版、`ai-news-holographic-image-bgm-vertical`、`ai-news-single-story-presenter-vertical`、`ai-news-digital-presenter`、`ai-news-editorial-landscape`）→ 合集 **科技前沿**
   - 「科技前沿」在账号上可能尚未创建：发布页下拉里没有该项时，走「创建新合集」建好再选（合集标题上限 10 字，**创建后不可修改**，建前先与用户核对用词）。
   - 两类都对不上（如品牌片、活动片）→ 不自动挂合集，标 `needs_human` 问用户，别自己挑一个看起来顺眼的。
6. 原创声明：本工作区所有成片一律勾选「声明原创」，并在弹出的「原创权益」对话框里同意《原创声明须知》后点【声明原创】。这是固定动作，不属于逐条确认项；成片有搬运/素材混剪等不该声明原创的情况时，先停下问用户。

## 执行顺序（顺序不能乱）

> 定时发表（`schedule`）已用脚本跑通：`python3 scripts/schedule_publish.py <看板ID> "YYYY-MM-DD HH:00"`，支持 `--edit`（改已排期条目的时间）与 `--dry`（停在发表前）。它按下面的顺序做上传、填表、挂合集、声明原创、传封面、选定时并回读核验；首次批量前仍要人工核对一遍字段表。手动走时注意：**定时时间必须用真实鼠标点击选（日期 → 时间 → 时），给 input 赋值只会改显示、不会落到组件状态**，早于当前约 2 小时的时档是置灰的。

> **命令格式先记住**：`agent-browser connect <port>` 只接端口且只连一次，之后每条操作独立调用（`agent-browser get url` / `frame "iframe"` / `upload "<css>" "<绝对路径>"` / `eval "..."` / `screenshot`）。把子命令拼在 `connect` 后面（如 `connect 9333 eval ...`）会返回"✓ Done"却什么都不做，是最容易空转反复的坑。详见 [工作流](references/wechat-channels-workflow.md) 的"2026-10-11 实测"补充。

1. 起真实 Chrome 调试实例并连上：`bash scripts/launch_wechat_chrome.sh <视频创建页URL>`，再 `agent-browser connect <port>`。
2. 打开 `https://channels.weixin.qq.com/platform/post/create`。若弹回 `login.html`，让用户在该窗口用"微信快捷登录"或扫码登录（真实 Chrome 下正常）；登录后 URL 应停在 create 页、左下角出现账号头像。
3. 核对账号名（提交前逐字确认，不以头像/历史推断）。
4. 上传：文件控件在同域 wujie 子 iframe 里，先 `agent-browser frame "iframe"` 再 `agent-browser upload "input[type=file]" <绝对路径>`。等封面预览出现、无"上传中/处理中/失败"。
5. 填字段：短标题用 `fill`；**描述是 contenteditable，必须用 eval 聚焦后 `execCommand('insertText')` 写入**，绝不能用 `keyboard type`（点击被 wujie 宿主遮挡会失焦，键盘输入会漏进短标题触发"超16字"）。话题以文字追加或用 #话题 按钮。
6. 选合集：点开"添加到合集 → 选择合集"下拉（同域 iframe 内的 `.post-album-display`），用鼠标事件序列点目标 `.option-item`，回读 `.collection-text` 确认显示的就是本条该挂的合集名。下拉里没有该合集时先「创建新合集」（标题不可改，建前核对用词）；创建后重新展开下拉选中。
7. 声明原创：勾 `.declare-original-checkbox input`，在「原创权益」对话框里勾选同意《原创声明须知》，点【声明原创】；对话框的【创建】【声明原创】等按钮初始是 disabled，必须等输入/勾选事件真正落到组件上才变可点。
8. **上传完整封面**：走"封面预览 → 编辑 → 上传封面"，用第 2 步生成的 `cover.png` 覆盖默认首帧，回读封面缩略图确认已是完整画面。
9. 提交前把完整字段表（账号/短标题/描述/话题/封面/**合集**/**原创**/位置/定时）交用户确认，得到明确"发"。
10. 发表：用 eval 点 `textContent==='发表'` 的 `weui-desktop-btn`；页面会跳到 `/platform/post/list`。
11. 回读核验：重载列表，用"描述前缀 + 时间戳 + 封面"指纹定位本条，逐字比对描述与短标题，读状态原文；再核两件事——条目带"已声明原创"字样、切到"合集"标签后目标合集的"内容数"比发布前 +1（视频号"视频"列表本身不显示合集名，只能这么核）。

## 状态契约

只用这些值，保留最后已证实状态，错误另列：`prepared`→`uploading`→`processing`→`draft_saved`/`scheduled`/`platform_pending`/`published`/`publish_failed`。

- 视频号列表不给已发布作品打"已发布"字样；判据是：条目正常出现在"视频管理"列表顶部、封面与描述完整、**无"审核中/转码中/原创审核中/发布中"徽标**、带浏览/点赞计数（刚发为 0）→ `published`。
- 出现"审核中/转码中/原创审核中"等原文 → `platform_pending`，即使创建页提示成功也不算 `published`。
- 成功提示、按钮消失、URL 跳转都单独不证明 `published`；必须回列表重载核对。
- 合集与原创属于发布完整性：视频号"视频管理"列表已发布的条目只提供"修改描述和封面"，没看到改合集/改原创的入口，所以这两项必须在点发表前就落定并发不出漏项。发出后才发现漏了，如实写进 `verify_note` 并标 `needs_human` 交用户处理，别默默交付半套字段。

## 防重与收口

- 提交后结果不明时**先重载列表查指纹，绝不重复点发表**（会发重复内容）。
- 页面结构变化就重新 `frame`+`eval` 读 DOM，不复用旧选择器/坐标。
- 全程只读源视频；发布是外部不可逆写动作，无用户明确"发"不提交。
- 收尾：`kill` 调试 Chrome 实例（按 PID），保留用户日常 Chrome 不动。
