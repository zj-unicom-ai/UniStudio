#!/usr/bin/env bash
# 起一个"真实 Chrome 调试实例"用于接管视频号助手发布。
# 独立 --user-data-dir，可与用户日常 Chrome 并存（Chrome 136+ 不允许在默认配置开调试端口）。
# 用法: bash launch_wechat_chrome.sh [起始URL] [端口]
set -euo pipefail

URL="${1:-https://channels.weixin.qq.com/platform/post/create}"
PORT="${2:-9333}"
PROFILE_DIR="${HOME}/.chrome-wxpublish"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if [[ ! -x "$CHROME" ]]; then
  echo "未找到 Google Chrome: $CHROME" >&2
  exit 2
fi

# 端口被占就报错，让用户换端口（避免撞到主 Chrome 的僵尸调试端点）
if curl -s --max-time 2 "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
  echo "端口 ${PORT} 已有可用调试端点，直接 'agent-browser connect ${PORT}' 即可" >&2
  exit 0
fi

nohup "$CHROME" \
  --remote-debugging-port="${PORT}" \
  --user-data-dir="${PROFILE_DIR}" \
  --no-first-run --no-default-browser-check \
  "$URL" >/tmp/chrome-wxpublish.log 2>&1 &
PID=$!
echo "launched pid ${PID}"

# 等 CDP 端点就绪
for _ in $(seq 1 15); do
  sleep 1
  if curl -s --max-time 3 "http://127.0.0.1:${PORT}/json/version" | grep -q webSocketDebuggerUrl; then
    echo "CDP ready on http://127.0.0.1:${PORT}"
    echo "下一步: agent-browser connect ${PORT}"
    exit 0
  fi
done

echo "调试端口 ${PORT} 未就绪，查看 /tmp/chrome-wxpublish.log" >&2
exit 1
