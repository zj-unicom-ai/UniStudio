# UniStudio · 创作工作室

一个属于创作者的 AI 视频工作空间：把 AI 视频模板、生成任务与发布流程收进同一个工作室。挑一套模板、看成片进度、跟进发布——重复环节交给工作室，人只管定方向、看片、点发布。

## 目录结构

```
UniStudio/
├── web/            # 平台单入口服务（页面 + 本地 HTTP 服务）
│   ├── index.html     # 自包含单页应用：主页 / 模板总览 / 任务看板 / 自动发布
│   └── serve.py        # 本地服务（/api/*、/projects/* 反向代理到 pipeline 上游）
├── templates/      # 视频模板源码（只读，5 套）
│   ├── ai-news-image-switch-brief-vertical/
│   ├── ai-news-single-story-digital-presenter-vertical/
│   ├── gangge-ai-international-vision/
│   ├── ai-weekly-news-roundup-landscape/
│   └── idea-explainer-landscape/
├── skills/        # 生产流程相关 Skill
│   └── publish-wechat-channels/   # 视频号自动发布
└── productions/    # 输出产物（已 gitignore，不入库）
    ├── pipeline/      # 任务服务代码 + platform.db 数据正本
    └── projects/      # 各工程成片（projects/<工程>/deliver/）
```

## 快速启动

需要两个服务：

```sh
# 1) 任务服务（数据上游，提供 /api/* 与成片静态文件）
cd productions/pipeline
python3 serve.py 8898

# 2) 平台服务（单入口，另开一个终端）
cd UniStudio
python3 web/serve.py --pipeline 127.0.0.1:8898
```

浏览器访问 **http://127.0.0.1:8610/**（默认自动打开；加 `--no-open` 关闭，`--port` 换端口）。

## 四个视图

1. **主页**：项目介绍 + 平台能力 + 工作流 + 真实统计（模板数 / 已发布成片 / 审核中 / 接入平台）。
2. **模板总览**：模板卡片栅格，按画幅 / 类型筛选、关键词搜索、对比表、样片灯箱播放。
3. **任务看板**：成片发布看板——状态统计、近 7 日趋势、按日期分组的任务卡片，点击播放成片。
4. **自动发布**：发布流水线说明 + 平台接入 + 最近发布记录。

## 两条生产约束

- **产出目录固定**：制作完成的视频统一写入 `productions/projects/<工程>/deliver/`，不散落在其他位置。
- **模板源码只读**：制作过程中不修改 `templates/` 源码；确有特殊需求时，先复制工程到 `productions/projects/` 下再调整。

## 数据链路

- 平台页 `index.html` 通过 `/api/stats`、`/api/records`、`/projects/...` 取数；
- `web/serve.py` 把这些路径反向代理到任务服务（`127.0.0.1:8898`），媒体请求带 Range（成片可拖动播放）；
- 任务服务（`productions/pipeline/serve.py`）从 `platform.db` 读真实数据，与 CLI / 定时任务共用同一把锁。

## 新增模板

1. 在 `templates/` 下新建模板目录（参照 `TEMPLATE-STANDARD.md` 与现有模板结构）；
2. 编辑 `web/index.html` 底部 `TEMPLATES` 数组，追加一条记录（字段见数组内注释，路径相对 `web/` 写为 `../templates/<模板名>/...`）；
3. 刷新页面即可看到新卡片。

## 说明

- `productions/` 是运行时产出目录，已在 `.gitignore` 中，不纳入版本库；仓库只保留模板源码与平台代码。
- 样片 MP4 与部分字体由 Git LFS 管理；本地未检出（文件只有一百多字节指针）时先执行 `git lfs pull`。

## 关于

UniStudio 是**浙江联通开源**的 AI 视频创作工作室，由 zj-unicom-ai 团队维护，欢迎社区共建。

## License

[MIT](./LICENSE) · Copyright (c) 2026 zj-unicom-ai contributors
