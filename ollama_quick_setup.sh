#!/bin/bash

echo "╔══════════════════════════════════════════════════╗"
echo "║   🚀 Ollama Research Quick Setup Wizard 🚀      ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if Ollama is installed
echo "Step 1: Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    ollama version
else
    echo "❌ Ollama not found"
    echo ""
    echo "Installing Ollama now..."
    echo "You'll need to enter your sudo password:"
    curl -fsSL https://ollama.com/install.sh | sudo sh
    
    if command -v ollama &> /dev/null; then
        echo "✅ Ollama installed successfully!"
    else
        echo "❌ Installation failed. Please run manually:"
        echo "   sudo /home/ice/install_ollama.sh"
        exit 1
    fi
fi

# Step 2: Start Ollama service
echo ""
echo "Step 2: Starting Ollama service..."
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service is already running"
else
    echo "Starting Ollama service..."
    sudo systemctl enable ollama
    sudo systemctl start ollama
    sleep 2
    
    if systemctl is-active --quiet ollama; then
        echo "✅ Ollama service started"
    else
        echo "❌ Failed to start Ollama service"
        exit 1
    fi
fi

# Step 3: Check GPU
echo ""
echo "Step 3: Checking GPU..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU detected:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
else
    echo "⚠️  NVIDIA GPU tools not found"
    echo "GPU acceleration may not be available"
fi

# Step 4: Pull recommended model
echo ""
echo "Step 4: Checking models..."
if ollama list | grep -q "deepseek-r1:8b"; then
    echo "✅ DeepSeek-R1:8b model is already installed"
else
    echo "📥 Pulling DeepSeek-R1:8b model..."
    echo "This is optimized for research and fits in 16GB VRAM"
    echo "This may take 5-10 minutes..."
    ollama pull deepseek-r1:8b
    echo "✅ Model downloaded"
fi

# Step 5: Check Python environment
echo ""
echo "Step 5: Checking Python environment..."
cd /home/ice/local-deep-researcher

if [ -d "venv" ]; then
    echo "✅ Python virtual environment exists"
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Check if packages are installed
if python -c "import langchain" 2>/dev/null; then
    echo "✅ Python packages are installed"
else
    echo "Installing Python packages..."
    pip install --upgrade pip
    pip install langchain langchain-community langchain-openai duckduckgo-search beautifulsoup4 requests httpx python-dotenv markdown
    echo "✅ Packages installed"
fi

# Step 6: Test the setup
echo ""
echo "Step 6: Testing the setup..."
python3 -c "
import requests
import os
from dotenv import load_dotenv

load_dotenv()

try:
    # Test Ollama connection
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    if r.status_code == 200:
        print('✅ Ollama API is accessible')
        models = r.json().get('models', [])
        if models:
            print(f'✅ Models available: {len(models)}')
            for m in models[:3]:
                print(f'   - {m.get(\"name\")}')
        
        # Test a simple query
        print('\\n🧪 Testing model response...')
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'deepseek-r1:8b',
                'prompt': 'Say hello in one sentence.',
                'stream': False
            },
            timeout=30
        )
        if response.status_code == 200:
            print('✅ Model is responding correctly')
        else:
            print('⚠️  Model test failed')
    else:
        print('❌ Cannot connect to Ollama')
except Exception as e:
    print(f'❌ Error: {e}')
"

# Step 7: Create aliases
echo ""
echo "Step 7: Setting up convenient aliases..."
cat > ~/.ollama_research_aliases << 'EOF'
# Ollama Research Aliases
alias research='cd /home/ice/local-deep-researcher && source venv/bin/activate && python ollama_research.py'
alias research-chat='cd /home/ice/local-deep-researcher && ./ollama_research_cli.sh'
alias research-start='cd /home/ice/local-deep-researcher && ./start_ollama_research.sh'
alias ollama-models='ollama list'
alias ollama-pull='ollama pull'
alias research-output='ls -la /home/ice/local-deep-researcher/research_output/'
EOF

echo "To activate aliases, add this to your ~/.bashrc:"
echo "  echo 'source ~/.ollama_research_aliases' >> ~/.bashrc"
echo "  source ~/.bashrc"

# Final message
echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║         🎉 Setup Complete! 🎉                   ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "You can now run research with:"
echo ""
echo "1. Quick research:"
echo "   cd /home/ice/local-deep-researcher"
echo "   source venv/bin/activate"
echo "   python ollama_research.py 'Your topic here'"
echo ""
echo "2. Interactive mode:"
echo "   cd /home/ice/local-deep-researcher"
echo "   ./ollama_research_cli.sh"
echo ""
echo "3. After setting up aliases:"
echo "   research 'Your topic here'"
echo "   research-chat"
echo ""
echo "Research outputs saved to:"
echo "  /home/ice/local-deep-researcher/research_output/"
echo ""
echo "Enjoy your private, local deep research system! 🔬"