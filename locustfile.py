from locust import HttpUser, task, between, constant_pacing
import random

class LLMUser(HttpUser):
    wait_time = constant_pacing(2)  # 每2秒发一次请求

    @task
    def generate_llama3(self):
        if random.choice([True, False]):
            self.client.post("/generate", json={
                "model": "llama3",
                "prompt": "请用三句话介绍人工智能。",
                "max_tokens": 128,
                "temperature": 0.7,
                "top_p": 0.9
            })
        else:
            self.client.post("/generate", json={
                "model": "qwen2",
                "prompt": "请用三句话介绍人工智能。",
                "max_tokens": 128,
                "temperature": 0.7,
                "top_p": 0.9
            })
