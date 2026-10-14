# 视频号发布工作流（可复制命令 + 踩坑）

所有命令在能跑 `agent-browser`（`/opt/homebrew/bin/agent-browser`）与 `curl` 的机器上执行。端口示例 `9333`。

## 栏目 → 合集 / 原创（每条必挂，判据见 SKILL「发布前必做」）

| 来源 | 合集 | 原创 |
|---|---|---|
| 《刚哥聊 AI》（`视频创作/刚哥聊AI/<日期>/renders/*.mp4`） | 刚哥聊AI（账号已存在） | 声明 |
| 快播资讯（`ai-news-*` 模板：快播版 `ai-news-holographic-image-vertical`、`ai-news-holographic-image-bgm-vertical`、`ai-news-single-story-presenter-vertical`、`ai-news-digital-presenter`、`ai-news-editorial-landscape`） | 科技前沿（账号暂无，首次用时按 5.6 创建） | 声明 |
| 其他（品牌片、活动片等） | 不自动挂，`needs_human` 问用户 | 问用户 |

## 0. 为什么不能用 browser-use MCP

实测：browser-use（Qoder 受管 Chromium）打 `channels.weixin.qq.com` 登录时——
- 快捷登录：页面往 `https://localhost.weixin.qq.com:14013/api/authorize` 发授权请求，一直 `[pending]` 不返回；控制台有 `Unrecognized feature: 'local-network-access'`。
- 手机扫码：二维码能渲染，但微信埋点上报 `connect_qrconnect_checkLogin_fail`。
根因：该实例缺本地网络访问权限 + 带自动化特征，被微信判负。**改用真实 Chrome 经 CDP 接管**（agent-browser `connect` 不注入 `navigator.webdriver`，且真实 Chrome 信任本机微信客户端）。

## 1. 起调试实例并接管

```bash
bash scripts/launch_wechat_chrome.sh "https://channels.weixin.qq.com/platform/post/create" 9333
agent-browser connect 9333
agent-browser get url    # 期望停在 .../platform/post/create（未登录会弹回 login.html）
```

主 Chrome 若已在 `127.0.0.1:9222` 监听但 `/json/version` 返回空，那是默认配置被禁用的僵尸端点，别用；本脚本用独立 user-data-dir + 干净端口。

## 2. 登录（真实 Chrome 下正常）

未登录时页面显示"登录视频号助手 / 微信快捷登录"。让用户在该窗口点"微信快捷登录"并在桌面微信确认，或点"使用其他头像、昵称或账号"出二维码用手机扫。登录后：

```bash
agent-browser get url    # 应停在 /platform/post/create
agent-browser screenshot /tmp/wx-login.png   # 左下角出现账号头像
```

## 3. 账号核对

视频号对外名常在上传预览浮层或头像菜单里。发布前把账号名报给用户逐字确认，不以头像/历史推断。

## 4. 上传（控件在同域 wujie 子 iframe）

```bash
# 确认文件控件位置（主文档没有，在 iframe.contentDocument 里）
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;return !!d.querySelector('input[type=file]')})()"
agent-browser frame "iframe"
agent-browser upload "input[type=file]" "/绝对路径/xxx.mp4"
agent-browser frame main
agent-browser screenshot /tmp/wx-upload.png   # 出现视频预览+封面预览，无“上传中/处理中/失败”
```

## 5. 填字段

短标题（**≤16 字**，中英都按字符计；超了报"标题超过16字限制"）：

```bash
agent-browser frame "iframe"
agent-browser fill 'input[placeholder*="短标题"]' "OpenAI决策API开放公测"
```

描述是 contenteditable `div.input-editor`。**Playwright click 会被 wujie 宿主遮挡**（报 "covered by <wujie-app…>"），且失焦后 `keyboard type` 会漏进短标题。用 eval 聚焦 + `execCommand('insertText')`：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const e=d.querySelector('.input-editor');e.focus();d.execCommand('insertText',false,'<描述正文>');return 'len='+e.textContent.trim().length})()"
# 追加话题（文字形式；要成真话题用 #话题 按钮逐个选）
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const e=d.querySelector('.input-editor');e.focus();const r=d.createRange();r.selectNodeContents(e);r.collapse(false);const s=d.getSelection();s.removeAllRanges();s.addRange(r);d.execCommand('insertText',false,' #话题1 #话题2');return e.textContent.trim().length})()"
```

清空重填短标题（React 受控 input，需原生 setter + input 事件）：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const el=[...d.querySelectorAll('input')].find(x=>/短标题/.test(x.placeholder));const set=Object.getOwnPropertyDescriptor(d.defaultView.HTMLInputElement.prototype,'value').set;set.call(el,'');el.dispatchEvent(new Event('input',{bubbles:true}));return 'cleared'})()"
```

## 5.5 上传完整封面（别用默认首帧）

视频号默认取视频首帧当封面；模板封面首帧是"干净暗场"（人和版式随后淡入），直接用会几乎全黑、只露一部分。渲染后从成片取一帧完整封面：

```bash
ffmpeg -y -ss 6 -i deliver/<成片>.mp4 -frames:v 1 deliver/cover.png   # 标题+主句+关键词+人物都在
```

发布页走"封面预览 → 编辑 → 上传封面"，用这张覆盖默认帧。上传封面也是同域 iframe 里的 `input[type=file]`（accept 常含 image/*），`frame "iframe"` 后 `agent-browser upload` 传 `cover.png` 绝对路径，再回读封面缩略图确认已是完整画面。

## 5.6 选合集（2026-10-09 实测 DOM）

合集控件在"添加到合集"这一 `.form-item` 里，全部位于同域 wujie iframe 的 contentDocument。未选时显示 `.display-text`「选择合集」；下拉 `.post-album-wrap .filter-wrap` 平时 `display:none`，但**选项已经在 DOM 里**，可以先只读列出账号现有合集：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const w=d.querySelector('.post-album-wrap');return JSON.stringify(w?[...w.querySelectorAll('.option-item .name')].map(e=>e.textContent):'nf')})()"
# 实测账号现有：AI前沿、刚哥聊AI、AI创作、智能体、MCP
```

挂载：先点开 `.post-album-display` 展开下拉，再对目标 `.option-item` 里的 `.item` 依序派发 `pointerdown/mousedown/pointerup/mouseup/click`（Vue 组件，普通 `.click()` 也生效，但和封面弹窗一样，事件序列更稳）：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;d.querySelector('.post-album-display').click();return 'opened'})()"; sleep 1
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const o=[...d.querySelectorAll('.post-album-wrap .option-item')].find(e=>e.textContent.includes('刚哥聊AI'));const t=o.querySelector('.item');['pointerdown','mousedown','pointerup','mouseup','click'].forEach(n=>t.dispatchEvent(new (n.startsWith('pointer')?PointerEvent:MouseEvent)(n,{bubbles:true,cancelable:true,view:d.defaultView})));return 'picked'})()"
```

回读：选中后 `.display-text` 会变成 `.collection-text`，里面 span 就是合集名（旁边有 `.clear-icon` 可清除）。**核验只认这行的文本**：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const c=d.querySelector('.post-album-wrap .collection-text');return c?c.textContent.trim():'未选中'})()"
```

合集不存在时（例如快播资讯要用的「科技前沿」）点 `.post-album-wrap .create a`「创建新合集」，对话框里只有一个标题 input（占位"有趣的合集标题更容易吸引粉丝"，**计数上限 10 字，创建后标题不可修改**）。填值要用原生 setter + `input` 事件，只 `set value` 不发事件时【创建】按钮一直 `weui-desktop-btn_disabled`：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const w=[...d.querySelectorAll('.weui-desktop-dialog__wrp')].find(x=>getComputedStyle(x).display!=='none'&&/创建合集/.test(x.innerText));const i=w.querySelector('input');i.focus();const set=Object.getOwnPropertyDescriptor(d.defaultView.HTMLInputElement.prototype,'value').set;set.call(i,'科技前沿');i.dispatchEvent(new Event('input',{bubbles:true}));const b=[...w.querySelectorAll('button')].find(x=>x.textContent.trim()==='创建');return JSON.stringify({cnt:w.innerText.match(/\\d+\\/\\d+/)?.[0],dis:b.disabled})})()"
# 确认 dis=false 且标题逐字无误，才对【创建】派发事件序列点击；取消用同排【取消】
```

挂错要改：对 `.collection-text .clear-icon` 派发事件序列清除，再重开下拉选正确的。

## 5.7 声明原创（固定动作，2026-10-09 实测）

"声明原创"是 `.form-item` 里的 ant checkbox（`.declare-original-checkbox input[type=checkbox]`），本工作区每条都勾。勾上会弹「原创权益」对话框，里面还有一个"我已阅读并同意《原创声明须知》和《使用条款》"的同意 checkbox——**不勾同意，对话框主按钮【声明原创】一直是 `weui-desktop-btn_disabled`**（`disabled` 属性为 false，禁用态写在 class 上，别只读 `.disabled`）：

```bash
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;d.querySelector('.declare-original-checkbox input[type=checkbox]').click();return 'box'})()"
sleep 1
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const w=[...d.querySelectorAll('.weui-desktop-dialog__wrp')].find(x=>getComputedStyle(x).display!=='none'&&/原创权益/.test(x.innerText));w.querySelector('input[type=checkbox]').click();const b=[...w.querySelectorAll('button')].find(x=>x.textContent.trim()==='声明原创');return JSON.stringify({dis:b.disabled,cls:b.className})})()"
# cls 里没有 _disabled 后，用事件序列点【声明原创】
agent-browser eval "(()=>{const d=document.querySelector('iframe').contentDocument;const w=[...d.querySelectorAll('.weui-desktop-dialog__wrp')].find(x=>getComputedStyle(x).display!=='none'&&/原创权益/.test(x.innerText));const b=[...w.querySelectorAll('button')].find(x=>x.textContent.trim()==='声明原创');['pointerdown','mousedown','pointerup','mouseup','click'].forEach(n=>b.dispatchEvent(new (n.startsWith('pointer')?PointerEvent:MouseEvent)(n,{bubbles:true,cancelable:true,view:d.defaultView})));return 'confirmed'})()"
```

回读：`.declare-original-checkbox .ant-checkbox` 的 class 含 `ant-checkbox-checked`、`input.checked===true`。已加入创作分成计划的账号可能先弹另一个对话框（标题"声明原创的视频有机会获得广告分成"，主按钮同样叫【声明原创】且默认可点）——按可见对话框的标题分支，别把两个模板混着选。未上传视频时这两步也能完成，不必等上传后再声明。

## 6. 提交前确认 + 发表

先把完整字段表（账号/短标题/描述/话题/封面/**合集**/**原创**/位置/定时）交用户确认，得到明确"发"。发表按钮文本恰为"发表"（另有"保存草稿""直接发表"，勿点错）：

```bash
agent-browser frame "iframe"
agent-browser eval "(()=>{const d=document.querySelector('iframe')?.contentDocument||document;const b=[...d.querySelectorAll('button,.weui-desktop-btn')].find(x=>x.textContent.trim()==='发表');if(!b)return 'nf';b.click();return 'clicked'})()"
# 成功后 URL 跳到 /platform/post/list
```

若 eval `.click()` 不触发（个别情况需可信事件），用 `agent-browser click` 在 frame 上下文按选择器点，或 `agent-browser find role button "发表" click`。

## 7. 回读核验（防重发的唯一证据）

```bash
agent-browser open "https://channels.weixin.qq.com/platform/post/list"; sleep 4
agent-browser eval "(()=>{const d=document.querySelector('iframe')?.contentDocument||document;const t=d.body.innerText.replace(/\s+/g,' ');return JSON.stringify({found:t.includes('<描述前缀>'), pending:/审核中|转码中|原创审核中|发布中/.test(t)})})()"
agent-browser screenshot /tmp/wx-list.png
```

- 条目在列表顶部、封面与描述完整、无待处理徽标、带浏览/点赞计数 → `published`。
- 出现"审核中/转码中/原创审核中" → `platform_pending`。
- **原创**：列表条目文案里会出现"已声明原创"字样（2026-10-09 实测：早先没声明的条目没这行）。整页文本 `/已声明原创/` 只能证明"页面上有原创条目"，要定位本条得先按描述前缀切出该卡片再查子串。
- **合集**："视频"列表不显示所属合集。核法：列表页顶部有"视频 (14) / 合集 (5)"两个标签，对"合集 (n)"标签派发事件序列切过去，读目标合集那行的"内容数"是否比发布前 +1（发布前先记一次基线）。
- 逐字比对描述与短标题是否与预期一致（描述易被截断或被误填进短标题）。
- 结果不明：只重载列表查指纹，**绝不重复点发表**。
- 已发布条目在列表里只提供"修改描述和封面"、"可见权限"、"删除"等入口，未提供改合集/改原创的入口——所以合集与原创必须在发表前落到 DOM 上并回读确认，漏了只能删重发或人工处理。

## 8. 收尾

```bash
# 关掉本次调试实例（按 launch 脚本打印的 PID），保留用户日常 Chrome
pkill -f "user-data-dir=$HOME/.chrome-wxpublish" || true
```

## 已知踩坑补充（2026-10-09 实测）

- **调试 Chrome 实例跑久了会"半坏"**：`agent-browser frame "iframe"` 看似切换成功，但 eval 落在主文档、`upload input[type=file]` 只触发 `beforeUpload` 日志而上传流程静默卡死（无任何网络请求、连昨天能成功的旧文件也一样）。判别法：注入后 `network requests` 里找不到上传相关 POST。处理：**kill 调试实例重新启动**，同一 profile 登录态保留，重启后正规 `frame "iframe"`+`upload` 一次成功。别在坏实例上反复换招（DataTransfer 注入、drop 模拟都只会同样卡住）。
- **封面编辑弹窗的【确认】按钮**：普通 `.click()` 不生效，需在 iframe contentDocument 里对按钮依序派发 `pointerdown/mousedown/pointerup/mouseup/click` MouseEvent 才关闭弹窗。【保存草稿】同理用事件序列点击，成功以重载草稿箱为准。
- **草稿短标题核验**：草稿箱列表只显示描述不显示短标题，且列表项被 `wujie-app` 遮挡无法点进编辑。用页面上下文 fetch 直接读接口：iframe 的 `contentWindow.fetch('/micro/content/cgi-bin/mmfinderassistant-bin/post/get_draft_list?_aid=…&_rid=…',{method:'POST',credentials:'include',headers:{'content-type':'application/json'},body:JSON.stringify({username:'',random_string:'x'})})`，在返回 JSON 里 grep `"shortTitle"` 逐字比对。

## 已知踩坑补充（2026-10-11 实测，补发布昨天的成片时踩到）

- **命令格式：`connect` 只接端口，子命令必须单独调用**。`agent-browser connect 9333 eval "..."`、`agent-browser connect 9333 upload-file ...` 这类把子命令拼在 connect 后面的写法**不会执行任何页面操作，却返回"✓ Done"**，极易误判为成功并反复空转。正确：先 `agent-browser connect 9333`（一次），之后每条独立跑 `agent-browser get url` / `frame "iframe"` / `upload "input[type=file]" <绝对路径>` / `eval "..."` / `screenshot /tmp/x.png`。上传是 `agent-browser upload "<css>" "<绝对路径>"`（不是 upload-file，也不是 --file）。填字段前先 `agent-browser get url` 确认停在 `/platform/post/create`（在 login.html 说明没登录，让用户在窗口扫码）。
- **原创权益弹窗的同意框：先置 `checked=true` 再 dispatch `change`，然后等约 1 秒**让 React 重渲染，【声明原创】按钮才会去掉 `weui-desktop-btn_disabled`；只 dispatch click 或不等待，按钮一直 disabled。真实 `agent-browser click` 点这个框会被 `wujie-app` 遮挡报 covered，但遮挡报错后状态往往已经落上，回读 `checked`/按钮 class 为准。
- **封面"裁剪不成功"是假失败**：`upload 'input[type=file][accept*="image"]' <cover.png>` 后顶部弹"裁剪不成功"toast、【确认】点不动，但封面预览实际已换成上传的完整帧。若确认关不掉弹窗，直接对【确认】再派发一次事件序列即可关闭，回看 `封面预览` 缩略图确认已是完整画面即可，不必纠结 toast。
- **状态判读**：发表后 URL 跳 `/platform/post/list`、条目在列表顶部且带"原创审核中/审核中/转码中"徽标 → 记 `platform_pending`（审核通过才公开），**不是 `published`**；`published` 要求无待处理徽标且带浏览/点赞计数。核验用 `eval` 读 `iframe.contentDocument.body.innerText`，别用 browser-use 的 snapshot（它看到的是受管 Chromium 的 login.html，跟 agent-browser 接管的真实 Chrome 不是同一个实例）。
- **发布 cron 与手工共用 9333**：本工作区有每 20 分钟的自动发布任务也连 9333 这个 `~/.chrome-wxpublish` 实例。手工补发前先看看板该条是否已是 `publishing`/`platform_pending`（可能 cron 已在跑），避免重复上传；收尾**不要 pkill 9333 共享实例**。

## 与创作侧衔接

成片来自 `projects/<模板>/<日期>-<主题>/deliver/*.mp4`（由 video-template-producer 产出；新工程在 `projects/<模板名>/<YYYYMMDD>-<主题>/deliver/`，旧工程在 `projects/<video-name>/deliver/`）。竖版 1080×1920 是视频号原生画幅。发布不改动模板库与作品工程；只读源视频。

## 已知踩坑补充（2026-10-12 实测，发布《国际视野》第 2 期时踩到）

- **`agent-browser frame "iframe"` 在这个页面根本不切换上下文**：命令回 `✓ Done`，但随后 `eval` 仍落在主文档（`document.body.innerText` 只有"视频号 · 助手"10 个字符），`upload "input[type=file]"` 直接 `Element not found`。**别信 frame 切换，改用"把隐藏控件显形 + 用 ref 上传"**：

  ```bash
  # 1) 在 iframe.contentDocument 里把目标 input 显形（视频框是 [0]，封面框是切到「上传封面」页签后的 [1]）
  agent-browser eval '(function(){const d=document.querySelector("iframe").contentDocument;const i=[...d.querySelectorAll("input[type=file]")][0];i.style.cssText="display:block!important;opacity:1;position:fixed;left:0;top:0;width:220px;height:60px;z-index:2147483647";return "shown"})()'
  # 2) snapshot 里会出现 `button "选择文件" [ref=eNN]`，用它上传
  agent-browser snapshot | grep -n "选择文件"
  agent-browser upload "@eNN" "/绝对路径/xxx.mp4"
  # 3) 上传成功后把 style 清回去，避免页面上留一个大方块
  ```
  判别上传是否真成功：iframe 文本从"上传时长8小时内…"变成"取消上传 | 封面预览 | 编辑"，再变成带账号名（万智创界）与 转发/赞/评论/删除 的预览卡。

- **不要用"本地 http.server + 页面内 fetch + DataTransfer"绕上传**：`fetch("http://127.0.0.1:PORT/x.mp4")` 在 `channels.weixin.qq.com` 里直接 `ERR Failed to fetch`（Chrome 的本地网络访问限制，页面没有 meta CSP 也照样拦）。走上面的 ref 方案。顺带：`8899` 端口被本工作区看板 `pipeline/serve.py` 占着，临时起服务会静默失败并拿到看板的 404 页，换端口前先看 `lsof`。

- **合集"内容数"会滞后约 1 分钟**：点完发表立刻切「合集 (6)」标签，`刚哥聊AI` 仍是发布前的 12；等 45–60 秒重载才变 13。核合集要按"发布前基线 → 稍后复查"两步走，别因为第一次读到 12 就判定漏挂（发表页下拉里的"共 N 个内容"就是最方便的基线）。

- **发表后头几分钟「原创审核中」一定在**（本次 07:48 发表，07:56 仍在）：状态记 `platform_pending`，即使条目已在"视频 (33)"顶部、浏览量已经开始 +1、合集计数已 +1。别因此重复发表。
