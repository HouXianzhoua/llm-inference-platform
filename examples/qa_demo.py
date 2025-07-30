# examples/qa_demo.py
"""
问答场景测试：Qwen2 vs Llama3
"""
import requests

BASE_URL = "http://localhost:8000/v1/generate"
QUESTIONS = [
    "牛顿三大定律是什么？",
    "光合作用的过程是怎样的？",
    "请解释量子纠缠的基本原理。"
]

def ask_question(model_id: str, question: str):
    print(f"\n❓ 输入问题: {question}")

    payload = {
        "model_id": model_id,
        "inputs": question,
        "scenario": "qa",
        "parameters": {
            "max_new_tokens": 256,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"✅ [{model_id.upper()}] 回答:")
        print(f"📝 {result['generated_text']}")
        print("-" * 80)
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    print("🔍 正在进行多模型问答对比测试...\n")
    for q in QUESTIONS:
        ask_question("qwen2", q)
        ask_question("llama3", q)
