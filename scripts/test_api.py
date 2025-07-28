import requests

url = "http://localhost:8080/generate"

prompt = """<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
请用中文介绍你自己。<|im_end|>
<|im_start|>assistant\n"""

data = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 128,
        "temperature": 0.7,
        "top_p": 0.9,
        "return_full_text": False
    }
}

response = requests.post(url, json=data)
print(response.json())
