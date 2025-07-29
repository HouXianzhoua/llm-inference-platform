# scripts/load_test.py
import asyncio
import httpx
import time
import json
from typing import List

# 配置
GATEWAY_URL = "http://localhost:8000/v1/generate"
CONCURRENT_REQUESTS = 20  # 并发数
TEST_MODEL = "qwen2"
TEST_PROMPT = "请简要介绍人工智能的发展历程。"

async def send_request(client: httpx.AsyncClient, request_id: int) -> dict:
    """
    发送单个生成请求
    """
    payload = {
        "model_id": TEST_MODEL,
        "inputs": f"{TEST_PROMPT} [Request-{request_id}]",  # 添加ID便于日志追踪
        "parameters": {
            "max_new_tokens": 64,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "stop": []  # 可选：测试 stop token 的影响
        }
    }

    start_time = time.time()
    try:
        response = await client.post(GATEWAY_URL, json=payload)
        end_time = time.time()
        latency = end_time - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"✅ REQ-{request_id:02d} | Status: {response.status_code} | Latency: {latency:.2f}s | Tokens: {result.get('tokens', 'N/A')}")
            return {"success": True, "latency": latency, "status": response.status_code}
        else:
            print(f"❌ REQ-{request_id:02d} | Status: {response.status_code} | Error: {response.text[:100]}...")
            return {"success": False, "latency": latency, "status": response.status_code, "error": response.text}
    except Exception as e:
        end_time = time.time()
        latency = end_time - start_time
        print(f"🔥 REQ-{request_id:02d} | Exception: {type(e).__name__}: {e}")
        return {"success": False, "latency": latency, "exception": str(e)}

async def main():
    print(f"🚀 Starting load test: {CONCURRENT_REQUESTS} concurrent requests to {GATEWAY_URL}")
    print(f"📝 Model: {TEST_MODEL}, Prompt: '{TEST_PROMPT}'")

    # 使用连接池
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
        # 创建并发任务
        tasks = [send_request(client, i) for i in range(CONCURRENT_REQUESTS)]
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # 统计结果
    successes = [r for r in results if isinstance(r, dict) and r.get("success")]
    failures = [r for r in results if not isinstance(r, dict) or not r.get("success")]

    print("\n" + "="*50)
    print("📊 LOAD TEST RESULTS")
    print("="*50)
    print(f"Total Requests: {CONCURRENT_REQUESTS}")
    print(f"Success: {len(successes)}")
    print(f"Failure: {len(failures)}")
    print(f"Success Rate: {len(successes)/CONCURRENT_REQUESTS*100:.1f}%")

    if successes:
        avg_latency = sum(s["latency"] for s in successes) / len(successes)
        print(f"Average Latency (Success): {avg_latency:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
