#!/usr/bin/env bash
# Nightly Vectra FutureLab for Hermes
set -euo pipefail

ROOT="/Users/aiserver/Workspace_New/VectraFutureLab"
BACKEND="$ROOT/backend"
LOG_DIR="$ROOT/logs"
PYTHON="$BACKEND/.venv/bin/python"
STAMP="$(date '+%Y-%m-%d %H:%M %Z')"

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${HOME}/.local/bin:${PATH}"
export TZ="${TZ:-America/Los_Angeles}"
export PYTHONPATH="$BACKEND"

mkdir -p "$LOG_DIR"
cd "$BACKEND"

if [[ ! -x "$PYTHON" ]]; then
  echo "error: virtualenv missing at $PYTHON"
  echo "run: cd $BACKEND && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

ARGS=()
for arg in "$@"; do
  ARGS+=("$arg")
done

echo "[FutureLab] Starting nightly experiment"
echo "[FutureLab] time=$STAMP"

PRIMARY_OLLAMA="${OLLAMA_HOST:-http://10.0.0.25:11434}"
FALLBACK_OLLAMA="${OLLAMA_FALLBACK_HOST:-http://localhost:11434}"
FALLBACK_MODEL="${OLLAMA_FALLBACK_MODEL:-qwen3.5:latest}"
if curl -sf "${PRIMARY_OLLAMA}/api/tags" >/dev/null 2>&1; then
  export OLLAMA_HOST="$PRIMARY_OLLAMA"
  echo "[FutureLab] Ollama primary ok: $PRIMARY_OLLAMA"
elif curl -sf "${FALLBACK_OLLAMA}/api/tags" >/dev/null 2>&1; then
  export OLLAMA_HOST="$FALLBACK_OLLAMA"
  export LLM_BASE_URL="${FALLBACK_OLLAMA}/v1"
  export OLLAMA_FALLBACK_MODEL="$FALLBACK_MODEL"
  export OLLAMA_MODEL="$FALLBACK_MODEL"
  export LLM_FILTER_MODEL="$FALLBACK_MODEL"
  export LLM_REASONING_MODEL="$FALLBACK_MODEL"
  export LLM_CODING_MODEL="$FALLBACK_MODEL"
  export LLM_DEFAULT_MODEL="$FALLBACK_MODEL"
  echo "[FutureLab] Ollama primary failed ($PRIMARY_OLLAMA); falling back to $FALLBACK_OLLAMA with $FALLBACK_MODEL (all tiers)"
elif [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "warning: Ollama unreachable (primary + local fallback) and OPENAI_API_KEY not set; run may use catalog scoring"
fi

set +e
OUTPUT="$("$PYTHON" -m app.cli run --mode auto --build "${ARGS[@]}" 2>&1)"
STATUS=$?
set -e

echo "$OUTPUT"

if [[ $STATUS -ne 0 ]]; then
  echo "[FutureLab] Failed with exit code $STATUS at $STAMP" >&2
  exit "$STATUS"
fi

echo "[FutureLab] Complete at $STAMP (builds up to DAILY_PROTOTYPE_COUNT GitHub repos when publish is enabled)"
