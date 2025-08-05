# locustfile.py - 修正版
from locust import HttpUser, task, constant_pacing
import random

class LLMUser(HttpUser):
    # 每2秒（或更快）发送一次请求，模拟持续流量
    wait_time = constant_pacing(1.5)  # 比2秒快，增加压力

    @task
    def generate(self):
        # 随机选择模型
        model_id = random.choice(["qwen2", "llama3"])
        
        # 构造符合你 FastAPI 模型定义的 payload
        payload = {
            "model_id": model_id,
            "inputs": "请解释量子计算的基本原理。",
            "scenario": random.choice(["base", "qa", "summarize", "rewrite"]),  # 测试不同场景
            "parameters": {
                "max_new_tokens": 128,      # TGI 参数
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # 发送到正确的 API 端点
        with self.client.post("/v1/generate", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Got {response.status_code}: {response.text}")
