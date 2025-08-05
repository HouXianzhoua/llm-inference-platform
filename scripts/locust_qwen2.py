# locust_qwen2.py - 专用于 Qwen2 模型的多场景压力测试
from locust import HttpUser, task, between
class Qwen2User(HttpUser):
    # 每1秒发起一次请求，模拟持续流量
    wait_time = between(1.5, 2.5)

    # 定义不同场景的权重，模拟真实流量分布
    SCENARIO_WEIGHTS = [
        ("base", 0.4),      # 40% 的请求是普通对话
        ("qa", 0.3),        # 30% 的请求是问答
        ("summarize", 0.2), # 20% 的请求是摘要
        ("rewrite", 0.1)    # 10% 的请求是改写
    ]

    @task
    def generate(self):
        # 根据权重随机选择一个场景
        scenarios, weights = zip(*self.SCENARIO_WEIGHTS)
        chosen_scenario = self.random_choice_weighted(scenarios, weights)

        # 为不同场景准备不同的输入（模拟真实用户行为）
        inputs = {
            "base": "请用三句话介绍人工智能。",
            "qa": "量子纠缠是如何实现的？",
            "summarize": "机器学习是人工智能的一个分支，它通过算法使计算机能够从数据中学习并做出预测或决策，而无需进行明确的编程。监督学习、无监督学习和强化学习是其主要类型。",
            "rewrite": "这个产品非常好，大家都很喜欢，买了都说好。"
        }

        payload = {
            "model_id": "qwen2",  # 固定为 qwen2
            "inputs": inputs[chosen_scenario],
            "scenario": chosen_scenario,
            "parameters": {
                "max_new_tokens": 128,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        self.client.post("/v1/generate", json=payload)
    
    def random_choice_weighted(self, choices, weights):
        """根据权重随机选择"""
        import random
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for c, w in zip(choices, weights):
            if upto + w >= r:
                return c
            upto += w
