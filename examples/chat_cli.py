# examples/chat_cli.py
"""
简易命令行聊天界面，支持多轮对话与模型切换
"""
import requests
import sys

BASE_URL = "http://localhost:8000/v1/generate"
HISTORY = []

def chat_loop():
    print("💬 欢迎使用多模型聊天 CLI！")
    print("可用命令：/model qwen2|llama3  /quit  /clear")
    print("-" * 50)

    model_id = "qwen2"
    while True:
        try:
            user_input = input(f"\n👤 ({model_id}) > ").strip()
            if not user_input:
                continue

            # 命令处理
            if user_input.startswith("/model "):
                new_model = user_input.split()[-1]
                if new_model in ["qwen2", "llama3"]:
                    model_id = new_model
                    print(f"🔄 模型已切换为: {model_id}")
                else:
                    print("❌ 不支持的模型，仅支持 qwen2 或 llama3")
                continue

            if user_input == "/quit":
                print("👋 再见！")
                break

            if user_input == "/clear":
                global HISTORY
                HISTORY = []
                print("🧹 对话历史已清空")
                continue

            # 构造上下文（简单拼接）
            context = "\n".join(HISTORY[-4:]) + "\n" + user_input  # 最近4轮

            payload = {
                "model_id": model_id,
                "inputs": context,
                "scenario": "base",
                "parameters": {
                    "max_new_tokens": 256,
                    "temperature": 0.8,
                    "top_p": 0.9
                }
            }

            response = requests.post(BASE_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            reply = result["generated_text"].strip()

            print(f"\n🤖 {reply}")

            # 更新历史
            HISTORY.append(f"用户: {user_input}")
            HISTORY.append(f"助手: {reply}")

        except KeyboardInterrupt:
            print("\n\n👋 检测到 Ctrl+C，退出中...")
            break
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
        except EOFError:
            break

if __name__ == "__main__":
    chat_loop()
