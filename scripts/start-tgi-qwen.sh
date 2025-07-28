#!/bin/bash
# scripts/start-tgi-qwen.sh

docker run --rm \
  --gpus all \
  --shm-size 1g \
  -p 8080:80 \
  -v $PWD/models/Qwen2-7B-Instruct-GPTQ-Int4:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id /data \
  --quantize gptq \
  --max-input-length 2048 \
  --max-total-tokens 4096 \
  --trust-remote-code
