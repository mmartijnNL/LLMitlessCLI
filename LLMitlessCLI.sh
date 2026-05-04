#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
window_id=""

if command -v kdotool >/dev/null 2>&1; then
	window_id=$(kdotool search --name "~ : python3 — Konsole" 2>/dev/null | head -n 1)
fi

if [ -n "$window_id" ]; then
	kdotool windowactivate "$window_id"
else
	konsole -e "python3 \"$SCRIPT_DIR/os_agent.py\" &"
fi
