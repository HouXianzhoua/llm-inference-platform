# scripts/test_stop_tokens.py
import requests
import json

def test_stop_tokens(model_id: str, prompt: str, user_stop: list = None):
    url = "http://localhost:8000/v1/generate"
    
    parameters = {
        "max_new_tokens": 256,
        "temperature": 0.7,
        "top_p": 0.9
    }
    if user_stop:
        parameters["stop"] = user_stop

    data = {
        "model_id": model_id,
        "inputs": prompt,
        "parameters": parameters
    }

    print(f"\n🔍 Testing [{model_id.upper()}] with stop={user_stop}")
    print(f"📝 Prompt: {prompt}")
    
    try:
        resp = requests.post(url, json=data)
        print(f"📡 HTTP {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            output = result["generated_text"]
            print(f"✅ Output: {output}")
            
            # 检查是否真的停止了
            for stop_token in (user_stop or []):
                if stop_token in output:
                    end_idx = output.find(stop_token)
                    after = output[end_idx + len(stop_token):].strip()
                    if after:
                        print(f"⚠️  WARNING: Content after '{stop_token}': '{after[:50]}...'")
                    else:
                        print(f"🟢 PASSED: Stopped cleanly at '{stop_token}'")
                else:
                    print(f"🟡 NOTE: '{stop_token}' not found in output")
        else:
            print(f"❌ Error: {resp.text}")
    except Exception as e:
        print(f"💥 Exception: {e}")

# --- 测试用例 ---
print("🚀 Starting stop tokens test...")

# ✅ Qwen2: 测试 <|im_end|> 是否生效
test_stop_tokens(
    model_id="qwen2",
    prompt="你好",
    user_stop=["<|im_end|>"]
)

# ✅ Llama3: 测试 <|eot_id|> 是否生效
test_stop_tokens(
    model_id="llama3",
    prompt="Hello",
    user_stop=["<|eot_id|>"]
)

# ✅ 测试多个 stop tokens
test_stop_tokens(
    model_id="qwen2",
    prompt="请写一个Python函数计算斐波那契数列",
    user_stop=["<|im_end|>", "\n\n"]  # 遇到任一就停
)
