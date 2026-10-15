# 使用方法

## 1. 准备环境

- Node.js 22+(脚本经 `npx --yes hyperframes@0.8.138` 调用 CLI,首次运行需联网下载)。
- Chromium 与 FFmpeg:按 HyperFrames 当前环境要求在本机准备(检查与渲染依赖)。
- Python 3(仅 `fill.py` 填充内容时需要,标准库即可,无第三方依赖)。
- GSAP 3.14.2 与 Noto Sans SC、Archivo、JetBrains Mono 从 CDN 加载；检查和渲染需要联网。
- 渲染提速(可选):`export PRODUCER_BROWSER_GPU_MODE=hardware` 启用硬件 GPU,26.5s 竖屏样片约 20s 出片。

命令使用相对路径，不依赖作者电脑的绝对路径。填充命令从模板根目录执行，HyperFrames 命令从生成的 `out/` 目录执行。

## 2. 替换内容(推荐:填充脚本)

1. 复制 `content.example.json` 为 `content.<产品>.json`,按下表改字段:

| 字段组 | 键 | 说明 |
| --- | --- | --- |
| 品牌色 | `COOL` / `WARM` | 两个 hex 即可换品牌;浅色调与半透明档由 color-mix 自动派生 |
| 封面 | `EYEBROW_BRAND` `COVER_L1` `COVER_L2` `COVER_PAYOFF` | 顶部仪表条品牌、两行主标题、暖金收益行 |
| 卖点 | `F_EYEBROW` `F_TITLE` `F_BODY` `F_CHIP1..3` | 冷色功能标题(可含 `<br />`)、正文、三个规格 chips |
| 规格 | `S_EYEBROW` `S1..S4_KEY/VAL/UNIT/W` | 四行参数:等宽键、大值、单位、进度条宽度(如 `86%`) |
| 大数字 | `ST_EYEBROW` `ST_NUM` `ST_UNIT` `ST_CAP` `ST_SUB` | 头条数字、倍率符号、标签、注释 |
| 情绪 | `E_EYEBROW` `E_L1` `E_L2` `E_BODY` `E_GHOST` | 暖调页两行标题、正文、一个出血底纹字(单字最佳) |
| 结尾 | `BRAND_MARK` `BRAND_LATIN` `C_L1` `C_L2` `C_PILL` `C_DATE` | 品牌单字 mark、拉丁名、CTA 两行、胶囊文案、日期 |

2. 填充:`python3 fill.py content.<产品>.json out/`(会生成 `out/index.html`，并拷入 `package.json`、HyperFrames 配置与 assets；`out/` 是临时构建目录)。
3. 用你的产品图覆盖 `out/assets/hero.jpg`(竖幅约 2:3、主体居中、上下留白)与 `out/assets/macro.jpg`(方形微距、浅景深)。AI 生成图记得裁掉底部水印(约 140px)。打光建议"冷色主光 + 暖色 rim",与双色系统呼应。
4. 在 `out/` 内检查与渲染(见第 6 节)；正式成片和封面放到工程根目录的 `deliver/`。

## 3. 直接改 index.html 也可以

`index.html` 本身就是完整示例:六页为六个 `class="clip"` 的场景 div(`#c1`–`#c6`),文案直接在 markup 里改;品牌色改 `<style>` 顶部 `:root` 的 `--cool` / `--warm`。适合只改一两处文案的轻量修改。

## 4. 调整时长与节奏

六页时间写在每个 clip 的 `data-start` / `data-duration`,总时长在 `#root` 的 `data-duration`。**注意**:主时间轴 `<script>` 内的补间使用绝对秒定位,改 clip 时间必须同步改对应补间的起始时间,否则动效会错位。默认节奏已调好,非必要不动。

## 5. 配乐

- 默认 `assets/bgm.mp3` 已内置:Mixkit《Trap Electro Vibes》,带鼓点推进感,从原曲 10s 裁 26.5s(跳过慢热铺垫),0.3s 淡入、结尾 2s 淡出。
- 换曲:覆盖 `assets/bgm.mp3` 即可(保持 26.5s,或同步改 `<audio>` 的 `data-duration`)。配方:`ffmpeg -y -ss <起裁秒> -t 26.5 -i <源>.mp3 -af "afade=t=in:st=0:d=0.3,afade=t=out:st=24.5:d=2.0" -codec:a libmp3lame -q:a 2 assets/bgm.mp3`。
- 选曲方法:用 `volumedetect` 分窗(每 4–5s)对比开头与中段,挑"开头不拖、中段稳"的窗口做起裁点。备选:氛围向 Mixkit id 175《Digital Clouds》@0s;四踩脉冲 id 726《Uplifting Bass》@12s。
- 配乐挂根级 `<audio data-track-index="10">`,跨场景连续,不要塞进某个 clip。

## 6. 检查、预览和渲染

```bash
cd out
npm install        # 安装固定版本的 HyperFrames composition 运行时
npm run check      # lint + 浏览器门禁(运行时/布局/动效/对比度)
npm run dev        # Studio 预览；检查后按 Ctrl+C 停止
npx --yes hyperframes@0.8.138 snapshot --at 1.8,6,11,15.5,19.5,24.5   # 六页关键帧接触表
mkdir -p ../deliver
PRODUCER_BROWSER_GPU_MODE=hardware npm run render -- --quality high --output ../deliver/product-promo.mp4
ffmpeg -y -ss 0.5 -i ../deliver/product-promo.mp4 -frames:v 1 -update 1 ../deliver/cover.png
```

`lint` 必须 0 error、`check` 必须 passed 才渲染;snapshot 接触表用于核对六页画面(封面/主体/结尾至少各看一眼)。预览并检查导出的 MP4、BGM 和封面后，再按 UniStudio 工作流把视频与封面登记到看板。

## 常见问题

- **lint 报 `font_family_without_font_face`**:字体回退里写了系统字体名(如 PingFang SC)。本模板用 `"Noto Sans SC", -apple-system, sans-serif`,不要加系统字体名。
- **lint 报 `nested_structure_needs_subcomposition`(警告)**:本模板刻意用单文件六 clip,该警告只是 Studio 时间轴显示建议,可忽略。
- **check 的 info 级 `container_overflow` / `canvas_overflow`**:刻意的 Ken Burns 裁切、光晕出血、情绪页出血底纹字,可忽略。
- **check 对比度警告(约 1.1:1,t≈19.1s)**:情绪页 7% 不透明度的装饰底纹字,刻意,可忽略。
- **渲染出黑屏/元素不出现**:检查是否在同一元素上叠了冲突变换(入场 y 与同时 scale);环境运动必须挂在时间轴 `tl` 上,裸 `gsap.to` 渲染时不出现。
- **图片不显示**:合成内资源路径必须根相对(`assets/hero.jpg`),写 `../assets/` 会 lint 报错。
