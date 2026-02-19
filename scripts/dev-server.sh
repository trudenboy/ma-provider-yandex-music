#!/usr/bin/env bash
# dev-server.sh — run MA in an isolated git worktree with live provider code
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROVIDER_DIR="$SCRIPT_DIR/../provider"
PROVIDER_DOMAIN=$(python3 -c "import json; print(json.load(open('$PROVIDER_DIR/manifest.json'))['domain'])")

# ---------- Find fork repository ----------
find_ma_repo() {
  [[ -n "${MA_SERVER_REPO:-}" ]] && { realpath "$MA_SERVER_REPO"; return; }
  local override="$SCRIPT_DIR/../ma-server.repo"
  [[ -f "$override" ]] && { realpath "$(cat "$override")"; return; }
  for candidate in \
    "$SCRIPT_DIR/../../ma-server" \
    "$HOME/Projects/ma-server" \
    "$HOME/src/ma-server" \
    "$HOME/dev/ma-server"; do
    [[ -d "$candidate/.git" ]] && { realpath "$candidate"; return; }
  done
  echo "ERROR: ma-server repo not found." >&2
  echo "  Set MA_SERVER_REPO=/path/to/repo, or create ma-server.repo file." >&2
  exit 1
}

MA_REPO=$(find_ma_repo)
MA_BRANCH="${MA_DEV_BRANCH:-dev}"

echo "→ Provider : $PROVIDER_DOMAIN"
echo "→ MA repo  : $MA_REPO  (branch: $MA_BRANCH)"

# ---------- Create isolated worktree ----------
WORKTREE=$(mktemp -d "${TMPDIR:-/tmp}/ma-dev-${PROVIDER_DOMAIN}-XXXXXX")

cleanup() {
  echo -e "\n→ Removing worktree: $WORKTREE"
  git -C "$MA_REPO" worktree remove --force "$WORKTREE" 2>/dev/null || true
  rm -rf "$WORKTREE"
}
trap cleanup EXIT INT TERM

git -C "$MA_REPO" worktree add --detach "$WORKTREE" "$MA_BRANCH" -q
echo "→ Worktree : $WORKTREE"

# ---------- Symlink provider ----------
rm -rf "$WORKTREE/music_assistant/providers/$PROVIDER_DOMAIN"
ln -s "$(realpath "$PROVIDER_DIR")" "$WORKTREE/music_assistant/providers/$PROVIDER_DOMAIN"
echo "→ Linked   : providers/$PROVIDER_DOMAIN → $PROVIDER_DIR"

# ---------- Venv in worktree (reuses uv cache) ----------
uv venv "$WORKTREE/.venv" --python 3.13 -q
uv pip install --python "$WORKTREE/.venv/bin/python" \
   "$WORKTREE[test]" -r "$WORKTREE/requirements_all.txt" -q 2>&1 | tail -2

# ---------- Run MA ----------
DATA_DIR="${MA_DEV_DATA:-$HOME/.musicassistant-dev-$PROVIDER_DOMAIN}"
mkdir -p "$DATA_DIR"
echo "→ Data dir : $DATA_DIR"
echo "→ UI at    : http://localhost:8095"
echo ""

"$WORKTREE/.venv/bin/python" -m music_assistant \
  --data-dir "$DATA_DIR" \
  --cache-dir "$DATA_DIR/.cache" \
  --log-level "${LOG_LEVEL:-debug}"
