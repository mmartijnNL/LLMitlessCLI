#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
window_id=""

# ── ensure a sane PATH ───────────────────────────────────────────────────────
# Source Homebrew environment (critical on Bazzite/immutable where brew manages tools)
for _brew_prefix in /home/linuxbrew/.linuxbrew /usr/local /opt/homebrew; do
    if [ -x "$_brew_prefix/bin/brew" ]; then
        eval "$("$_brew_prefix/bin/brew" shellenv 2>/dev/null)"
        break
    fi
done
# Ensure common install locations are in PATH
export PATH="/usr/local/bin:/usr/bin:/bin:$HOME/.local/bin:$PATH"
# ────────────────────────────────────────────────────────────────────────────

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
    # Detect immutable OS (Bazzite / Silverblue / Kinoite / etc.)
    _IMMUTABLE=false
    if grep -qiE "bazzite|silverblue|kinoite|ostree" /etc/os-release 2>/dev/null; then
        _IMMUTABLE=true
    fi

    # Helper: install a package using the right package manager
    _pkg_install() {
        local pkg="$1"
        local brew_pkg="${2:-$1}"   # optional alternate brew formula name
        if [ "$_IMMUTABLE" = "true" ] && command -v brew >/dev/null 2>&1; then
            brew install "$brew_pkg"
        else
            sudo apt-get install -y "$pkg" 2>/dev/null || \
            sudo dnf install -y "$pkg" 2>/dev/null || \
            sudo pacman -S --noconfirm "$pkg" 2>/dev/null || \
            (command -v brew >/dev/null 2>&1 && brew install "$brew_pkg")
        fi
    }

    # Ensure python3 is present
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[bootstrap] Installing python3..."
        _pkg_install python3 python
    fi

    # Ensure pip is present
    if ! python3 -m pip --version >/dev/null 2>&1; then
        echo "[bootstrap] Installing pip..."
        _pkg_install python3-pip python
    fi

    echo "[bootstrap] Checking Python dependencies..."
    python3 -m pip install --quiet --disable-pip-version-check \
        ollama ddgs requests 2>&1 | grep -v 'already satisfied' || true

    # Ensure ollama is installed
    if ! command -v ollama >/dev/null 2>&1; then
        echo "[bootstrap] Installing ollama..."
        if command -v brew >/dev/null 2>&1; then
            brew install ollama
        else
            curl -fsSL https://ollama.com/install.sh | sh
        fi
    fi

    # Ensure ollama is installed as a systemd service and running
    if command -v ollama >/dev/null 2>&1; then
        OLLAMA_BIN="$(command -v ollama)"

        # Write a user-level systemd unit if no system unit exists
        if ! systemctl list-unit-files ollama.service &>/dev/null 2>&1 && \
           ! systemctl --user list-unit-files ollama.service &>/dev/null 2>&1; then
            echo "[bootstrap] Registering ollama as a systemd user service..."
            mkdir -p "$HOME/.config/systemd/user"
            cat > "$HOME/.config/systemd/user/ollama.service" <<EOF
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=${OLLAMA_BIN} serve
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
EOF
            systemctl --user daemon-reload
        fi

        # Prefer user service on immutable OS; fall back to system service
        if [ "$_IMMUTABLE" = "true" ] || systemctl --user list-unit-files ollama.service &>/dev/null 2>&1; then
            if ! systemctl --user is-enabled --quiet ollama 2>/dev/null; then
                echo "[bootstrap] Enabling ollama user service..."
                systemctl --user enable ollama
            fi
            if ! systemctl --user is-active --quiet ollama 2>/dev/null; then
                echo "[bootstrap] Starting ollama user service..."
                systemctl --user start ollama
            fi
        else
            if ! systemctl is-enabled --quiet ollama 2>/dev/null; then
                echo "[bootstrap] Enabling ollama system service..."
                sudo systemctl enable ollama
            fi
            if ! systemctl is-active --quiet ollama 2>/dev/null; then
                echo "[bootstrap] Starting ollama system service..."
                sudo systemctl start ollama
            fi
        fi

        # Wait up to 15 s for the API to become ready
        for _ in $(seq 1 15); do
            curl -sf http://localhost:11434 >/dev/null 2>&1 && break
            sleep 1
        done

        # Pull gemma4 if no models are present
        if [ -z "$(ollama list 2>/dev/null | tail -n +2)" ]; then
            echo "[bootstrap] No models found. Pulling gemma4..."
            ollama pull gemma4
        fi
    fi

    # Ensure kdotool is present (needed for Konsole window detection on KDE/Wayland)
    if ! command -v kdotool >/dev/null 2>&1; then
        echo "[bootstrap] Installing kdotool..."
        _pkg_install kdotool kdotool || \
        echo "[bootstrap] WARNING: kdotool not found. Install manually: https://github.com/jinliu/kdotool"
    fi
fi
# ────────────────────────────────────────────────────────────────────────────

if command -v kdotool >/dev/null 2>&1; then
	window_id=$(kdotool search --name " : python3 — Konsole" 2>/dev/null | head -n 1)
fi

if [ -n "$window_id" ]; then
	kdotool windowactivate "$window_id"
else
	konsole -e bash -c "cd \"$(dirname "$SCRIPT_DIR")\" && python3 -m LLMitlessCLI"
fi
