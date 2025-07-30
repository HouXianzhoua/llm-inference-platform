# gateway/config.py
from templates import TEMPLATES

MODEL_REGISTRY = {
    "qwen2": {
        "name": "Qwen2-7B-Instruct-GPTQ-Int4",
        "endpoint": "http://tgi-qwen2",
        "prompt_templates": TEMPLATES["qwen2"],  # 改为字典
        "default_template": "base",  # 默认模板
        "stop": ["<|im_end|>"],
        "stop_token_ids": [151645]
    },
    "llama3": {
        "name": "Meta-Llama-3.1-8B-Instruct-GPTQ-INT4",
        "endpoint": "http://tgi-llama3",
        "prompt_templates": TEMPLATES["llama3"],
        "default_template": "base",
        "stop": ["<|eot_id|>", "<|end_of_text|>"],
        "stop_token_ids": [128001, 128009]
    }
}
