# examples/summarize_demo.py
"""
文本摘要测试：长文本 → 简洁摘要
"""
import requests

BASE_URL = "http://localhost:8000/v1/generate"

LONG_TEXT = """
人工智能（Artificial Intelligence，简称 AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
这些任务包括学习、推理、问题解决、感知、语言理解等。近年来，深度学习的突破推动了 AI 的快速发展，
特别是在图像识别、自然语言处理和语音识别等领域取得了显著成果。
大语言模型（LLM）如 GPT、Qwen、Llama 等，能够生成高质量文本，已被广泛应用于写作辅助、代码生成、客服机器人等场景。
然而，AI 也面临伦理、偏见、可解释性等挑战，需要技术、法律和社会的共同治理。
"""

def summarize(model_id: str):
    print(f"\n📋 正在请求 {model_id.upper()} 进行摘要...")
    print(f"📄 原文:\n{LONG_TEXT}")

    payload = {
        "model_id": model_id,
        "inputs": LONG_TEXT,
        "scenario": "summarize",
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.5,
            "top_p": 0.9
        }
    }

    try:
        response = requests.post(BASE_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        print(f"✅ 摘要结果:")
        print(f"📝 {result['generated_text']}")
        print("-" * 80)
        return result
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        return None

if __name__ == "__main__":
    print("📝 正在测试文本摘要功能...")
    summarize("qwen2")
    summarize("llama3")
