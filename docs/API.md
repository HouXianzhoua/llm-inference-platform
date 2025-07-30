# 📡 统一推理 API 文档

> 本平台提供统一的 RESTful API 接口，支持多模型路由、动态参数控制与多场景生成任务。

---

## 🌐 基础信息

- **Base URL**: `http://localhost:8000`
- **协议**: HTTP/HTTPS
- **认证**: 无需认证（本地环境），可扩展 JWT 或 API Key
- **Content-Type**: `application/json`
- **超时设置**: 读取超时 60s（根据 `max_new_tokens` 自动适应）

---

## 🧩 核心接口

### 1. `/v1/generate` —— 文本生成
> POST 生成补全或指令响应，支持多模型、多场景。

#### 请求
- **Method**: `POST`
- **Endpoint**: `/v1/generate`
- **Body** (JSON):

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model_id` | string | ✅ | 模型标识符：`qwen2` 或 `llama3` |
| `inputs` | string | ✅ | 输入文本（Prompt） |
| `scenario` | string | ❌ | 生成场景：`base`（默认）、`qa`、`summarize`、`rewrite` |
| `parameters` | object | ❌ | 生成参数（见下表） |

**`parameters` 子字段**：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_new_tokens` | int | 128 | 最大生成 token 数 |
| `temperature` | float | 0.7 | 采样温度，控制随机性（0.0~2.0） |
| `top_p` | float | 0.9 | 核采样比例（Nucleus Sampling） |
| `do_sample` | bool | true | 是否启用采样（`False` 为 greedy） |
| `stop` | string[] | [] | 自定义停止字符串（如 `["\n"]`） |

#### 响应
- **Status**: `200 OK`
- **Body** (JSON):

```json
{
  "generated_text": "生成的完整文本",
  "model": "Qwen2-7B-Instruct-GPTQ-Int4",
  "tokens": 87
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `generated_text` | string | 模型生成的文本（已去除 prompt） |
| `model` | string | 实际调用的模型名称 |
| `tokens` | int | 生成的 token 数量（估算） |

#### 错误码

| 状态码 | `error_code` | 说明 |
|--------|--------------|------|
| 400 | `MODEL_NOT_FOUND` | `model_id` 不支持 |
| 400 | `PROMPT_FORMAT_FAILED` | Prompt 模板格式化失败 |
| 504 | `INFERENCE_TIMEOUT` | 推理超时（>60s） |
| 503 | `DOWNSTREAM_REQUEST_FAILED` | TGI 服务不可达 |
| 500 | `TGI_SERVER_ERROR` | TGI 返回非 200 状态 |

---

## 🧪 使用示例

### 示例 1：基础对话（Qwen2）

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "qwen2",
    "inputs": "请用中文介绍你自己",
    "parameters": {
      "max_new_tokens": 128,
      "temperature": 0.7,
      "top_p": 0.9
    }
  }'
```

### 示例 2：问答任务（Llama3）

```bash
curl http://localhost:8000/v1/generate -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "llama3",
    "inputs": "牛顿三大定律是什么？",
    "scenario": "qa",
    "parameters": {
      "max_new_tokens": 200,
      "temperature": 0.5
    }
  }'
```

### 示例 3：摘要生成（Qwen2）

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

### 示例 4：内容改写（Llama3）

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

## 📋 模型管理接口

### 1. `GET /v1/models` —— 列出所有模型

返回所有已注册模型及其状态。

#### 请求
- **Method**: `GET`
- **Endpoint**: `/v1/models`

#### 响应
```json
{
  "models": [
    {
      "id": "qwen2",
      "name": "Qwen2-7B-Instruct-GPTQ-Int4",
      "status": "healthy",
      "supports": ["completion", "instruct"],
      "endpoint": "http://tgi-qwen2"
    },
    {
      "id": "llama3",
      "name": "Meta-Llama-3.1-8B-Instruct-GPTQ-INT4",
      "status": "healthy",
      "supports": ["completion", "instruct"],
      "endpoint": "http://tgi-llama3"
    }
  ]
}
```

---

### 2. `GET /health` —— 简要健康检查

返回整体健康状态。

#### 响应（200）
```json
{
  "status": "healthy",
  "models": {
    "qwen2": "healthy",
    "llama3": "healthy"
  },
  "total": 2
}
```

### 3. `GET /health/full` —— 详细健康检查

实时探测所有模型状态。

#### 响应（200）
```json
{
  "status": "healthy",
  "details": {
    "qwen2": "healthy",
    "llama3": "healthy"
  },
  "total": 2,
  "healthy": 2
}
```

---

## 🛠️ 参数调优建议

| 场景 | 推荐参数 |
|------|----------|
| **确定性输出**（如代码生成） | `temperature=0.1`, `do_sample=False` |
| **创意生成**（如诗歌、故事） | `temperature=0.9~1.5`, `top_p=0.9` |
| **摘要/问答** | `temperature=0.5~0.7`, `max_new_tokens=128~256` |
| **低延迟测试** | `max_new_tokens=32`, `temperature=0.1` |

---

## 📚 说明

- 所有模型均使用 **GPTQ-INT4 量化**，显存占用 < 7GB
- Prompt 模板已自动注入，无需手动添加 `<|im_start|>` 等标记
- 支持跨域请求（CORS），前端可直接调用
- 错误信息包含 `error_code`，便于前端处理

---

## 🔗 相关文档

- [部署指南](DEPLOY.md)
- [量化原理](QUANTIZATION.md)
- [性能测试](PERFORMANCE_TEST.md)
- [项目主页](../README.md)
