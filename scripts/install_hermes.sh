#!/usr/bin/env bash
set -euo pipefail

ROOT="/Users/aiserver/Workspace_New/VectraFutureLab"
HERMES_HOME_DIR="${HERMES_HOME:-$HOME/.hermes}"
SCRIPTS_DIR="$HERMES_HOME_DIR/scripts"
WRAPPER="$SCRIPTS_DIR/futurelab-nightly.sh"
JOB_NAME="Vectra FutureLab"

if [[ ! -x "$ROOT/backend/.venv/bin/python" ]]; then
  echo "Virtualenv missing. Create it first:"
  echo "  cd $ROOT/backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

mkdir -p "$SCRIPTS_DIR"
chmod +x "$ROOT/scripts/futurelab-nightly.sh"

cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$ROOT"
exec "$ROOT/scripts/futurelab-nightly.sh" "\$@"
EOF
chmod +x "$WRAPPER"

echo "Hermes wrapper installed: $WRAPPER"

if ! command -v hermes >/dev/null 2>&1; then
  echo "hermes is not on PATH; wrapper is installed but cron job was not created."
  echo "Manual run: $WRAPPER"
  exit 0
fi

if hermes cron list 2>/dev/null | grep -q "$JOB_NAME"; then
  echo "Cron job already exists: $JOB_NAME"
else
  hermes cron create "30 22 * * *" \
    --no-agent \
    --script "futurelab-nightly.sh" \
    --deliver local \
    --name "$JOB_NAME" \
    --workdir "$ROOT"
  echo "Created Hermes cron job: $JOB_NAME (30 22 * * * — nightly at 10:30 PM)"
fi

echo
echo "Verify:"
echo "  hermes cron list"
echo "  hermes cron run \"$JOB_NAME\""
echo "  $WRAPPER"
