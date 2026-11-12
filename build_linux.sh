#!/usr/bin/env bash
set -e

# Directory where script resides
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " Building Standalone Linux Binary for Kali Linux GNOME"
echo "=========================================================="

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found."
    exit 1
fi

# Ensure virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv --system-site-packages .venv
fi

echo "[2/3] Installing dependencies..."
.venv/bin/pip install -q pyinstaller numpy

echo "[3/3] Compiling with PyInstaller..."
.venv/bin/pyinstaller --clean --noconfirm rose_disc.spec

echo "=========================================================="
if [ -f "dist/rose_disc" ]; then
    chmod +x dist/rose_disc
    echo "SUCCESS: Standalone Linux binary created at:"
    echo "         $SCRIPT_DIR/dist/rose_disc"
    echo ""
    echo "To test run:"
    echo "  ./dist/rose_disc"
    echo "  ./dist/rose_disc --cli --frames 30"
    echo "=========================================================="
else
    echo "Error: Output binary not found in dist/"
    exit 1
fi
