# locust_llama3.py - 专用于 Llama3 模型的多场景压力测试
from locust import HttpUser, task, between
class Llama3User(HttpUser):
    wait_time = between(1.5,2.5)

    # Llama3 使用相同的场景权重
    SCENARIO_WEIGHTS = [
        ("base", 0.4),
        ("qa", 0.3),
        ("summarize", 0.2),
        ("rewrite", 0.1)
    ]

    @task
    def generate(self):
        chosen_scenario = self.random_choice_weighted(
            [s for s, w in self.SCENARIO_WEIGHTS], 
            [w for s, w in self.SCENARIO_WEIGHTS]
        )

        inputs = {
            "base": "请用三句话介绍人工智能。",
            "qa": "量子纠缠是如何实现的？",
            "summarize": "机器学习是人工智能的一个分支，它通过算法使计算机能够从数据中学习并做出预测或决策，而无需进行明确的编程。监督学习、无监督学习和强化学习是其主要类型。",
            "rewrite": "这个产品非常好，大家都很喜欢，买了都说好。"
        }

        payload = {
            "model_id": "llama3",  # 固定为 llama3
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
        import random
        total = sum(weights)
        r = random.uniform(0, total)
        upto = 0
        for c, w in zip(choices, weights):
            if upto + w >= r:
                return c
            upto += w
