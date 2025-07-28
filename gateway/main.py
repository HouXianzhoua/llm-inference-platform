# gateway/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging

from config import MODEL_REGISTRY

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Unified LLM Inference Gateway", version="1.0.0")

# 允许跨域（前端调试用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求/响应模型
class GenerateRequest(BaseModel):
    model_id: str = "qwen2"
    inputs: str
    parameters: dict = {}

class GenerateResponse(BaseModel):
    generated_text: str
    model: str
    tokens: int = None


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "models": list(MODEL_REGISTRY.keys()),
        "total": len(MODEL_REGISTRY)
    }


@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    model_id = request.model_id.lower()
    if model_id not in MODEL_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Model not supported: {model_id}. Options: {list(MODEL_REGISTRY.keys())}"
        )

    model_config = MODEL_REGISTRY[model_id]
    prompt = request.inputs
    parameters = request.parameters.copy()

    # === 注入 Prompt 模板 ===
    try:
        formatted_prompt = model_config["prompt_template"].format(input=prompt)
    except Exception as e:
        raise HTTPException(500, f"Failed to format prompt: {str(e)}")

    # === 设置 stop tokens（TGI 支持 stop 参数）===
    if "stop" in model_config:
        if "stop" in parameters:
            parameters["stop"] = parameters["stop"] + model_config["stop"]
        else:
            parameters["stop"] = model_config["stop"]

    # 构造转发给 TGI 的 payload
    tgi_payload = {
        "inputs": formatted_prompt,
        "parameters": parameters
    }

    logger.info(f"[{model_id}] Forwarding to {model_config['endpoint']}")
    logger.debug(f"Prompt: {formatted_prompt}")

    # === 转发请求到 TGI ===
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        try:
            resp = await client.post(f"{model_config['endpoint']}/generate", json=tgi_payload)
            resp.raise_for_status()
            result = resp.json()

            # 标准化返回格式
            generated_text = result.get("generated_text", "")
            return {
                "generated_text": generated_text,
                "model": model_config["name"],
                "tokens": len(generated_text.split())  # 简单估算
            }
        except httpx.TimeoutException:
            raise HTTPException(504, "Model inference timeout")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(503, f"Service unreachable: {str(e)}")
        except httpx.HTTPStatusError as e:
            err_detail = resp.text
            raise HTTPException(resp.status_code, f"Model error: {err_detail}")
