---
name: tech-product-promo-vertical
description: 使用科技产品竖屏 Promo 模板制作六页产品发布短片。适用于手机、硬件、SaaS 或 AI 产品宣传；固定 9:16、约 26.5 秒、BGM-only，无旁白。
---

# 科技产品宣传｜竖屏 Promo

## 制作流程

1. 阅读 `README.md`、`USAGE.md`、`TOOLS.md` 和 `SOURCES.md`。确认用户提供的产品事实、卖点、规格、品牌素材与 CTA；不要沿用样例里的虚构品牌、参数和日期。
2. 近期价格、性能和上市信息须核对可信来源，并在本期工程记录来源。无法核实的数据不要包装成实测结果。
3. 保持模板的六页结构、9:16 画幅、26.5 秒节奏和无旁白声音设计。产品主图放 `assets/hero.jpg`，卖点微距图放 `assets/macro.jpg`，配乐放 `assets/bgm.mp3`；替换的素材须有适用于目标用途的授权。
4. 将 `content.example.json` 复制为本期 JSON，填写品牌色、封面、卖点、4 项规格、核心数据、情绪页和 CTA。检查文案长度与 `<br />` 换行，特别核对单位、百分比和日期。
5. 在工程根目录填充并进入生成目录：

   ```sh
   python3 fill.py content.<产品>.json out/
   cd out
   npm install
   npm run check
   npm run dev
   ```

6. 使用 HyperFrames snapshot 检查六页关键帧，预览主要转场后停止预览服务。检查通过后将视频输出到工程根目录 `deliver/`，并从成片截取完整封面：

   ```sh
   mkdir -p ../deliver
   npm run render -- --quality high --output ../deliver/product-promo.mp4
   ffmpeg -y -ss 0.5 -i ../deliver/product-promo.mp4 -frames:v 1 -update 1 ../deliver/cover.png
   ```

7. 检查最终视频画面、BGM、分辨率、帧率、时长和封面。只有核验完成后才按 UniStudio 流程执行 `ready` 登记；检查未通过则记录制作失败原因。

## 模板边界

- 本模板使用固定的六页内容与时间线；更改场景时长需要同步调整主时间轴补间。
- 模板无 TTS、数字人或生成服务；默认 BGM 和 AI 占位图的授权边界见 `SOURCES.md`。
- GSAP 与字体从 CDN 加载，构建、预览和渲染需要网络。
