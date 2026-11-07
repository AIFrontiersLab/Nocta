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

echo "[FutureLab] Starting nightly experiment"
echo "[FutureLab] time=$STAMP"

# SharedRoute only — no direct Ollama / oMLX backends.
ROUTER_BASE="${OPENAI_BASE_URL:-http://10.0.0.27:8088/v1}"
ROUTER_ORIGIN="${ROUTER_BASE%/v1}"
export OPENAI_BASE_URL="$ROUTER_BASE"
export OPENAI_API_KEY="${OPENAI_API_KEY:-unused}"
export AI_MODEL="${AI_MODEL:-router}"
export AI_PROJECT="${AI_PROJECT:-VectraFutureLab}"

if curl -sf "${ROUTER_ORIGIN}/health" >/dev/null 2>&1; then
  echo "[FutureLab] SharedRoute ok: $ROUTER_BASE (project=$AI_PROJECT model=$AI_MODEL)"
else
  echo "warning: SharedRoute unreachable ($ROUTER_ORIGIN/health); run may use catalog scoring"
fi

set +e
# Use "$@" (not an empty array under set -u) so Hermes/cron with no extra args works.
LOG_FILE="$(mktemp "${TMPDIR:-/tmp}/futurelab-nightly.XXXXXX")"
RESULT="$("$PYTHON" -m app.cli run --mode auto --build --json "$@" 2>"$LOG_FILE")"
STATUS=$?
set -e

cat "$LOG_FILE" >&2
rm -f "$LOG_FILE"

if [[ -n "$RESULT" ]]; then
  echo "$RESULT"
fi

if [[ $STATUS -ne 0 ]]; then
  echo "[FutureLab] Failed with exit code $STATUS at $STAMP" >&2
  exit "$STATUS"
fi

echo "[FutureLab] Complete at $STAMP (builds up to DAILY_PROTOTYPE_COUNT GitHub repos when publish is enabled)" >&2
