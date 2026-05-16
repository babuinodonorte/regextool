#!/bin/bash
# Regex Tool — uninstaller

INSTALL_PATH="/usr/local/bin/regextool"

echo "╔══════════════════════════════════════╗"
echo "║     REGEX TOOL — Desinstalador       ║"
echo "╚══════════════════════════════════════╝"
echo ""

if [ ! -f "$INSTALL_PATH" ]; then
    echo "[INFO] regextool não está instalado em $INSTALL_PATH"
    exit 0
fi

sudo rm "$INSTALL_PATH"
echo "[OK] Regex Tool removido com sucesso."
