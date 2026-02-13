#!/bin/bash
# 100 Times AI Heroes - Ollama版 初期化スクリプト
# M4 MacBook Pro (128GB) 向け

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "======================================"
echo "100 Times AI Heroes - Ollama Setup"
echo "======================================"

# 1. Ollama確認
echo ""
echo "[1/6] Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "ERROR: Ollama not found. Install with: brew install ollama"
    exit 1
fi
echo "  OK: Ollama installed"

# 2. Ollamaサーバー確認
echo ""
echo "[2/6] Checking Ollama server..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "  Starting Ollama server..."
    ollama serve &
    sleep 3
fi
echo "  OK: Ollama server running"

# 3. モデル確認
echo ""
echo "[3/6] Checking model (gpt-oss-20b)..."
MODEL="gpt-oss-20b"
if ! ollama list | grep -q "$MODEL"; then
    echo "  Pulling $MODEL (this may take a while)..."
    ollama pull "$MODEL"
fi
echo "  OK: $MODEL available"

# 4. Python環境確認
echo ""
echo "[4/6] Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "  OK: Python $PYTHON_VERSION"

# 5. 依存パッケージインストール
echo ""
echo "[5/6] Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -q -r requirements.txt
    echo "  OK: Dependencies installed"
else
    echo "  SKIP: requirements.txt not found"
fi

# 6. 環境変数確認
echo ""
echo "[6/6] Checking configuration..."
if [ ! -f ".env" ]; then
    echo "  Creating .env from template..."
    cat > .env << 'EOF'
OLLAMA_MODEL=gpt-oss-20b
OLLAMA_HOST=http://localhost:11434
SHEET_URL=<your-spreadsheet-url>
CREDENTIALS_PATH=./credentials.json
EOF
    echo "  WARNING: Edit .env and set SHEET_URL"
else
    echo "  OK: .env exists"
fi

if [ ! -f "credentials.json" ]; then
    echo "  WARNING: credentials.json not found"
    echo "  See docs/DESIGN_SPEC_OLLAMA.md section 7.3 for setup"
else
    echo "  OK: credentials.json exists"
fi

# 完了
echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and set SHEET_URL"
echo "  2. Add credentials.json (Google service account)"
echo "  3. Run: python3 ollama_hero_gen.py"
echo ""
