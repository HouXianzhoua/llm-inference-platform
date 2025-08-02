# scripts/monitor_gpu.sh
#!/bin/bash

# 检查是否在 WSL2 中且有 nvidia-smi
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. Are you in WSL2 with GPU enabled?"
    exit 1
fi

# 生成时间戳文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="gpu_monitor_${TIMESTAMP}.log"

echo "📊 Starting GPU monitoring... Logging to $LOG_FILE"
echo "Timestamp, GPU Util (%), Memory Util (%), Memory Used (MB), Memory Total (MB)" >> "$LOG_FILE"

# 每1秒采样一次，按 CSV 格式输出
nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total \
           --format=csv -l 1 >> "$LOG_FILE" &

# 保存后台进程 PID，便于后续停止
MONITOR_PID=$!

# 提供停止方法
echo "✅ GPU monitoring started (PID: $MONITOR_PID)"
echo "To stop: kill $MONITOR_PID"
echo "Or press Ctrl+C"

# 等待用户中断
trap "echo '🛑 Stopping GPU monitoring...'; kill $MONITOR_PID 2>/dev/null; exit 0" INT TERM

# 持续运行
while true; do sleep 1; done
