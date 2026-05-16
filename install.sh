#!/bin/bash
# Regex Tool — installer

set -e

INSTALL_PATH="/usr/local/bin/regextool"
SCRIPT_NAME="regex_tool.py"

echo "╔══════════════════════════════════════╗"
echo "║     REGEX TOOL — Installer           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found."
    echo "        Install it with: sudo apt install python3"
    exit 1
fi

# Check tkinter
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "[INFO] python3-tk not found. Installing..."
    sudo apt-get install -y python3-tk
fi

# Check script exists in current directory
if [ ! -f "$SCRIPT_NAME" ]; then
    echo "[ERROR] $SCRIPT_NAME not found in the current directory."
    echo "        Run the installer from inside the cloned repository."
    exit 1
fi

# Copy and make executable
sudo cp "$SCRIPT_NAME" "$INSTALL_PATH"
sudo chmod +x "$INSTALL_PATH"

echo ""
echo "[OK] Regex Tool installed successfully."
echo "     Run: regextool"
