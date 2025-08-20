#!/bin/bash

echo "🦙 Starting Ollama Research Environment"
echo "======================================"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "Please run: sudo /home/ice/install_ollama.sh"
    exit 1
fi

# Check if Ollama service is running
if ! systemctl is-active --quiet ollama; then
    echo "🚀 Starting Ollama service..."
    sudo systemctl start ollama
    sleep 2
fi

# Verify Ollama is responding
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not responding"
    echo "Try: sudo systemctl restart ollama"
    exit 1
fi

# Show available models
echo ""
echo "📦 Available models:"
ollama list

# Check if recommended model is installed
if ! ollama list | grep -q "deepseek-r1:8b"; then
    echo ""
    echo "⚠️  Recommended model 'deepseek-r1:8b' not found"
    echo "Pulling it now (this may take a few minutes)..."
    ollama pull deepseek-r1:8b
fi

# Activate Python environment
cd /home/ice/local-deep-researcher
source venv/bin/activate

echo ""
echo "✅ Research environment ready!"
echo "======================================"
echo ""
echo "Usage:"
echo "  python ollama_research.py 'Your research topic'"
echo ""
echo "Examples:"
echo "  python ollama_research.py 'Quantum computing breakthroughs 2025'"
echo "  python ollama_research.py 'Fedora 42 security hardening'"
echo "  python ollama_research.py 'Local LLM optimization techniques'"
echo ""
echo "Or use interactive mode:"
echo "  ./ollama_research_cli.sh"
echo ""