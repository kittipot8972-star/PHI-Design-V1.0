#!/bin/bash
# ────────────────────────────────────────────────
# PHI Assembly API — Start Script
# วิธีใช้: bash start.sh
# ────────────────────────────────────────────────
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "======================================"
echo "  PHI Integration Design — Assembler"
echo "======================================"

# Check Python
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 not found. กรุณาติดตั้ง Python 3.10+"
  exit 1
fi

# Install deps if needed
if ! python3 -c "import cadquery" 2>/dev/null; then
  echo "📦  Installing dependencies..."
  pip install -r "$DIR/assembler/requirements.txt" --break-system-packages -q
fi

# Create folders
mkdir -p "$DIR/models/solenoid" "$DIR/models/manifold" "$DIR/models/blanking"
mkdir -p "$DIR/previews" "$DIR/output"

PORT=${PORT:-5050}
echo ""
echo "🚀  Starting API on http://localhost:$PORT"
echo "   /health          → ตรวจสอบสถานะ"
echo "   /api/assemble    → สร้าง Assembly STEP (sync)"
echo "   /api/assemble-async → สร้าง Assembly STEP (async)"
echo ""
echo "⚠️   STEP จาก SMC: วางไว้ใน models/solenoid/, models/manifold/"
echo "    ระบบจะใช้ parametric geometry ถ้าไม่มีไฟล์จริง"
echo ""
echo "Press Ctrl+C to stop"
echo "--------------------------------------"

cd "$DIR"
PORT=$PORT python3 assembler/api.py
