# monitoring/gpu_monitor.py
import time
import pynvml
import statsd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 StatsD
client = statsd.StatsClient('statsd-exporter', 9125)  # 本地运行

def monitor_gpu():
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        logger.info(f"Found {device_count} GPU(s)")
    except Exception as e:
        logger.error(f"Failed to init NVML: {e}")
        return

    while True:
        for i in range(device_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)

                # 上报指标
                client.gauge('gpu.utilization', util.gpu)
                client.gauge('gpu.memory_used', mem_info.used / 1024**2)  # MB
                client.gauge('gpu.memory_util', (mem_info.used / mem_info.total) * 100)

                logger.debug(f"GPU-{i}: {util.gpu}% | Mem: {mem_info.used/1024**2:.0f}MB")
            except Exception as e:
                logger.error(f"Failed to get GPU-{i} info: {e}")
        time.sleep(5)  # 每5秒上报一次

if __name__ == "__main__":
    monitor_gpu()
