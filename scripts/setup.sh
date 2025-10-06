#!/bin/bash
# AgentAru Setup Script

set -e

echo "🤖 Setting up AgentAru..."
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python $python_version"
echo

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
echo "✅ Virtual environment created"
echo

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"
echo

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/vector_db data/memory data/cache logs
echo "✅ Directories created"
echo

# Setup environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env with your API keys"
else
    echo "✅ .env file already exists"
fi
echo

# Download embedding model (optional)
read -p "Download sentence transformer model? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading embedding model..."
    python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
    echo "✅ Embedding model downloaded"
fi

echo
echo "✅ Setup complete!"
echo
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. (Optional) Add Gmail credentials.json for email features"
echo "3. Run: source .venv/bin/activate"
echo "4. Run CLI: python src/main.py"
echo "5. Run UI: streamlit run src/ui/streamlit_app.py"
echo
