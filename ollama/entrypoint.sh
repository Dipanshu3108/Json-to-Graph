#!/bin/sh
set -e

MODEL_NAME="${OLLAMA_MODEL_PULL:-deepseek-coder:latest}"
MAX_PULL_RETRIES="${OLLAMA_PULL_RETRIES:-5}"

echo "Starting Ollama server..."
# Redirect noisy server logs away from Docker compose output; readiness is checked below.
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!

# Wait for the API to become ready
until ollama list >/dev/null 2>&1; do
  echo "Waiting for Ollama API..."
  sleep 2
done

# Pull the requested model if it is not already present
if ! ollama list | grep -q "^${MODEL_NAME%%:*}"; then
  echo "Pulling model ${MODEL_NAME}..."

  attempt=0
  while [ "$attempt" -lt "$MAX_PULL_RETRIES" ]; do
    attempt=$((attempt + 1))
    echo "Pull attempt ${attempt}/${MAX_PULL_RETRIES}..."
    if ollama pull "${MODEL_NAME}"; then
      echo "Model ${MODEL_NAME} pulled successfully."
      break
    fi
    echo "Pull failed, retrying in 10s..."
    sleep 10
  done

  if [ "$attempt" -eq "$MAX_PULL_RETRIES" ]; then
    echo "ERROR: Failed to pull ${MODEL_NAME} after ${MAX_PULL_RETRIES} attempts."
    exit 1
  fi
else
  echo "Model ${MODEL_NAME} already available."
fi

# Keep the server in the foreground
wait "$OLLAMA_PID"
