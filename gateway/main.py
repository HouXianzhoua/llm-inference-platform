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

@app.get("/v1/models")
async def list_models():
    return {
        "models": [
            {
                "id": k,
                "name": v["name"],
                "supports": ["completion", "instruct"]
            }
            for k, v in MODEL_REGISTRY.items()
        ]
    }

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
    except KeyError as e:
        raise HTTPException(500, f"Prompt template error: missing key {e}")
    except Exception as e:
        raise HTTPException(500, f"Failed to format prompt: {str(e)}")
    # 合并 stop tokens
    final_stop = set(model_config.get("stop", []))  # 来自 config.py 的默认 stop
    if "stop" in parameters:
        final_stop.update(parameters["stop"])       # 用户传入的 stop
    if final_stop:
        parameters["stop"] = list(final_stop)       # 写回 parameters
    # === 注入 stop_token_ids ===
    if "stop_token_ids" in model_config:
        if "stop_token_ids" in parameters:
            # 合并用户传入的 stop_token_ids
            parameters["stop_token_ids"] = list(
                set(parameters["stop_token_ids"]) | set(model_config["stop_token_ids"])
            )
        else:
            parameters["stop_token_ids"] = model_config["stop_token_ids"]
    # 构造 TGI 请求体
    tgi_payload = {
        "inputs": formatted_prompt,
        "parameters": parameters  # 完整透传
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
                "tokens": len(generated_text.split()),  # 简单估算，也可用 tokenizer
                "model_id": model_id
            }
        except httpx.TimeoutException:
            raise HTTPException(504, "Model inference timeout")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise HTTPException(503, f"Service unreachable: {str(e)}")
        except httpx.HTTPStatusError as e:
            err_detail = resp.text
            raise HTTPException(resp.status_code, f"Model error: {err_detail}")
