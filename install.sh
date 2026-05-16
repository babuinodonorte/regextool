#!/bin/bash
# Regex Tool — installer

set -e

INSTALL_PATH="/usr/local/bin/regextool"
SCRIPT_NAME="regex_tool.py"

echo "╔══════════════════════════════════════╗"
echo "║     REGEX TOOL — Instalador          ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Verifica Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado."
    echo "       Instale com: sudo apt install python3"
    exit 1
fi

# Verifica tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "[INFO] python3-tk não encontrado. Instalando..."
    sudo apt-get install -y python3-tk
fi

# Verifica se o script existe no diretório atual
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "[ERRO] Arquivo $SCRIPT_NAME não encontrado no diretório atual."
    echo "       Execute o instalador de dentro do repositório clonado."
    exit 1
fi

# Copia e torna executável
sudo cp "$SCRIPT_NAME" "$INSTALL_PATH"
sudo chmod +x "$INSTALL_PATH"

# Adiciona shebang se não tiver
if ! head -1 "$INSTALL_PATH" | grep -q "^#!"; then
    sudo sed -i '1s/^/#!/usr/bin\/env python3\n/' "$INSTALL_PATH"
fi

echo ""
echo "[OK] Regex Tool instalado com sucesso."
echo "     Execute: regextool"
