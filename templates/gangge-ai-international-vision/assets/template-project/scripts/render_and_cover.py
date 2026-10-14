import argparse
import json
import html
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path('renders/刚哥聊AI_国际视野_定稿.mp4')


def run(args):
    subprocess.run(args, cwd=PROJECT, check=True)


def main():
    parser = argparse.ArgumentParser(description='Render the finished film and export a full-cover frame as the cover.')
    parser.add_argument('--allow-demo', action='store_true', help='Render the explicitly silent template sample')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--quality', choices=['draft', 'looks', 'delivery'], default='delivery')
    args = parser.parse_args()
    mode_path = PROJECT / 'voice-mode.json'
    if mode_path.exists() and json.loads(mode_path.read_text()).get('mode') == 'demo-silent' and not args.allow_demo:
        parser.error('Silent demo audio: use --allow-demo to verify the sample, or import real WAVs and compose --narration.')
    output = args.output if args.output.is_absolute() else PROJECT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    cover = output.with_name(output.stem + '_封面.png')
    playback = output.with_name(output.stem + '_播放页.html')
    run(['npx', '--yes', 'hyperframes@0.8.133', 'render', '--quality', args.quality, '--output', str(output)])
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError(f'Render output missing or empty: {output}')
    # The original v3 opening reveals the title over the first half-second.
    # Use a later frame for the standalone platform cover while preserving that motion in the MP4.
    run(['ffmpeg', '-y', '-v', 'error', '-i', str(output), '-ss', '0.7', '-frames:v', '1', '-update', '1', str(cover)])
    if not cover.is_file() or cover.stat().st_size == 0:
        raise RuntimeError(f'Cover extraction failed: {cover}')
    rel_video = html.escape(output.name, quote=True)
    rel_cover = html.escape(cover.name, quote=True)
    page = f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>刚哥聊天 AI--国际视野</title><style>body{{margin:0;background:#080d1c;color:#f4f7ff;font-family:system-ui;text-align:center}}video{{display:block;width:min(100%,480px);max-height:88vh;margin:20px auto;background:#080d1c;object-fit:contain}}p{{margin:16px}}a{{color:#69e4ff}}</style><video controls playsinline preload="metadata" poster="{rel_cover}" src="{rel_video}"></video><p>刚哥聊AI · 国际视野</p><p><a href="{rel_video}" download>下载 MP4</a>　<a href="{rel_cover}" download>下载首页封面 PNG</a></p></html>'''
    playback.write_text(page, encoding='utf-8')
    print(f'MP4: {output}')
    print(f'首页封面（取自视频0.7秒完整画面）: {cover}')
    print(f'播放页（已绑定封面）: {playback}')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Release export failed: {exc}', file=sys.stderr)
        raise
