#!/bin/bash
# scripts/start-tgi-llama3.sh

docker run --rm \
  --gpus all \
  --shm-size 1g \
  -p 8081:80 \
  -v $PWD/models/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4:/data \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id /data \
  --quantize gptq \
  --max-input-length 2048 \
  --max-total-tokens 4096 \
  --trust-remote-code
