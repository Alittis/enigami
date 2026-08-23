#!/usr/bin/env bash
# Write the Anthropic API key into enigami's gitignored .env.
# Re-runnable: press Enter at a prompt to keep the current value.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$REPO_ROOT/.env"
cd "$REPO_ROOT"

# Refuse to write anywhere git would track.
if ! git check-ignore -q "$ENV_FILE" 2>/dev/null; then
  echo "REFUSING: $ENV_FILE is not gitignored. Add '.env' to .gitignore first." >&2
  exit 1
fi

touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

upsert() {                       # upsert KEY VALUE
  local key="$1" val="$2" tmp
  tmp="$(mktemp)"
  grep -v "^${key}=" "$ENV_FILE" > "$tmp" 2>/dev/null || true
  printf '%s=%s\n' "$key" "$val" >> "$tmp"
  mv "$tmp" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
}

current() { grep "^$1=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true; }

CUR="$(current ANTHROPIC_API_KEY)"
if [ -n "$CUR" ]; then
  echo "ANTHROPIC_API_KEY is currently set (${#CUR} chars, ends ...${CUR: -4})."
  echo "Press Enter to keep it, or paste a new key to replace it."
else
  echo "ANTHROPIC_API_KEY is not set. Paste your key from https://console.anthropic.com/settings/keys"
fi

read -rs -p "ANTHROPIC_API_KEY: " KEY; echo
if [ -n "$KEY" ]; then
  case "$KEY" in
    sk-ant-*) ;;
    *) echo "WARNING: that does not start with 'sk-ant-'. Writing it anyway." >&2 ;;
  esac
  upsert ANTHROPIC_API_KEY "$KEY"
  echo "Wrote ANTHROPIC_API_KEY to $ENV_FILE (mode 600)."
elif [ -n "$CUR" ]; then
  echo "Kept existing ANTHROPIC_API_KEY."
else
  echo "No key entered and none stored — enigami will not be able to call the API." >&2
  exit 1
fi

echo
echo "Verify with:  uv run enigami doctor"
