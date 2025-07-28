# gateway/config.py
MODEL_REGISTRY = {
    "qwen2": {
        "name": "Qwen2-7B-Instruct-GPTQ-Int4",
        "endpoint": "http://tgi-qwen2",
        "prompt_template": TEMPLATES["qwen2"],
        "stop": ["<|im_end|>"],                    # 文本级 stop（备用）
        "stop_token_ids": [151645]                 # <|im_end|> 的 token ID
    },
    "llama3": {
        "name": "Meta-Llama-3.1-8B-Instruct-GPTQ-INT4",
        "endpoint": "http://tgi-llama3",
        "prompt_template": TEMPLATES["llama3"],
        "stop": ["<|eot_id|>", "<|end_of_text|>"],  # 文本级 stop
        "stop_token_ids": [128001, 128009]          # <|eot_id|> 和 <|end_of_text|> 的 token ID
    }
}
