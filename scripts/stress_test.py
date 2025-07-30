# scripts/stress_test.py
import time
import random
import asyncio
import httpx

# 测试数据
TEST_CASES = [
    "你好",
    "请介绍一下量子力学",
    "帮我写一首诗，关于春天",
    "你是谁？",
    "帮我写一个简单的Python函数",
    "用英文说一个笑话",
    "Describe the solar system",
    "Tell me a story about a dragon and a knight",
]

# 请求参数设置
PARAMS_LIST = [
    {"temperature": 0.7, "top_p": 0.9, "max_new_tokens": 128},
    {"temperature": 0.3, "top_p": 0.95, "max_new_tokens": 256},
    {"temperature": 1.2, "top_p": 0.7, "max_new_tokens": 64},
]

# 模型列表
MODELS = ["qwen2", "llama3"]

# 请求构造
async def send_request(client, text, params, model):
    try:
        payload = {
            "model_id": model,
            "inputs": text,
            "parameters": params,
        }
        response = await client.post("http://localhost:8000/v1/generate", json=payload)
        response.raise_for_status()
        print(f"[✓] {model} OK | Prompt: {text[:10]}... | {params}")
    except Exception as e:
        print(f"[✗] {model} ERROR | {e}")

# 并发执行
async def run_stress_test(concurrency=10, duration=60):
    timeout = httpx.Timeout(10.0, read=60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        start_time = time.time()
        while time.time() - start_time < duration:
            tasks = []
            for _ in range(concurrency):
                prompt = random.choice(TEST_CASES)
                model = random.choice(MODELS)
                params = random.choice(PARAMS_LIST)
                tasks.append(send_request(client, prompt, params, model))
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)  # 控制节奏

if __name__ == "__main__":
    # 并发请求数, 运行时长（秒）
    asyncio.run(run_stress_test(concurrency=5, duration=60))


