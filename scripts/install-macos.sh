#!/usr/bin/env bash
# One-command NutriMe install for macOS (issue #34).
#
#   ./scripts/install-macos.sh            # install + start at login
#   ./scripts/install-macos.sh --no-autostart
#   ./scripts/install-macos.sh --uninstall   # remove the login agent; data stays
#
# Installs what's missing (Homebrew packages ollama + uv), sets up
# NutriMe, downloads the local model, copies the bundled recipe
# collection, vets it, takes a first backup and registers a launchd
# agent. Safe to run again: every step skips work that's already done.
set -euo pipefail

MODEL="${NUTRIME_MODEL:-qwen3:8b}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${NUTRIME_DATA_DIR:-$HOME/.nutrime}"
LABEL="dev.nutrime.serve"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CRAWL_LABEL="dev.nutrime.crawl"
CRAWL_PLIST="$HOME/Library/LaunchAgents/$CRAWL_LABEL.plist"
AUTOSTART=1

step() { printf '\n==> %s\n' "$1"; }

case "${1:-}" in
  --uninstall)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    launchctl bootout "gui/$(id -u)/$CRAWL_LABEL" 2>/dev/null || true
    rm -f "$PLIST" "$CRAWL_PLIST"
    echo "Removed the login and weekly-crawl agents. Your data in $DATA_DIR is untouched."
    exit 0 ;;
  --no-autostart) AUTOSTART=0 ;;
  "") ;;
  *) echo "unknown option: $1" >&2; exit 2 ;;
esac

[ -f "$REPO/pyproject.toml" ] || { echo "Run this from the NutriMe folder." >&2; exit 1; }

step "Checking for Homebrew"
command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh" >&2; exit 1; }

step "Checking for Ollama and uv"
command -v ollama >/dev/null || brew install ollama
command -v uv >/dev/null || brew install uv
brew services start ollama >/dev/null 2>&1 || true

cd "$REPO"
step "Installing NutriMe"
uv sync --no-dev

step "Creating your data folder at $DATA_DIR"
uv run --no-dev nutrime init --data-dir "$DATA_DIR" >/dev/null

if ! ls "$DATA_DIR/corpus/recipes/"*.md >/dev/null 2>&1; then
  step "Copying the bundled recipe collection"
  mkdir -p "$DATA_DIR/corpus/recipes"
  cp -R "$REPO/corpus/recipes/." "$DATA_DIR/corpus/recipes/"
fi

step "Checking recipes (vetting)"
uv run --no-dev nutrime recipes vet --data-dir "$DATA_DIR"

step "Downloading the local model $MODEL (several GB, one time)"
ollama pull "$MODEL" || echo "Model download didn't finish. Run 'ollama pull $MODEL' later; everything except plan-making works without it."

step "Taking a first backup"
uv run --no-dev nutrime backup --data-dir "$DATA_DIR"

if [ "$AUTOSTART" = 1 ]; then
  step "Starting NutriMe at login"
  UV="$(command -v uv)"
  mkdir -p "$HOME/Library/LaunchAgents" "$DATA_DIR/logs"
  cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$UV</string><string>run</string><string>--no-dev</string><string>--directory</string><string>$REPO</string>
    <string>nutrime</string><string>serve</string><string>--data-dir</string><string>$DATA_DIR</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$DATA_DIR/logs/serve.log</string>
  <key>StandardErrorPath</key><string>$DATA_DIR/logs/serve.log</string>
</dict>
</plist>
PLISTEOF
  launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$PLIST"

  step "Collecting new recipes weekly (Sunday 3 am; sites' robots.txt decides)"
  cat > "$CRAWL_PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$CRAWL_LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>$UV</string><string>run</string><string>--no-dev</string><string>--directory</string><string>$REPO</string>
    <string>nutrime</string><string>recipes</string><string>crawl</string><string>--data-dir</string><string>$DATA_DIR</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>StartCalendarInterval</key><dict><key>Weekday</key><integer>0</integer><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>$DATA_DIR/logs/crawl.log</string>
  <key>StandardErrorPath</key><string>$DATA_DIR/logs/crawl.log</string>
</dict>
</plist>
PLISTEOF
  launchctl bootout "gui/$(id -u)/$CRAWL_LABEL" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$CRAWL_PLIST"
fi

step "Checking everything"
uv run --no-dev nutrime doctor --data-dir "$DATA_DIR" || true

printf '\nDone. Open http://localhost:8765 in your browser.\n'
