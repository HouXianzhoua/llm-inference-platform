# 🚀 部署指南

> 本项目基于 **Text Generation Inference (TGI)** 与 **GPTQ-INT4 量化技术**，构建支持 `Qwen2-7B` 与 `Llama-3.1-8B` 双模型的本地化大语言模型推理平台。通过 FastAPI 统一网关路由请求，并集成完整监控体系。

---

## 🧰 环境要求

| 组件 | 版本/要求 |
|------|----------|
| 操作系统 | Ubuntu 20.04+ on WSL2 |
| GPU | NVIDIA GPU（推荐 ≥12GB 显存，如 RTX 4070 Super） |
| 驱动 | NVIDIA Driver ≥ 535 |
| CUDA | 支持 CUDA 12.2+（通过 WSL2 配置） |
| Docker | Docker Desktop for Windows + Docker Engine ≥ 24.0 |
| Docker Compose | ≥ v2.23.0 |
| 磁盘空间 | ≥ 15GB（模型 + 容器） |
| 内存 | ≥ 16GB RAM（建议） |

---

## 🔽 第一步：准备模型（GPTQ-INT4 量化版）

使用 `git lfs` 下载 Hugging Face 上的 GPTQ 量化模型。

### 1. 安装 git-lfs（首次）

```bash
sudo apt update && sudo apt install git-lfs -y
git lfs install
```

### 2. 创建模型目录并下载

```bash
mkdir -p models
```

#### 下载 Qwen2-7B-Instruct-GPTQ-Int4

```bash
git clone https://huggingface.co/Qwen/Qwen2-7B-Instruct-GPTQ-Int4 models/Qwen2-7B-Instruct-GPTQ-Int4
```

#### 下载 Llama-3.1-8B-Instruct-GPTQ-INT4

```bash
git clone https://huggingface.co/hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4 models/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4
```

> 💡 模型总大小约 12GB，请确保磁盘空间充足。

---

## 🌐 第二步：创建共享网络

Docker Compose 中的服务需在同一网络中通信。创建一个外部网络：

```bash
docker network create app-network
```

> ⚠️ 确保 `docker-compose.yml` 中的 `networks.app-net.name` 与之匹配。

---

## ▶️ 第三步：一键启动全部服务

项目已提供 `docker-compose.yml`，一键启动 TGI 推理服务、FastAPI 网关与监控系统。

### 启动命令

```bash
docker-compose up --build
```

### 服务说明

| 服务 | 端口 | 功能 |
|------|------|------|
| `tgi-qwen2` | 内部 80 | Qwen2-7B-Instruct-GPTQ-Int4 推理后端 |
| `tgi-llama3` | 内部 80 | Llama-3.1-8B-Instruct-GPTQ-INT4 推理后端 |
| `gateway` | `8000:8000` | 统一 API 网关（FastAPI） |
| `statsd-exporter` | 9125 | 接收 StatsD 指标 |
| `influxdb` | 8086 | 时序数据库 |
| `grafana` | `3000:3000` | 监控可视化面板 |

> 🕐 首次启动较慢（约 3-5 分钟），因需加载两个 INT4 模型至 GPU。

---

## 🧪 第四步：测试推理 API

### 1. 基础测试（curl）

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen2",
    "inputs": "你好",
    "parameters": {
      "max_new_tokens": 64,
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'
```

预期响应：
```json
{
  "generated_text": "你好！有什么我可以帮助你的吗？",
  "model": "Qwen2-7B-Instruct-GPTQ-Int4",
  "tokens": 12
}
```

### 2. 测试 Llama3 模型

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama3",
    "inputs": "Hello, how are you?",
    "parameters": {
      "max_new_tokens": 64
    }
  }'
```

### 3. 使用 Python 脚本测试

运行内置测试脚本：

```bash
python scripts/test_api.py
```

---

## 📊 第五步：访问监控系统

### 1. Grafana 可视化面板

访问：[http://localhost:3000](http://localhost:3000)

- **默认账号**：`admin`
- **默认密码**：`admin`（首次登录后可修改）

### 2. 仪表盘功能

已预配置以下监控项：
- 📈 请求总量（`requests.total`）
- ⏱️ 请求延迟 P95/P99（`request.latency`）
- 🧠 按模型统计输入/输出 token 数
- 🔴 错误请求计数（timeout, model error）

> 仪表盘配置见 `monitoring/grafana/dashboards/`

---

## 🛠️ 第六步：多场景推理测试

### 问答（QA）

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama3",
    "inputs": "光合作用的原理是什么？",
    "scenario": "qa",
    "parameters": {
      "max_new_tokens": 128,
      "temperature": 0.5
    }
  }'
```

### 摘要生成

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen2",
    "inputs": "人工智能是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统……",
    "scenario": "summarize",
    "parameters": {
      "max_new_tokens": 100
    }
  }'
```

### 内容改写

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama3",
    "inputs": "这个产品非常好，大家都很喜欢。",
    "scenario": "rewrite",
    "parameters": {
      "max_new_tokens": 64,
      "temperature": 0.9
    }
  }'
```

---

## 📊 验证资源占用

在另一个终端运行：

```bash
nvidia-smi
```

应看到：
- GPU 显存占用 **< 7.5 GB**（双模型加载）
- 进程 `docker-containerd-shim` 或 `python` 占用 GPU
- GPU 利用率随推理请求波动

---

## 🧩 配置说明

### 1. FastAPI 网关配置

- 路由逻辑：`gateway/main.py`
- 模型注册表：`gateway/config.py`
- Prompt 模板：`gateway/templates.py`
- 日志与监控：集成 `statsd` + `logging`

### 2. TGI 启动参数

| 参数 | 说明 |
|------|------|
| `--quantize=gptq` | 启用 GPTQ INT4 量化 |
| `--trust-remote-code` | 允许加载 Qwen/Llama3 自定义代码 |
| `--max-input-length` | 最大输入长度 |
| `--max-total-tokens` | 总上下文长度（KV Cache） |
| `--cuda-memory-fraction` | 限制 GPU 显存使用比例（Qwen2 设置为 0.6） |

---

## 🔄 后续扩展

- ✅ **支持更多模型**：只需在 `models/` 添加模型，并更新 `config.py`
- ✅ **迁移到云环境**：支持阿里云 A10/A100 实例，只需修改 `docker-compose.yml`
- ✅ **性能优化**：启用 `--cuda-graphs`、`--max-batch-size` 等高级参数
- ✅ **前端界面**：可对接 Gradio 或自定义 Web UI

---

## 📚 参考文档

- [统一 API 文档](API.md)
- [GPTQ 量化原理](QUANTIZATION.md)
- [性能测试指南](PERFORMANCE_TEST.md)
- [项目主页](../README.md)
