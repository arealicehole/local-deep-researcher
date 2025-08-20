# Local Deep Research Setup

A completely local, private deep research system using LM Studio and local LLMs.

## 🚀 Quick Start

```bash
./quick_start.sh
```

This will guide you through the entire setup process.

## 📁 Directory Structure

```
/home/ice/
├── lm-studio/                 # LM Studio installation
│   ├── lmstudio.AppImage     # LM Studio application
│   └── download_lmstudio.sh  # Download helper script
│
└── local-deep-researcher/     # Research system
    ├── venv/                  # Python virtual environment
    ├── .env                   # Configuration
    ├── lmstudio_research.py   # Main research script
    ├── research_cli.sh        # Interactive CLI
    ├── start_research_environment.sh  # Environment starter
    ├── quick_start.sh         # Setup wizard
    └── research_output/       # Research results directory
```

## 🔧 Configuration

Edit `.env` file to customize:

- `MAX_ITERATIONS`: Number of research iterations (default: 5)
- `MAX_TOKENS`: Maximum tokens per response (default: 4096)
- `TEMPERATURE`: Model temperature (default: 0.7)
- `SEARCH_ENGINE`: Search provider (default: duckduckgo)

## 💻 Usage

### Interactive Research Mode
```bash
cd /home/ice/local-deep-researcher
./research_cli.sh
```

### Command Line Research
```bash
cd /home/ice/local-deep-researcher
source venv/bin/activate
python lmstudio_research.py "Your research topic here"
```

### Examples
```bash
python lmstudio_research.py "Impact of quantum computing on cryptography"
python lmstudio_research.py "Best security practices for Fedora 42"
python lmstudio_research.py "Optimizing LLMs for local inference"
```

## 🎯 Recommended Models for 16GB VRAM

1. **DeepSeek-R1-Distill-Qwen-7B** (Q4_K_M) - Best for research
2. **Qwen2.5-7B-Instruct** (Q4_K_M) - Fast and capable
3. **Mistral-7B-Instruct-v0.3** (Q5_K_M) - Good balance
4. **Llama-3.2-8B-Instruct** (Q4_K_M) - Strong general performance

## 🔒 Privacy Features

- ✅ 100% local processing
- ✅ No external API dependencies
- ✅ All data stays on your machine
- ✅ DuckDuckGo for private web search
- ✅ No telemetry or tracking

## 🛠️ Troubleshooting

### LM Studio not connecting
1. Ensure LM Studio is running
2. Check that a model is loaded
3. Verify local server is started on port 1234
4. Run: `curl http://localhost:1234/v1/models`

### Python issues
```bash
cd /home/ice/local-deep-researcher
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install langchain langchain-community langchain-openai duckduckgo-search beautifulsoup4 requests httpx python-dotenv markdown
```

### GPU not being used
Check NVIDIA drivers:
```bash
nvidia-smi
```

In LM Studio settings:
- Set GPU Layers to "Max"
- Enable "Keep model loaded"
- Set appropriate context length (8192 or 16384)

## 📊 System Requirements

- **OS**: Fedora 42
- **GPU**: RTX 5060 Ti (16GB VRAM)
- **Python**: 3.11+
- **Disk Space**: ~20GB for models
- **RAM**: 16GB+ recommended

## 🔄 Updates

To update the research system:
```bash
cd /home/ice/local-deep-researcher
git pull
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 📝 Research Output

All research results are saved to:
```
/home/ice/local-deep-researcher/research_output/
```

Files are named with format:
```
[topic]_[timestamp].md
```

## 🎨 Customization

You can modify `lmstudio_research.py` to:
- Add custom research templates
- Integrate additional data sources
- Modify output formats
- Add citation management
- Implement research workflows

## 💡 Tips

1. **Model Selection**: Start with Q4_K_M quantization for best speed/quality balance
2. **Context Length**: Use 8192 for faster responses, 16384 for deeper research
3. **Temperature**: Lower (0.3) for factual research, higher (0.7) for creative exploration
4. **Iterations**: More iterations = deeper research but longer processing time

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review LM Studio documentation
3. Verify all dependencies are installed
4. Check system resources (GPU memory, disk space)

---

Built for privacy-focused deep research on Fedora 42 🐧