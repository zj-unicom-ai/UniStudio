# EP01 配音声线试听

这段试听只用于检查中文发音和叙述节奏，不是正式配音，也没有据此重排全片镜头。

- 音频：`output/voice-audition/EP01_voice_audition_f0ee4ce3.wav`，17.07 秒，单声道 24 kHz。
- 声线：VoiceStudio 中已有的“沉稳专业男播音”设计声线（profile `f0ee4ce3`）；该 profile 是 voice design，不是对某位真人的克隆。
- 引擎：本机 VoiceStudio 0.5.6，`k2-fsa/OmniVoice`，通过本机 MPS 生成；模型当时已安装，没有触发模型下载。
- 试听文案取自 `content/EP01_SCRIPT.md` 的 S01：1921 年上海石库门、1927 年挫折、1935 年遵义。
- VoiceStudio 本机转写得到 6 个短句片段，总时长 17.07 秒。转写仅用于核对试听文本，不能替代正式录音的逐词时码校准。

## 模型许可

OmniVoice Hugging Face 模型卡将代码标为 Apache 2.0，将预训练模型标为 CC-BY-NC；项目维护者也说明该检查点不允许商业使用，且目前没有可商用检查点。[模型卡](https://huggingface.co/k2-fsa/OmniVoice) · [维护者许可说明](https://github.com/k2-fsa/OmniVoice/issues/258)。

因此，本试听不能作为已获公开或商业发行许可的证明。正式发布前，应使用取得授权的真人录音或许可条件匹配的 TTS，并保留对应授权记录。

## M4 用户选定声线

- 用户选定 VoiceStudio 已保存声线 **“国标视野”**（profile `c36e2897`）用于本片；该试听音频为 `output/voice-audition/EP01_S01_audition_guobiaoshijie.wav`，时长 22.41 秒、24 kHz 单声道。
- M4 全片旁白按九章生成，源文件在 `output/voice-m4/`，合并配音在 `media/voice/EP01_M4_narration.wav`。章节合成时长、ASR 核对和时间轴信息见同目录的 `manifest.json` 与 `content/EP01_TIMELINE_M4.json`。
- 声音模型仍为 VoiceStudio OmniVoice，预训练权重许可 CC-BY-NC。用户确认作品作非商业发布；发布说明应注明模型出处，商业版本需改用许可匹配的旁白。
