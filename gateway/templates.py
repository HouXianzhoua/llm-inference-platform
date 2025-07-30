# gateway/templates.py
TEMPLATES = {
    # === 基础模板（用于通用对话）===
    "qwen2": {
        "base": "<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n",
        "qa": "<|im_start|>system\n你是一个知识丰富的助手，请准确回答用户问题。<|im_end|>\n<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n",
        "summarize": "<|im_start|>system\n请对以下内容进行简洁摘要，不超过100字。<|im_end|>\n<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n",
        "rewrite": "<|im_start|>system\n请改写以下内容，保持原意但更流畅自然。<|im_end|>\n<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n"
    },
    "llama3": {
        "base": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "qa": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "summarize": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nSummarize the following text in under 100 words.<|eot_id|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
        "rewrite": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nParaphrase the following text fluently while preserving meaning.<|eot_id|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    }
}
