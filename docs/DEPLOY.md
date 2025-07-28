# 🚀 部署指南

本文档介绍如何在本地环境（WSL2 + NVIDIA GPU）上部署基于 Text Generation Inference (TGI) 的大语言模型推理服务，支持 GPTQ 量化模型的高效运行。

**当前已验证支持模型：**
- `Qwen/Qwen2-7B-Instruct-GPTQ-Int4`

**后续将扩展支持：**
- `hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4`

---

## 🧰 环境要求

| 组件 | 版本/要求 |
|------|----------|
| 操作系统 | Ubuntu 20.04+ on WSL2 |
| GPU | NVIDIA GPU（推荐 12GB+ 显存，如 RTX 4070 Super） |
| 驱动 | NVIDIA Driver ≥ 535 |
| CUDA | 支持 CUDA 12.2+（通过 WSL2 配置） |
| Docker | Docker Desktop for Windows + Docker Engine ≥ 24.0 |
| Docker Compose | ≥ v2.23.0 |
| 磁盘空间 | ≥ 10GB（用于模型缓存） |

---

## 🔽 1. 下载模型（GPTQ-Int4 量化版）

使用 `git lfs` 克隆 Hugging Face 上的 GPTQ 量化模型：

```bash
# 创建模型目录
mkdir -p models

# 下载 Qwen2-7B-Instruct-GPTQ-Int4
git lfs install
git clone https://huggingface.co/Qwen/Qwen2-7B-Instruct-GPTQ-Int4 models/Qwen2-7B-Instruct-GPTQ-Int4
---

## ▶️ 2. 启动 TGI 推理服务

使用提供的脚本启动 Qwen2 模型服务：

```bash
./scripts/start-tgi-qwen.sh
```

该脚本内容如下：

```bash
#!/bin/bash
docker run --rm \
  --gpus all \
  --shm-size 1g \
  -p 8080:80 \
  -v $PWD/models/Qwen2-7B-Instruct-GPTQ-Int4:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id /data \
  --quantize gptq \
  --max-input-length 2048 \
  --max-total-tokens 4096 \
  --trust-remote-code
```

### 参数说明：
- `--quantize gptq`: 启用 GPTQ INT4 量化推理
- `--trust-remote-code`: 允许加载 Qwen 自定义模型代码
- `--max-*`: 控制上下文长度与显存使用
- `-v`: 将本地模型目录挂载到容器内

服务启动后将在 `http://localhost:8080` 提供 API 接口。

---

## 🧪 3. 测试推理 API

### 方法一：使用 curl

```bash
curl http://localhost:8080/generate \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "inputs": "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user\n请用中文介绍你自己。<|im_end|>\n<|im_start|>assistant\n",
        "parameters": {
            "max_new_tokens": 128,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": false
        }
    }'
```

### 方法二：使用 Python 脚本

运行测试脚本：

```bash
python scripts/test_api.py
```

预期输出示例：
```json
{
  "generated_text": "我是通义千问，由阿里云研发的超大规模语言模型……"
}
```

> ⚠️ 注意：Qwen2 使用特殊的 prompt 格式，请确保输入符合 `<|im_start|>role\ncontent<|im_end|>` 结构。

---

## 📊 4. 验证资源占用

在另一个终端运行：

```bash
nvidia-smi
```

应看到：
- GPU 显存占用 **< 7GB**
- 进程 `docker-containerd-shim` 或 `python` 占用 GPU

---

## 🧩 后续步骤

下一步将：
1. 部署第二个模型：Llama-3.1-8B-Instruct-GPTQ-INT4
2. 构建 FastAPI 网关，实现多模型路由
3. 自动化 prompt 模板适配

详见 [QUANTIZATION.md](QUANTIZATION.md) 了解 GPTQ 量化原理。
```

---


