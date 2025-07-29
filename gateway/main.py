# gateway/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import logging
from model_manager import manager
from config import MODEL_REGISTRY
import uuid
import time
from fastapi import Request

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
    parameters: dict = {
        "max_new_tokens": 128,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
        "stop": []  # 允许用户自定义 stop
    }

class GenerateResponse(BaseModel):
    generated_text: str
    model: str
    tokens: int = None

@app.on_event("startup")
async def startup_event():
    """
    应用启动时，探测所有模型状态
    """
    await manager.check_all()
    logging.info("✅ ModelManager initialized. Probed all models.")

@app.get("/v1/models")
async def list_models():
    """
    列出所有支持的模型及其状态
    """
    # 确保状态最新（可选：也可只在 startup 时探测）
    # await manager.check_all()  # 如果想每次请求都探测，取消注释
    return {"models": manager.get_model_list()}

@app.get("/health/full")
async def health_full():
    """
    返回详细健康信息，包含每个模型的状态
    """
    await manager.check_all()  # 实时探测
    return {
        "status": "healthy" if all(s == "healthy" for s in manager.status.values()) else "degraded",
        "details": manager.status,
        "total": len(manager.status),
        "healthy": sum(1 for s in manager.status.values() if s == "healthy")
    }

@app.get("/health")
async def health():
    await manager.check_all()
    all_healthy = all(s == "healthy" for s in manager.status.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "models": manager.status,
        "total": len(MODEL_REGISTRY)
    }

CLIENT_TIMEOUT = httpx.Timeout(
    connect=5.0,  # 连接TGI服务的超时
    read=60.0,    # 读取响应的超时，根据 max_new_tokens 动态调整更佳
    write=10.0,   # 发送请求的超时
    pool=5.0      # 从连接池获取连接的超时
)

@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    request_id = str(uuid.uuid4())[:8]
    model_id = request.model_id.lower()
    start_time = time.time()

    # === 日志：请求开始 ===
    logger.info(f"[{request_id}] Received | model={model_id} | input_len={len(request.inputs.split())} tokens")

    if model_id not in MODEL_REGISTRY:
        error_msg = f"Model not supported: {model_id}"
        logger.warning(f"[{request_id}] Reject: {error_msg}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "InvalidModel",
                "error_code": "MODEL_NOT_FOUND",
                "details": error_msg
            }
        )

    model_config = MODEL_REGISTRY[model_id]
    prompt = request.inputs
    parameters = request.parameters.copy()

    # === 注入 Prompt 模板 ===
    try:
        formatted_prompt = model_config["prompt_template"].format(input=prompt)
    except Exception as e:
        error_msg = f"Failed to format prompt for {model_id}: {str(e)}"
        logger.error(f"[{request_id}] Template error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "TemplateError",
                "error_code": "PROMPT_FORMAT_FAILED",
                "details": str(e)
            }
        )

    # 合并 stop tokens 和 stop_token_ids（保持你原有的逻辑）
    final_stop = set(model_config.get("stop", []))
    if "stop" in parameters:
        final_stop.update(parameters["stop"])
    if final_stop:
        parameters["stop"] = list(final_stop)

    if "stop_token_ids" in model_config:
        if "stop_token_ids" in parameters:
            parameters["stop_token_ids"] = list(
                set(parameters["stop_token_ids"]) | set(model_config["stop_token_ids"])
            )
        else:
            parameters["stop_token_ids"] = model_config["stop_token_ids"]

    tgi_payload = {
        "inputs": formatted_prompt,
        "parameters": parameters
    }

    # === 转发请求到 TGI ===
    async with httpx.AsyncClient(timeout=CLIENT_TIMEOUT) as client:
        try:
            resp = await client.post(f"{model_config['endpoint']}/generate", json=tgi_payload)
            resp.raise_for_status()
            result = resp.json()
            generated_text = result.get("generated_text", "").strip()

            latency = time.time() - start_time
            output_tokens = len(generated_text.split())

            # === 日志：成功响应 ===
            logger.info(
                f"[{request_id}] Success | model={model_id} | "
                f"output_tokens={output_tokens} | latency={latency:.2f}s"
            )

            return {
                "generated_text": generated_text,
                "model": model_config["name"],
                "tokens": output_tokens
            }

        except httpx.TimeoutException as e:
            latency = time.time() - start_time
            logger.error(f"[{request_id}] Timeout | model={model_id} | latency={latency:.2f}s")
            raise HTTPException(
                status_code=504,
                detail={
                    "error": "Timeout",
                    "error_code": "INFERENCE_TIMEOUT",
                    "details": f"Inference took longer than {CLIENT_TIMEOUT.read}s"
                }
            )

        except httpx.RequestError as e:
            logger.error(f"[{request_id}] RequestError | model={model_id} | error={str(e)}")
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "ServiceUnreachable",
                    "error_code": "DOWNSTREAM_REQUEST_FAILED",
                    "details": str(e)
                }
            )

        except httpx.HTTPStatusError as e:
            err_detail = resp.text if 'resp' in locals() else str(e)
            logger.error(f"[{request_id}] HTTPError | model={model_id} | status={resp.status_code} | {err_detail}")
            raise HTTPException(
                status_code=resp.status_code,
                detail={
                    "error": "ModelError",
                    "error_code": "TGI_SERVER_ERROR",
                    "details": err_detail
                }
            )
