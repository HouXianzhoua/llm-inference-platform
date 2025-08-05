# 临时测试脚本：test_template.py
from gateway.templates import TEMPLATES
from gateway.config import MODEL_REGISTRY

print("🔍 Testing Templates:")
for k, v in TEMPLATES.items():
    print(f"  {k}: {v[:50]}...")

print("\n🔍 Testing Config Model Registry:")
for mid, cfg in MODEL_REGISTRY.items():
    try:
        example = cfg["prompt_template"].format(input="Hello")
        print(f"✅ {mid} template works: {example[:60]}...")
    except Exception as e:
        print(f"❌ {mid} template error: {e}")
