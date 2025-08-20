# 🔍 Streamlit UI for Local Deep Researcher

A beautiful, user-friendly web interface for conducting AI-powered research using local LLMs.

## 🚀 Quick Start

```bash
# Launch the Streamlit UI
./launch_streamlit.sh
```

Or manually:
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

Access the UI at: **http://localhost:8501**

## ✨ Features

### Core Functionality
- **🤖 Multi-Provider Support**: Works with both Ollama and LMStudio
- **🔍 Iterative Research**: Conducts deep, multi-iteration research
- **📊 Live Progress Tracking**: Real-time updates during research
- **💾 Research History**: Saves and recalls previous research sessions
- **📥 Export Options**: Download results as Markdown files
- **⚙️ Full Configuration**: Adjust all research parameters from the UI

### User Interface
- **Clean Design**: Modern, intuitive interface
- **Responsive Layout**: Works on desktop and tablet
- **Dark/Light Mode**: (Coming soon)
- **Real-time Status**: Live updates during research process
- **Error Handling**: Clear error messages and recovery options

## 🎯 How to Use

### 1. Initial Setup
1. Launch the app using `./launch_streamlit.sh`
2. The sidebar will show connection status to Ollama/LMStudio
3. If not connected, follow the instructions to start your LLM provider

### 2. Configure Settings
In the sidebar, you can configure:
- **LLM Provider**: Choose between Ollama or LMStudio
- **Model Selection**: Pick from available models
- **Research Depth**: Number of research iterations (1-10)
- **Search Engine**: DuckDuckGo, Tavily, Perplexity, or SearXNG
- **Temperature**: Control creativity (0.0-1.0)
- **Advanced Settings**: Token limits, context window, etc.

### 3. Start Research
1. Enter your research topic in the main input field
2. Click "🚀 Start Research"
3. Watch the progress bar and live updates
4. Results will appear below when complete

### 4. View & Export Results
- **View**: Results display in formatted Markdown
- **Download**: Click "📥 Download MD" to save results
- **History**: Access previous research from the sidebar
- **Sources**: Expand the sources section to see references

## 🔧 Configuration Options

### Environment Variables
Create or modify `.env` file:

```env
# LLM Provider Settings
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LMSTUDIO_BASE_URL=http://localhost:1234/v1

# Model Settings
OLLAMA_MODEL=llama3.2
LOCAL_LLM=llama3.2

# Research Settings
MAX_ITERATIONS=3
MAX_SEARCH_RESULTS=10
TEMPERATURE=0.7
MAX_TOKENS=4096
NUM_CTX=8192

# Search API
SEARCH_API=duckduckgo
TAVILY_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Output
RESEARCH_OUTPUT_DIR=./research_output
```

### Streamlit Configuration
The app uses custom theming for better aesthetics:
- Primary Color: Green (#4CAF50)
- Clean white background
- Responsive layout
- Custom CSS for enhanced UI elements

## 📊 Research Process

The app follows this workflow:

1. **Query Generation**: Creates targeted search queries
2. **Web Search**: Retrieves relevant information
3. **Analysis**: Processes and synthesizes findings
4. **Iteration**: Refines search based on gaps
5. **Report Generation**: Creates comprehensive markdown report
6. **Source Attribution**: Includes all references

## 🛠️ Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Pull a model
ollama pull llama3.2
```

### LMStudio Connection Issues
1. Open LMStudio application
2. Load a model
3. Start the local server (usually on port 1234)
4. Verify in the UI sidebar

### Streamlit Issues
```bash
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit

# Clear cache
streamlit cache clear

# Run with debug mode
streamlit run streamlit_app.py --logger.level=debug
```

## 🎨 Customization

### Modify UI Theme
Edit the launch script or create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#4CAF50"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Add Custom Features
The `streamlit_app.py` is modular and easy to extend:
- Add new research providers
- Implement custom export formats
- Create visualization components
- Add authentication

## 🔒 Privacy & Security

- **100% Local**: All processing happens on your machine
- **No Data Sharing**: No telemetry or external API calls (except optional search APIs)
- **Secure Storage**: Research history stored locally
- **API Key Protection**: Keys stored in environment variables

## 📈 Performance Tips

1. **Model Selection**: Use quantized models (Q4_K_M) for speed
2. **Iteration Count**: Start with 3 iterations, increase for depth
3. **Context Window**: Balance between 8192-16384 for best results
4. **Temperature**: Use 0.3-0.5 for factual research, 0.7+ for creative

## 🚧 Upcoming Features

- [ ] WebSocket support for real-time streaming
- [ ] Multi-language support
- [ ] PDF export option
- [ ] Research templates
- [ ] Collaborative research sessions
- [ ] Citation management
- [ ] Graph visualizations
- [ ] Voice input support

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with Streamlit
- Powered by LangGraph and LangChain
- Local LLM support via Ollama and LMStudio
- Search capabilities from DuckDuckGo and others

---

**Happy Researching! 🔍✨**