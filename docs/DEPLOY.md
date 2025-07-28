# 部署指南

## 环境要求
- WSL2 with NVIDIA GPU Driver
- Docker Desktop with GPU support
-至少 12GB 显存（如 RTX 4070 Super）
- Hugging Face Token（用于下载闭源模型）

## 启动服务
```bash
docker-compose up -d访问服务
API 网关：http://localhost:8000/v1/generate
Grafana：http://localhost:3000（账号 admin/admin）
详见各模块文档。
