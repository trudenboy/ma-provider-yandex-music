#!/usr/bin/env bash
# Mirrors MA server's scripts/setup.sh pattern
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v uv &>/dev/null; then
    echo "❌ uv not installed: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v ffmpeg &>/dev/null; then
    echo "⚠️  ffmpeg not found — required for MA integration tests"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt-get install ffmpeg"
fi

env_name=${1:-".venv"}
[[ -d "$env_name" ]] || uv venv "$env_name"
source "$env_name/bin/activate"

uv pip install -e ".[test]"

if command -v pre-commit &>/dev/null; then
    pre-commit install
fi

echo "✅ Done. $(python -V) | $(uv --version)"
echo "Re-run after pulling latest code (MA models version may change)."
