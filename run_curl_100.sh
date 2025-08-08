#!/usr/bin/env bash
set -euo pipefail

export URL=http://localhost:8000/v1/generate

# 固定 payload（收敛变量；如需更重，调大 max_new_tokens / inputs）
body='{
  "model_id": "qwen2",
  "inputs": "请用三句话介绍人工智能。",
  "scenario": "base",
  "parameters": {"max_new_tokens": 256, "temperature": 0.7, "top_p": 0.9, "do_sample": true}
}'

USERS=100
MODE=fixed           # fixed=固定2s；random=1.5~2.5s
RUNTIME_SEC=300      # 跑10分钟；需要时改长
MIN_WAIT=1.5
MAX_WAIT=2.5

rand_sleep() {
  # 1.5~2.5 随机秒
  python3 - <<PY
import random,time; print(f"{random.uniform($MIN_WAIT,$MAX_WAIT):.3f}")
PY
}

logger() { # 采样线程：写CSV
  while true; do
    out=$(curl -s -D - -o /dev/null \
          -H 'Content-Type: application/json' \
          -d "$body" \
          -w "X-Curl-Time-Total: %{time_total}\nX-Curl-Http-Code: %{http_code}\n" \
          "$URL" | tr -d '\r')
    ts=$(date -Is)
    e2e=$(printf "%s" "$out" | awk 'tolower($1)=="x-curl-time-total:"{print $2}')
    code=$(printf "%s" "$out" | awk 'tolower($1)=="x-curl-http-code:"{print $2}')
    gw=$(printf  "%s" "$out" | awk 'tolower($1)=="x-gateway-latency:"{print $2}')
    rid=$(printf "%s" "$out" | awk 'tolower($1)=="x-request-id:"{print $2}')
    printf "%s,%s,%s,%s,%s\n" "$ts" "$e2e" "$code" "$gw" "$rid" >> curl_probe.csv
    [ "$MODE" = fixed ] && sleep 2 || sleep "$(rand_sleep)"
  done
}

worker() { # 载荷线程
  while true; do
    curl -s -o /dev/null -H 'Content-Type: application/json' -d "$body" "$URL"
    [ "$MODE" = fixed ] && sleep 2 || sleep "$(rand_sleep)"
  done
}

trap 'pkill -P $$ || true' INT TERM
: > curl_probe.csv
logger &                             # 1 条采样
for i in $(seq 2 $USERS); do worker & done  # 其余作为载荷
sleep "$RUNTIME_SEC"

