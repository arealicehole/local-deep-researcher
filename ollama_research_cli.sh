#!/bin/bash

# Ollama Interactive Research CLI
cd /home/ice/local-deep-researcher
source venv/bin/activate

clear
echo "╔══════════════════════════════════════════════════╗"
echo "║    🦙 Ollama Deep Research System 🔬             ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check Ollama connection
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama: Connected"
    
    # Show loaded model
    current_model=$(grep "OLLAMA_MODEL=" .env | cut -d'=' -f2)
    echo "🤖 Model: $current_model"
    
    # Check if model exists
    if ollama list | grep -q "$current_model"; then
        echo "✅ Model ready"
    else
        echo "⚠️  Model not found, pulling..."
        ollama pull $current_model
    fi
else
    echo "❌ Ollama: Not running"
    echo ""
    echo "Starting Ollama..."
    sudo systemctl start ollama
    sleep 3
    
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama started successfully"
    else
        echo "❌ Failed to start Ollama"
        echo "Try: sudo systemctl status ollama"
        exit 1
    fi
fi

echo ""
echo "Available commands:"
echo "  Type your research topic and press Enter"
echo "  'models' - List available models"
echo "  'switch' - Switch to a different model"
echo "  'config' - Show current configuration"
echo "  'quit'   - Exit"
echo ""
echo "Example topics:"
echo "  • Impact of quantum computing on encryption"
echo "  • Best practices for Linux system security"
echo "  • Latest developments in renewable energy"
echo ""
echo "────────────────────────────────────────────────────"

while true; do
    echo ""
    read -p "Research Topic > " input
    
    if [ "$input" = "quit" ] || [ "$input" = "exit" ] || [ "$input" = "q" ]; then
        echo "Goodbye! 👋"
        break
    elif [ "$input" = "models" ]; then
        echo ""
        echo "Available models:"
        ollama list
    elif [ "$input" = "switch" ]; then
        echo ""
        echo "Available models:"
        ollama list | tail -n +2 | awk '{print NR". "$1}'
        echo ""
        read -p "Enter model name: " new_model
        if [ -n "$new_model" ]; then
            sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$new_model/" .env
            echo "✅ Switched to model: $new_model"
        fi
    elif [ "$input" = "config" ]; then
        echo ""
        echo "Current Configuration:"
        echo "────────────────────────────"
        grep -E "^(OLLAMA_MODEL|MAX_ITERATIONS|MAX_TOKENS|TEMPERATURE)" .env | sed 's/^/  /'
    elif [ -n "$input" ]; then
        echo ""
        echo "🔬 Starting research on: $input"
        echo "════════════════════════════════════════════════════"
        python ollama_research.py "$input"
        echo ""
        echo "════════════════════════════════════════════════════"
        echo ""
        echo "Research complete! Check ./research_output/ for full report."
    fi
done