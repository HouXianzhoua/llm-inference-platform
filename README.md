# Unified LLM Inference Gateway

基于 **Text Generation Inference (TGI)** 与 **GPTQ 量化技术** 构建的多模型大语言模型推理服务平台，支持 **Qwen2-7B-Instruct** 与 **Meta-Llama-3.1-8B-Instruct** 的热加载、按需切换与统一 API 接入。

本项目专为本地 GPU 环境（如 RTX 4070 Super 12GB）优化，同时具备向阿里云 A10/A100 等企业级 GPU 实例迁移的能力，适用于多模型服务、A/B 测试、性能评估等场景。

🔧 **核心特性**  
✅ 双模型支持（Qwen2 / Llama3）GPTQ-Int4 量化，显存友好  
✅ 统一 FastAPI 网关，RESTful API 接入  
✅ 动态路由：通过 `model_id` 指定模型，支持热切换  
✅ 多场景 Prompt 模板（问答 / 摘要 / 改写 / 通用）  
✅ 自动适配模型专用模板（Qwen: `<|im_start|>`，Llama3: `<|eot_id|>`）  
✅ 异步高并发处理（基于 `httpx`）  
✅ 完整监控系统：StatsD + InfluxDB + Grafana + GPU 实时监控  
✅ Docker Compose 一键部署，开箱即用  
✅ 开源可复现，支持本地与云端部署  

📊 **性能表现（压测结果）**  
在 **100 并发用户、2秒等待** 的压力测试下（Locust）：

| 模型 | QPS | P99 延迟 |
|------|-----|----------|
| Qwen2-7B-Instruct-GPTQ-Int4 | 20 | 4.2s |
| Llama3-8B-Instruct-GPTQ-INT4 | 20 | 3.9s |

> ✅ 系统稳定，支持长时间高负载运行

🚀 **快速启动**
```bash
# 1. 克隆项目
git clone https://github.com/yourname/llm-inference-platform.git
cd llm-inference-platform

# 2. 下载模型（需 Hugging Face Token）
huggingface-cli download Qwen/Qwen2-7B-Instruct-GPTQ-Int4 --local-dir models/Qwen2-7B-Instruct-GPTQ-Int4
huggingface-cli download hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4 --local-dir models/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4

# 3. 启动监控系统（StatsD + InfluxDB + Grafana）
docker-compose -f monitoring/docker-compose.monitor.yml up -d

# 4. 启动推理网关与模型服务
docker-compose up -d

# 5. 测试聊天 CLI（支持模型切换）
python examples/chat_cli.py
```

🌐 **API 接口**
```bash
POST http://localhost:8000/v1/generate
```
```json
{
  "model_id": "qwen2",
  "inputs": "你好，世界！",
  "scenario": "qa",
  "parameters": {
    "max_new_tokens": 128,
    "temperature": 0.8,
    "top_p": 0.9
  }
}
```

📈 **监控可视化**
- 访问 Grafana 仪表盘：`http://localhost:3000`（账号: `admin`，密码: `grafana`）
- 查看：请求量、延迟（P99）、QPS、GPU 利用率、显存占用等核心指标

📚 **文档**
- [API 说明](docs/API.md)
- [部署指南](docs/DEPLOY.md)
- [性能测试报告](docs/PERFORMANCE_TEST.md)
- [量化模型说明](docs/QUANTIZATION.md)

☁️ **上云准备**
已验证可迁移至 **阿里云 A10/A100 GPU 实例**，详见 [DEPLOY.md](docs/DEPLOY.md)。

---

## 项目结构
```
.
├── docker-compose.yml               # 主服务：TGI + Gateway
├── monitoring/                      # 监控栈：InfluxDB + Grafana + StatsD + GPU 监控
├── gateway/                         # FastAPI 网关核心
│   ├── main.py                      # API 路由与请求处理
│   ├── model_manager.py             # 模型健康探测
│   ├── templates.py                 # Qwen/Llama3 多场景 Prompt 模板
│   └── config.py                    # 模型注册表
├── models/                          # 本地模型存储目录
├── examples/                        # 示例脚本
│   └── chat_cli.py                  # 支持模型切换的命令行聊天
└── docs/                            # 项目文档
```

## 许可证
MIT License
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
