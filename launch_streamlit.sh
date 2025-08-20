#!/bin/bash

# Launch script for Streamlit Local Deep Researcher UI

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 Local Deep Researcher - Streamlit UI${NC}"
echo "============================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}Streamlit not found. Installing...${NC}"
    pip install streamlit
fi

# Check if Ollama is running (optional)
if command -v ollama &> /dev/null; then
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Ollama is not running. Starting Ollama...${NC}"
        ollama serve > /dev/null 2>&1 &
        sleep 2
    else
        echo -e "${GREEN}✅ Ollama is running${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama not found. Make sure to install and start Ollama or use LMStudio${NC}"
fi

# Launch Streamlit
echo -e "${GREEN}🚀 Launching Streamlit UI...${NC}"
echo "============================================"
echo -e "${GREEN}Access the UI at: http://localhost:8501${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run Streamlit with custom configuration
streamlit run streamlit_app.py \
    --server.port 8501 \
    --server.address localhost \
    --server.headless true \
    --browser.gatherUsageStats false \
    --theme.primaryColor "#4CAF50" \
    --theme.backgroundColor "#ffffff" \
    --theme.secondaryBackgroundColor "#f0f2f6" \
    --theme.textColor "#262730"