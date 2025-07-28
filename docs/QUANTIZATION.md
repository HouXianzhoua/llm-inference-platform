# GPTQ INT4 量化说明

本项目采用 **GPTQ（General-Purpose Quantization）** 技术对大语言模型进行 **INT4 低比特量化**，显著降低模型显存占用，提升推理效率，使其能够在消费级 GPU（如 RTX 4070 Super 12GB）上高效部署。

## 什么是 GPTQ？

GPTQ 是一种针对大语言模型的后训练量化方法，能够在几乎不损失模型性能的前提下，将模型权重从 FP16 或 FP32 量化为 INT4（4-bit 整数）。相比传统量化方法，GPTQ 在保持高精度的同时，大幅减少显存占用和计算开销。

- 📚 论文：[GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers](https://arxiv.org/abs/2210.17323)
- ⚙️ 实现：基于 Hugging Face `auto-gptq` 库，与 `text-generation-inference` 深度集成

## 为什么使用 INT4？

| 精度类型 | 显存占用（估算） | 优势 | 适用场景 |
|----------|------------------|------|----------|
| FP16     | 2 bytes/参数      | 高精度，原始性能 | 实验室环境 |
| INT8     | 1 byte/参数       | 显存减半 | 一般推理 |
| **INT4** | **0.5 bytes/参数** | **显存降低 75%** | **本地/边缘部署** |

> 举例：7B 参数模型  
> - FP16：约 14 GB 显存  
> - INT4：约 **3.5 GB 权重 + 3~4 GB 缓存 ≈ 6.8 GB**

## 本项目量化模型

| 模型名称 | 原始显存（FP16） | 量化后显存（INT4） | 量化方式 | Hugging Face ID |
|---------|------------------|--------------------|----------|------------------|
| Qwen2-7B-Instruct | ~14 GB | ~6.8 GB | GPTQ-INT4 | `Qwen/Qwen2-7B-Instruct-GPTQ-Int4` |
| Meta-Llama-3.1-8B-Instruct | ~16 GB | ~7.2 GB | GPTQ-INT4 | `hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4` |

## TGI 中的量化配置

在 `docker-compose.yml` 或启动命令中，通过以下参数启用 GPTQ 量化：

```yaml
command:
  - --model-id=/data
  - --quantize=gptq
  - --trust-remote-code
  - --quantize=gptq：启用 GPTQ 解码器感知量化
  - --trust-remote-code：允许加载自定义模型代码（Qwen/Llama3 所需）
```
## 注意事项
首次加载较慢：INT4 模型需在 GPU 上进行反量化，首次推理延迟略高。
精度微损：INT4 量化可能导致极轻微的生成质量下降，但在大多数场景下不可察觉。
必须使用支持 GPTQ 的推理后端：如 text-generation-inference 或 vLLM（部分支持）。

## 扩展性
该量化方案可无缝迁移至云环境（如阿里云 A10/A100 实例），支持企业级多模型并发推理服务，具备良好的成本效益与扩展能力。

---
