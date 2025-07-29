# gateway/model_manager.py
"""
模型管理模块：负责探测和维护所有后端模型的健康状态。
"""
import httpx
from typing import Dict, List, Optional
from config import MODEL_REGISTRY

class ModelManager:
    def __init__(self):
        # 存储每个 model_id 的健康状态
        self.status: Dict[str, str] = {model_id: "unknown" for model_id in MODEL_REGISTRY}
        # 使用长连接客户端，提高探测效率
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(5.0))

    async def probe_model(self, model_id: str) -> bool:
        """
        探测指定模型是否健康
        :param model_id: 如 "qwen2"
        :return: True if healthy
        """
        config = MODEL_REGISTRY[model_id]
        endpoint = config["endpoint"]  # e.g., http://tgi-qwen2

        try:
            # 发送一个极短的生成请求，测试模型是否响应
            payload = {
                "inputs": "你好",
                "parameters": {
                    "max_new_tokens": 8,           # 只生成几个 token，快速返回
                    "temperature": 0.1,            # 确定性输出
                    "do_sample": False,
                    "stop": config.get("stop", []) # 使用默认 stop，防止无限生成
                }
            }

            # 调用 TGI 的 /generate 接口
            resp = await self.client.post(f"{endpoint}/generate", json=payload)
            
            # 成功且返回文本，认为健康
            if resp.status_code == 200:
                result = resp.json()
                generated = result.get("generated_text", "").strip()
                # 简单判断：是否有生成内容？
                return len(generated) > 0
            return False

        except (httpx.RequestError, httpx.TimeoutException, Exception) as e:
            # 任何网络错误、超时、解析错误都视为不健康
            return False

    async def check_all(self):
        """
        探测所有注册的模型，更新 self.status
        """
        for model_id in MODEL_REGISTRY:
            is_healthy = await self.probe_model(model_id)
            self.status[model_id] = "healthy" if is_healthy else "unhealthy"

    def get_model_list(self) -> List[Dict]:
        """
        返回模型列表，供 /v1/models 接口使用
        """
        return [
            {
                "id": k,
                "name": v["name"],
                "status": self.status[k],
                "supports": ["completion", "instruct"],
                "endpoint": v["endpoint"]
            }
            for k, v in MODEL_REGISTRY.items()
        ]

    async def close(self):
        """
        关闭 HTTP 客户端，用于应用关闭时
        """
        await self.client.aclose()

# ========== 全局实例 ==========
# 我们在整个应用中只使用一个 ModelManager 实例
manager = ModelManager()
