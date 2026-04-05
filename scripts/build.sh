#!/bin/bash
# ChampCom Build & Launch Script (Linux/macOS)
set -e

echo "==============================="
echo "  ChampCom Build System"
echo "==============================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is required but not found."
    echo "Install: sudo apt install python3 python3-tk"
    exit 1
fi

# Check tkinter
python3 -c "import tkinter" 2>/dev/null || {
    echo "[ERROR] tkinter is not installed."
    echo "Install: sudo apt install python3-tk"
    exit 1
}

# Create directories
mkdir -p configs assets modules logs

echo "[OK] All dependencies satisfied."
echo "[OK] Launching ChampCom..."
echo ""

cd "$(dirname "$0")/.."
python3 main.py
