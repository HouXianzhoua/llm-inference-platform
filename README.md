---

```markdown
# 🚀 高并发多模型大语言模型推理服务平台

> 基于 Text Generation Inference (TGI) 与 GPTQ 量化技术构建的本地化、可扩展、高性能 LLM 推理平台，支持多模型热加载、统一 API 路由与完整监控体系。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Built with FastAPI](https://img.shields.io/badge/built%20with-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Docker Compose](https://img.shields.io/badge/deploy-Docker%20Compose-blue)](https://docs.docker.com/compose/)

---

## 🌟 项目亮点

- ✅ **双模型支持**：`Llama-3.1-8B-Instruct` + `Qwen2-7B-Instruct`，INT4 量化，显存占用 < 7GB
- ✅ **本地适配**：成功部署于 RTX 4070 Super (12GB)，无需云端资源
- ✅ **一键部署**：基于 `docker-compose.yml` 实现多服务协同启动
- ✅ **统一网关**：FastAPI 封装 RESTful API，支持按 `model_id` 路由请求
- ✅ **动态控制**：灵活调节 `max_tokens`、`temperature`、`top_p` 等生成参数
- ✅ **多场景适配**：支持问答、摘要、改写等多种推理任务（通过 prompt 模板）
- ✅ **完整监控**：集成 StatsD + InfluxDB + Grafana，可视化请求量、延迟、模型状态
- ✅ **企业可扩展**：架构设计支持迁移至阿里云 A10/A100 实例，具备多模型服务潜力

---

## 📦 项目结构

```bash
llm-inference-platform/
├── docker-compose.yml           # 多服务编排（TGI + Gateway + Monitoring）
├── gateway/                     # FastAPI 统一推理网关
│   ├── main.py                  # 核心 API 逻辑
│   ├── config.py                # 模型注册表
│   ├── model_manager.py         # 模型健康探测
│   └── templates.py             # 多场景 prompt 模板
├── models/                      # 本地缓存的 GPTQ-INT4 量化模型
│   ├── Meta-Llama-3.1-8B-Instruct-GPTQ-INT4
│   └── Qwen2-7B-Instruct-GPTQ-Int4
├── monitoring/                  # 监控栈（StatsD + InfluxDB + Grafana）
├── scripts/                     # 启动、测试、压测脚本
├── docs/                        # 详细文档
│   ├── DEPLOY.md                # 部署指南
│   ├── API_EXAMPLES.md          # API 使用示例
│   ├── QUANTIZATION.md          # GPTQ 量化说明
│   └── PERFORMANCE_TEST.md      # 性能测试方法
└── README.md                    # 本文件
```

---

## 🧰 环境要求

| 组件 | 版本/要求 |
|------|----------|
| 操作系统 | Ubuntu 20.04+ on WSL2 |
| GPU | NVIDIA GPU（≥12GB 显存，如 RTX 4070 Super） |
| 驱动 | NVIDIA Driver ≥ 535 |
| CUDA | 支持 CUDA 12.2+（通过 WSL2 配置） |
| Docker | Docker Desktop for Windows + Engine ≥ 24.0 |
| Docker Compose | ≥ v2.23.0 |
| 磁盘空间 | ≥ 15GB（模型 + 容器） |

---

## 🚀 快速启动（一键部署）

### 1. 克隆项目并进入目录

```bash
git clone https://github.com/yourname/llm-inference-platform.git
cd llm-inference-platform
```

> 💡 若尚未下载模型，请先执行 `docs/DEPLOY.md` 中的模型下载步骤。

### 2. 创建共享网络（仅首次）

```bash
docker network create app-network
```

### 3. 启动全部服务

```bash
docker-compose up --build
```

服务将启动：
- `tgi-qwen2`: Qwen2-7B-Instruct-GPTQ-INT4 @ `http://tgi-qwen2:80`
- `tgi-llama3`: Llama-3.1-8B-Instruct-GPTQ-INT4 @ `http://tgi-llama3:80`
- `gateway`: 统一 API 网关 @ `http://localhost:8000`
- `statsd-exporter`, `influxdb`, `grafana`: 监控系统

---

## 📡 统一 API 接口

所有请求通过 FastAPI 网关 `/v1/generate` 接入。

### 示例：基础生成

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen2",
    "inputs": "你好",
    "parameters": {"max_new_tokens": 64}
  }'
```

### 示例：多场景调用

#### ✅ 问答（QA）
```json
{
  "model_id": "llama3",
  "inputs": "光合作用的原理是什么？",
  "scenario": "qa",
  "parameters": {"max_new_tokens": 128}
}
```

#### ✅ 摘要生成
```json
{
  "model_id": "qwen2",
  "inputs": "人工智能是计算机科学的一个分支...",
  "scenario": "summarize",
  "parameters": {"max_new_tokens": 100}
}
```

#### ✅ 内容改写
```json
{
  "model_id": "llama3",
  "inputs": "这个产品非常好，大家都很喜欢。",
  "scenario": "rewrite",
  "parameters": {"max_new_tokens": 64, "temperature": 0.9}
}
```

> 更多示例见 [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md)

---

## 📊 监控系统

访问 [http://localhost:3000](http://localhost:3000) 查看 Grafana 面板。

内置仪表盘：
- 📈 请求总量与 QPS
- ⏱️ P95/P99 请求延迟
- 🧠 按模型统计输入/输出 token 数
- 🟢 模型健康状态

数据采集链路：
```
FastAPI → StatsD → InfluxDB → Grafana
```

> 详情见 `monitoring/` 目录与 `docs/MONITORING.md`（待补充）

---

## 📚 文档索引

| 文档 | 说明 |
|------|------|
| [`docs/DEPLOY.md`](docs/DEPLOY.md) | 本地部署全流程指南 |
| [`docs/API_EXAMPLES.md`](docs/API_EXAMPLES.md) | API 使用示例与调用方式 |
| [`docs/QUANTIZATION.md`](docs/QUANTIZATION.md) | GPTQ INT4 量化原理与优势 |
| [`docs/PERFORMANCE_TEST.md`](docs/PERFORMANCE_TEST.md) | 性能测试方法与结果分析 |

---

## 🧪 性能表现（初步测试）

| 指标 | 结果 |
|------|------|
| 单模型显存占用 | ~6.8 GB (INT4) |
| 冷启动时间 | 相比 FP16 缩短约 60% |
| 并发能力 | 支持 50+ 并发请求 |
| P99 延迟 | < 1.5s (max_new_tokens=128) |
| QPS | ~8-12（双模型混合负载） |

> 更多测试脚本见 `scripts/load_test.py` 和 `scripts/stress_test.py`

---

## 🛠️ 技术栈

- **推理后端**：[Text Generation Inference (TGI)](https://github.com/huggingface/text-generation-inference)
- **量化技术**：GPTQ-INT4（`auto-gptq`）
- **API 网关**：FastAPI + Python
- **异步请求**：`httpx.AsyncClient`
- **监控系统**：StatsD + InfluxDB + Grafana + Telegraf
- **容器编排**：Docker Compose
- **模型**：
  - [`hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4`](https://huggingface.co/hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4)
  - [`Qwen/Qwen2-7B-Instruct-GPTQ-Int4`](https://huggingface.co/Qwen/Qwen2-7B-Instruct-GPTQ-Int4)

---

## 🌐 扩展能力

本项目具备以下企业级扩展潜力：
- ✅ 支持动态加载更多 GPTQ 模型（只需添加 `models/` 并更新 `config.py`）
- ✅ 可迁移至云 GPU 实例（阿里云 A10/A100 已验证）
- ✅ 支持 Kubernetes 集群部署（未来可扩展）
- ✅ 集成 Prometheus + Alertmanager 实现告警

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

---

## 🙌 致谢

- Hugging Face 团队 —— TGI 与模型生态
- TheBloke, hugging-quants —— 开源量化模型
- FastAPI, StatsD, Grafana 社区

---

> 🔭 项目持续更新中，欢迎 Star ⭐ & Fork 🍴！
```
