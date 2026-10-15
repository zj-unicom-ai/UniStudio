# 模板接入标准

每个模板独立放在 `templates/<模板ID>/`。模板源文件只读，制作时复制到 `productions/projects/<工程>/`。

必需内容：

- README.md：适用场景、画幅、制作输入、实际构建/检查/渲染命令和交付物。
- package.json 与 HyperFrames 工程入口；固定依赖版本，所有媒体路径在工程内可解析。
- 可编辑内容数据与示例素材；SOURCES.md / LICENSE 记录事实来源和素材授权。
- preview/cover.png（或相应封面文件）与样片，明确静音占位、模拟数据和额外服务要求。
- 若有专门操作约束，提供 SKILL.md / USAGE.md / TOOLS.md；不硬编码个人电脑路径、私人账号或不可迁移的声线。

在 `templates/catalog.json` 登记 ID、展示名、目录、画幅、是否有旁白、可选 SKILL 路径和 project_source。后者通常为 `.`，包裹工程可指向 `assets/template-project`。`new` 从这里复制。新增后同步 `web/index.html` 的 TEMPLATES 展示信息，ID 必须与目录一致；其封面和样片路径相对 web/。

验证：环境预检通过；复制的新目录可独立构建/检查/预览/渲染；新旁白不依赖作者声线；最终 MP4 与封面进入 deliver/ 后可 ready 登记和看板播放。添加到 catalog 不代表模板已通过验证，贡献时应说明验证范围。
