# scripts/test_api.py
import requests

def test_model(url, prompt, model_name):
    resp = requests.post(
        f"{url}/generate",
        json={
            "inputs": prompt,
            "parameters": {"max_new_tokens": 128}
        }
    )
    print(f"[{model_name}] Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"Response: {resp.json()['generated_text']}\n")
    else:
        print(f"Error: {resp.text}\n")

# 测试 Qwen2
test_model("http://localhost:8080", "请用中文写一首关于秋天的诗", "Qwen2")

# 测试 Llama3
test_model("http://localhost:8081", "Write a poem about autumn in English", "Llama3")
