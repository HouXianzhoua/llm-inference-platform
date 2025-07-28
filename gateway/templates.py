# gateway/templates.py

TEMPLATES = {
    "qwen2": "<|im_start|>user\n{input}<|im_end|>\n<|im_start|>assistant\n",
    "llama3": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{input}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
    # 后续可扩展 bloom、chatglm 等
}
