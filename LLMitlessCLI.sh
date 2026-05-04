#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
window_id=""

# ── dependency bootstrap ────────────────────────────────────────────────────
AUTO_INSTALL=$(python3 -c "
import json, sys
try:
    cfg = json.load(open('$SCRIPT_DIR/configuration.json'))
    print('true' if cfg.get('auto_install', True) else 'false')
except Exception:
    print('true')
" 2>/dev/null)

if [ "$AUTO_INSTALL" = "true" ]; then
    # Ensure python3 is present
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[bootstrap] Installing python3..."
        sudo apt-get install -y python3 python3-pip 2>/dev/null || \
        sudo dnf install -y python3 python3-pip 2>/dev/null || \
        sudo pacman -S --noconfirm python python-pip 2>/dev/null
    fi

    # Ensure pip is present
    if ! python3 -m pip --version >/dev/null 2>&1; then
        echo "[bootstrap] Installing pip..."
        sudo apt-get install -y python3-pip 2>/dev/null || \
        sudo dnf install -y python3-pip 2>/dev/null || \
        sudo pacman -S --noconfirm python-pip 2>/dev/null
    fi

    echo "[bootstrap] Checking Python dependencies..."
    python3 -m pip install --quiet --disable-pip-version-check \
        ollama ddgs requests 2>&1 | grep -v 'already satisfied' || true
fi
# ────────────────────────────────────────────────────────────────────────────

if command -v kdotool >/dev/null 2>&1; then
	window_id=$(kdotool search --name "~ : python3 — Konsole" 2>/dev/null | head -n 1)
fi

if [ -n "$window_id" ]; then
	kdotool windowactivate "$window_id"
else
	konsole -e "python3 \"$SCRIPT_DIR/LLMitlessCLI.py\""
fi
