# 双引擎集成规范

## 架构结论

**Huashu 不是 HyperFrames 的现成插件。** 最稳妥的桥接是：

```text
口播稿 + 审核资料
        │
        ├── 程序化解释镜头：Huashu SKILL / y3 JSON / render.py
        │      → MP4 片段（4–8s） → media/huashu/
        │
        ├── 章节结构 / 文本 / 时间轴 → EP01_TIMELINE.json
        │      → Canvas2D/GSAP 逐帧可寻址画面
        │
        └── 真人录音 / TTS / 字幕
                   ↓
         HyperFrames HTML Composition
            ├── base Canvas 动态轨
            ├── Huashu 已渲好的 MP4 视频轨
            ├── 旁白及音乐轨（需要补齐）
            └── 定时字幕（需要按音频真实时码对齐）
                   ↓
           MP4 + 各章源文件 + QA
```

## 为什么不直接复制 Huashu 引擎进 HyperFrames

- Huashu 的已有 render.py 管线用 Playwright/Canvas/FFmpeg 控制帧，Huashu 本身有完整的镜头/转场机制；HF 控制的是 HTML/GSAP 时间和媒体轨。
- 要整合成一条共用的实时 JS 时钟，需要改写不少状态/seek 契约，并非其 README 现成导出接口。
- 先渲成 8s MP4 片段，不丢失“画真正动起来”的效果，又能准确控制时间、声轨和审核。

## 已写入的桥接器

`huashu-specs/*.json`: 官方示例兼容的白板语法，结构为 `grammar, duration, fps, width, height, theme, cues`；每段最长 8s，样片收束段为 7s。

`render_huashu.sh`: 默认调用 `third_party/huashu-art-motion/scripts/engine/render.py --spec ... --out ...`；如已有外部源码，可用 `HUASHU_REPO=/Users/wrg/mystudy/huashu-art-motion` 指向它，不会复制或修改 Huashu 仓库。

`build_composition.py`: 对所有存在的 MP4 用 ffprobe 读取真实时长，将 `<video class="clip" data-start data-duration data-track-index>` 插入 HF，生成 `compositions/index-with-huashu.html`。此文件有独立 composition id，通过 `hyperframes render --composition compositions/index-with-huashu.html` 渲染。

**计划插入位置**：1921 组织图解 05:40；1927 道路变化 09:15；1929 组织建设 13:20；1935 决策调整 17:10。均为演示占位时码，待真实旁白录音后逐项修改。

60 秒样片 `compositions/EP01_60s_preview.html` 按四段各 15s 编排。最后一段把 8s 的 1935 议题图解和 7s 白板收束接在同一轨道上；该样片独立于 20 分钟版的四个演示插入点。

## 代码约束

- 基础动画 `renderAt(t)` 给定时间即可重画。HF 中通过 `gsap.timeline({paused:true})` 创建 **有限** 1200s 时间线，`onUpdate` 按虚拟 clock 调用 `renderAt`。运行前需安装 GSAP，输出不能依赖 `Date.now()` 和随机状态。
- HF 的 clip/合成数据属性可能随仓库版本调整，升级后以当期官方 docs + lint/check 为准。
- 层级：默认 Canvas 主画面，Huashu 全屏片段优先级更高；如需品牌 Logo 与字幕贯穿其上，请再增加独立 overlay 轨，不要用 canvas 覆盖媒体轨。
- 合成页不应插入不存在的 MP4；脚本已默认跳过缺文件。
- Huashu 白板默认 `chalk` 的主题色不同于赤金规范；Codex 后续需修改其 theme/palette 以匹配，不要只在两个风格间硬切。
