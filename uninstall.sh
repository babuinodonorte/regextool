#!/bin/bash
# Regex Tool — uninstaller

INSTALL_PATH="/usr/local/bin/regextool"

echo "╔══════════════════════════════════════╗"
echo "║     REGEX TOOL — Uninstaller         ║"
echo "╚══════════════════════════════════════╝"
echo ""

if [ ! -f "$INSTALL_PATH" ]; then
    echo "[INFO] regextool is not installed at $INSTALL_PATH"
    exit 0
fi

sudo rm "$INSTALL_PATH"
echo "[OK] Regex Tool removed successfully."
