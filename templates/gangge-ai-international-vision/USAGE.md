# 使用方法

## 环境与示例

需要 Node.js 22+ / npm、Python 3、FFmpeg/FFprobe 和 HyperFrames 能使用的浏览器。`npm run compose`、`npm run check`、`npm run render -- --allow-demo` 从本模板目录执行即可验证样例。根脚本负责转到内置工程，默认最终视频、封面和播放页写入根 `out/`，字幕在内置工程 `renders/subtitles.srt`。

预览：`npm run dev`。查看及停止服务时进入 `assets/template-project/` 执行 `npx --yes hyperframes@0.8.133 preview --status` / `preview --stop`。

## 新内容

优先复制到新工程：`python3 scripts/new_project.py /path/to/new-project`，再进入新工程按其 README 操作，不覆盖本模板。也可直接在本库的模板副本中改 `assets/template-project/story-data.json` 与 `voice-requests.json`。

画面可改字段：`project_title`、`brand`、`date_label`、`source_line`、`scenes`、`scene_titles`、`scene_boundaries`。保留 `base_css` 和品牌组件。场景边界是各页第一段旁白在 segments 中的零基索引；段数与场景数随内容调整。

旁白：按 segments 的 id 导入 `assets/template-project/assets/voice-guobiao/<id>.wav`，替换样例静音轨后 `npm run compose -- --narration`。如用 TTS，进入内置工程执行 `python3 scripts/generate_voiceover.py --url YOUR_ENDPOINT --voice YOUR_VOICE --model YOUR_MODEL`，可经 TTS_API_KEY 环境变量配置密钥，不能提交密钥。脚本只接受 WAV。

重配后 compose 按真实 WAV 时长生成字幕与时间线，再 check 和 render。`npm run render -- --output out/my-episode.mp4` 可指定根目录相对输出路径。正常有声作品不使用 --allow-demo。

## 品牌组件与输出

片尾及 Logo、三段片尾音效在内置工程 `compositions/gangge-ai-outro/`，翻页音效在 `assets/sfx/`。复制时连同 HTML、资源目录、字体和 GSAP 一起复制。所有渲染资源路径相对工程，无原作者电脑绝对路径。

完整封面为1080×1920 PNG，默认抽取最终 MP4 0.7秒的完整首页；播放页绑定该 PNG。不要为了让视频第0帧与封面相同而移除已经确认的开场动画。

## 常见情况

缺 WAV 会报错；样例静音轨是模板验证用，不能当作真实配音。没有国标视野声线配置时使用自己获得授权的声线或直接导入音频。字体较大时 CLI 会提示未内联，但文件已随工程提供，经本地资源路径加载。Noto 与原机苹方字形稍有差别，不能承诺和旧片像素一致。

样例已在同一电脑的新解压目录完成构建、检查和渲染；未跨操作系统实测。检查为0错误、5个原结构提示，详见 VALIDATION.md。
