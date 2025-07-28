# gateway/config.py

MODEL_REGISTRY = {
    "qwen2": {
        "name": "Qwen2-7B-Instruct-GPTQ-Int4",
        "endpoint": "http://tgi-qwen2",
        "prompt_template": "<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n",
        "stop": ["<|im_end|>"]
    },
    "llama3": {
        "name": "Meta-Llama-3.1-8B-Instruct-GPTQ-INT4",
        "endpoint": "http://tgi-llama3",
        "prompt_template": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "stop": ["<|eot_id|>", "<|end_of_text|>"]
    }
}
