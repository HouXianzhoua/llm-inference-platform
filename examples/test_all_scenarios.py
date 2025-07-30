# examples/test_all_scenarios.py
"""
一键测试所有模型 + 所有场景，并打印输入内容
"""
import requests

BASE_URL = "http://localhost:8000/v1/generate"
MODEL_IDS = ["qwen2", "llama3"]
SCENARIOS = ["base", "qa", "summarize", "rewrite"]
PROMPTS = {
    "base": "你好，今天过得怎么样？",
    "qa": "太阳为什么是热的？",
    "summarize": "机器学习是人工智能的一个分支，它允许系统从数据中学习并改进，而无需明确编程。",
    "rewrite": "这个电影很精彩，情节紧凑，演员演技出色。"
}

print("🧪 开始测试所有模型与场景组合...\n")
print("=" * 100)

for model in MODEL_IDS:
    for scenario in SCENARIOS:
        print(f"📌 测试: 模型 = {model.upper()}, 场景 = {scenario}")
        print(f"📥 输入内容: {PROMPTS[scenario]}")
        print(f"⚙️  请求参数: max_new_tokens=64, temperature=0.7")

        payload = {
            "model_id": model,
            "inputs": PROMPTS[scenario],
            "scenario": scenario,
            "parameters": {
                "max_new_tokens": 64,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        try:
            resp = requests.post(BASE_URL, json=payload)
            resp.raise_for_status()
            result = resp.json()
            print(f"✅ 输出: {result['generated_text']}")
        except Exception as e:
            print(f"❌ 请求失败: {e}")
        print("-" * 100)
