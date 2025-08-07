# gateway/tokenizer.py

from transformers import AutoTokenizer
import os

# 模型路径（根据你项目 models/ 目录调整）
MODEL_PATHS = {
    "qwen2": "/app/models/Qwen2-7B-Instruct-GPTQ-Int4",
    "llama3": "/app/models/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4"
}

# 缓存 tokenizer 实例
TOKENIZERS = {}

def get_tokenizer(model_id: str):
    if model_id not in TOKENIZERS:
        model_path = MODEL_PATHS.get(model_id)
        if not model_path or not os.path.exists(model_path):
            raise ValueError(f"Tokenizer model path not found for model_id: {model_id}")
        TOKENIZERS[model_id] = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    return TOKENIZERS[model_id]

def count_tokens(model_id: str, text: str) -> int:
    tokenizer = get_tokenizer(model_id)
    return len(tokenizer.encode(text))

