#!/bin/bash
# dev-restart.sh

echo "🔄 重启所有服务..."
docker-compose down
docker-compose up -d

echo "✅ 所有服务已重启"
echo "🔁 正在监听 gateway/ 文件变化..."

# 使用 fswatch 或 inotifywait 监听文件变化（macOS/Linux）
# 每次保存 main.py 就自动重启
fswatch -r ./gateway | while read; do
  echo "🔁 检测到代码变化，正在重启..."
  docker-compose restart gateway
done
