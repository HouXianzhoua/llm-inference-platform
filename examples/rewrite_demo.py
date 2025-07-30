# examples/rewrite_demo.py
"""
文本改写/润色测试：展示 temperature 的影响
"""
import requests

BASE_URL = "http://localhost:8000/v1/generate"

ORIGINAL_TEXT = "这个产品很好，它有很多功能，用户体验也不错，推荐大家使用。"

def rewrite(model_id: str, temperature: float):
    print(f"\n🔄 正在请求 {model_id.upper()} 进行改写 (temperature={temperature})...")
    print(f"📄 原文: {ORIGINAL_TEXT}")

    payload = {
        "model_id": model_id,
        "inputs": ORIGINAL_TEXT,
        "scenario": "rewrite",
        "parameters": {
            "max_new_tokens": 128,
            "temperature": temperature,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"✅ 改写结果:")
        print(f"📝 {result['generated_text']}")
        print("-" * 80)
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    print("✍️ 正在测试文本改写功能（temperature 影响）...")
    for temp in [0.3, 0.7, 1.0]:
        print(f"\n--- 🌡️ temperature = {temp} ---")
        rewrite("qwen2", temp)
        rewrite("llama3", temp)
