# scripts/test_api.py
import requests
import json

def test_model(prompt: str, model_id: str = "qwen2", max_tokens: int = 128):
    url = "http://localhost:8000/v1/generate"
    data = {
        "model_id": model_id,
        "inputs": prompt,
        "parameters": {"max_new_tokens": max_tokens}
    }

    print(f"\n🚀 Testing [{model_id.upper()}] '{prompt}'")
    try:
        resp = requests.post(url, json=data)
        print(f"HTTP {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Generated: {result['generated_text'][:200]}...")
        else:
            print(f"❌ Error: {resp.text}")
    except Exception as e:
        print(f"💥 Exception: {e}")

# --- 测试用例 ---
test_model("请用中文写一首关于秋天的诗", "qwen2")
test_model("Write a poem about autumn in English", "llama3")
test_model("Hello?", "bloom")  # 应报错
