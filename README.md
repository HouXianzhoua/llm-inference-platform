# 🚀 多模型大语言模型推理服务平台

基于 **Text Generation Inference (TGI)** 与 **GPTQ INT4 量化** 技术构建的高性能、可扩展的本地 LLM 推理平台，支持 Qwen 与 Llama-3 多模型热切换，集成 FastAPI 统一 API 与 Grafana 可视化监控。

## ✅ 特性
- 🔤 支持 GPTQ 量化模型（INT4），显存 <7GB
- 🔄 多模型动态路由（`model_id`）
- 🧩 自动 prompt 模板适配（Qwen / Llama3）
- 📡 FastAPI 封装 RESTful 接口
- 📊 StatsD + InfluxDB + Grafana 实时监控
- 🐳 Docker Compose 一键部署
- 💻 适配本地 RTX 4070 Super（12GB）
- ☁️ 可迁移至阿里云 A10/A100 实例

## 🚀 快速启动
```bash
docker-compose up -d

详见 docs/DEPLOY.md
