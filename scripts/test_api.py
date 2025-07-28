# scripts/test_api.py
import requests
import json

url = "http://localhost:8000/v1/generate"

def test_model(
    prompt: str,
    model_id: str = "qwen2",
    max_tokens: int = 128,
    temperature: float = 0.7,
    top_p: float = 0.9,
    do_sample: bool = True,
    stop: list = None  # 新增：支持 stop tokens
):
    parameters = {
        "max_new_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "do_sample": do_sample
    }
    if stop is not None:
        parameters["stop"] = stop  # 只有传了才加

    data = {
        "model_id": model_id,
        "inputs": prompt,
        "parameters": parameters
    }

    print(f"\n🚀 Testing [{model_id.upper()}] '{prompt}'")
    print(f"⚡ Params: temp={temperature}, top_p={top_p}, max_tokens={max_tokens}")
    if stop:
        print(f"🛑 Stop tokens: {stop}")
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

# ✅ 参数测试
test_model("Tell me a joke", "qwen2", max_tokens=64)
test_model("Tell me a joke", "qwen2", max_tokens=64, temperature=0.1)
test_model("Tell me a joke", "qwen2", max_tokens=64, temperature=1.5, top_p=0.5)
test_model("你好", "qwen2", max_tokens=100, stop=["<|im_end|>"])
test_model("Hello", "llama3", max_tokens=100, stop=["<|eot_id|>"])
test_model("", "qwen2")
test_model("你好", "qwen2", max_tokens=256)
test_model("你好", "qwen2", max_tokens=256, stop=["\n\n"])
