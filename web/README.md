# UniStudio 本地工作台

从仓库根目录启动 `python3 web/serve.py`，访问 http://127.0.0.1:8610/。单服务包含主页、模板库、任务看板、发布说明与数字员工介绍，任务 API 默认读取仓库内 `task_service/` 的源码，运行数据自动创建在 `productions/state/tasks.db`。

- `--no-open` 不自动打开浏览器；`--port 9000` 换端口。
- `GET /api/records` 与 `/api/stats` 提供真实任务数据，页面每 15 秒同步；空库显示空状态，服务异常显示读取失败。
- `/projects/<工程>/deliver/<文件>` 提供交付媒体，支持 Range / 206 拖动播放。
- 写入统一使用 `python3 scripts/unistudio.py`。任务看板仅显示“待发布”和“已发布”两种状态：`ready` 显示为待发布，`published` 与 `platform_pending` 显示为已发布；审核状态仍保存在原始任务记录中。`publishing` 是发布流程状态，`producing` 是制作流程状态。

迁移期间可选 `--legacy-upstream 127.0.0.1:8898` 代理旧任务上游（`--pipeline` 仍是兼容别名），仅建议只读查看；该模式与新 CLI 的数据库不同，不混用。完整配置和迁移步骤见根目录 README.md 与 docs/AI-WORKFLOW.md。

服务只监听 127.0.0.1，仅提供页面、模板与交付媒体；不公开仓库根、数据库、本机配置或领取令牌。模板展示项在 web/index.html 的 TEMPLATES，制作目录在 templates/catalog.json，新增时保持 ID 一致。
