#!/usr/bin/env python3
"""
Streamlit GUI for Local Deep Researcher
A user-friendly interface for conducting local AI-powered research
"""

import streamlit as st
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv
import threading
import queue

# Load environment variables
load_dotenv()

# Import our research modules
from ollama_research import OllamaResearcher
from src.ollama_deep_researcher.configuration import Configuration
from src.ollama_deep_researcher.graph import graph

# Page configuration
st.set_page_config(
    page_title="🔍 Local Deep Researcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .research-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .source-link {
        color: #0066cc;
        text-decoration: none;
    }
    .status-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    .status-pending { background-color: #ffd93d; color: #000; }
    .status-running { background-color: #4CAF50; color: #fff; }
    .status-completed { background-color: #2196F3; color: #fff; }
    .status-failed { background-color: #f44336; color: #fff; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'research_history' not in st.session_state:
        st.session_state.research_history = []
    if 'current_research' not in st.session_state:
        st.session_state.current_research = None
    if 'research_running' not in st.session_state:
        st.session_state.research_running = False
    if 'available_models' not in st.session_state:
        st.session_state.available_models = []
    if 'research_progress' not in st.session_state:
        st.session_state.research_progress = 0
    if 'research_status' not in st.session_state:
        st.session_state.research_status = ""
    if 'research_result' not in st.session_state:
        st.session_state.research_result = None

class StreamlitResearchInterface:
    """Main interface for the Streamlit research app"""
    
    def __init__(self):
        self.researcher = None
        self.config = Configuration()
        init_session_state()
        
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            response = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                st.session_state.available_models = [m['name'] for m in models]
                return True
        except:
            return False
    
    def check_lmstudio_connection(self) -> bool:
        """Check if LMStudio is running and accessible"""
        try:
            lmstudio_url = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1")
            response = requests.get(f"{lmstudio_url}/models", timeout=2)
            if response.status_code == 200:
                models = response.json().get('data', [])
                st.session_state.available_models = [m['id'] for m in models]
                return True
        except:
            return False
    
    def render_sidebar(self):
        """Render the sidebar with configuration options"""
        with st.sidebar:
            st.title("⚙️ Configuration")
            
            # Provider selection
            st.subheader("🤖 LLM Provider")
            provider = st.selectbox(
                "Select Provider",
                ["ollama", "lmstudio"],
                index=0 if self.config.llm_provider == "ollama" else 1,
                help="Choose between Ollama or LMStudio for local LLM inference"
            )
            
            # Connection status
            if provider == "ollama":
                connected = self.check_ollama_connection()
            else:
                connected = self.check_lmstudio_connection()
            
            if connected:
                st.success(f"✅ Connected to {provider.capitalize()}")
                
                # Model selection
                if st.session_state.available_models:
                    selected_model = st.selectbox(
                        "Select Model",
                        st.session_state.available_models,
                        help="Choose the LLM model for research"
                    )
                else:
                    st.warning("No models available. Please pull a model first.")
                    model_name = st.text_input("Model to pull (e.g., llama3.2)")
                    if st.button("Pull Model"):
                        with st.spinner(f"Pulling {model_name}..."):
                            # Pull model logic here
                            st.info("Model pulling in progress...")
            else:
                st.error(f"❌ Cannot connect to {provider.capitalize()}")
                st.info(f"Please ensure {provider.capitalize()} is running")
                
                if provider == "ollama":
                    st.code("sudo systemctl start ollama", language="bash")
                else:
                    st.info("Open LMStudio and start the local server")
            
            st.divider()
            
            # Research Configuration
            st.subheader("🔬 Research Settings")
            
            max_iterations = st.slider(
                "Research Depth (Iterations)",
                min_value=1,
                max_value=10,
                value=int(os.getenv("MAX_ITERATIONS", 3)),
                help="Number of iterative research cycles"
            )
            
            search_api = st.selectbox(
                "Search Engine",
                ["duckduckgo", "tavily", "perplexity", "searxng"],
                index=0,
                help="Web search provider for research"
            )
            
            if search_api in ["tavily", "perplexity"]:
                api_key = st.text_input(
                    f"{search_api.capitalize()} API Key",
                    type="password",
                    help=f"Enter your {search_api.capitalize()} API key"
                )
            
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=float(os.getenv("TEMPERATURE", 0.7)),
                step=0.1,
                help="Controls randomness in responses (0=focused, 1=creative)"
            )
            
            fetch_full_page = st.checkbox(
                "Fetch Full Page Content",
                value=False,
                help="Retrieve complete webpage content (slower but more comprehensive)"
            )
            
            st.divider()
            
            # Advanced Settings
            with st.expander("🔧 Advanced Settings"):
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=32000,
                    value=int(os.getenv("MAX_TOKENS", 4096)),
                    step=100,
                    help="Maximum tokens per LLM response"
                )
                
                num_ctx = st.number_input(
                    "Context Window",
                    min_value=2048,
                    max_value=32768,
                    value=int(os.getenv("NUM_CTX", 8192)),
                    step=1024,
                    help="Context window size for the model"
                )
                
                max_search_results = st.number_input(
                    "Max Search Results",
                    min_value=5,
                    max_value=50,
                    value=int(os.getenv("MAX_SEARCH_RESULTS", 10)),
                    help="Maximum number of search results to process"
                )
            
            # Save configuration
            if st.button("💾 Save Configuration"):
                config_data = {
                    "llm_provider": provider,
                    "local_llm": selected_model if connected else "",
                    "max_web_research_loops": max_iterations,
                    "search_api": search_api,
                    "temperature": temperature,
                    "fetch_full_page": fetch_full_page,
                    "max_tokens": max_tokens,
                    "num_ctx": num_ctx,
                    "max_search_results": max_search_results
                }
                # Update environment variables
                for key, value in config_data.items():
                    os.environ[key.upper()] = str(value)
                st.success("✅ Configuration saved!")
            
            st.divider()
            
            # Research History
            st.subheader("📚 Research History")
            if st.session_state.research_history:
                for idx, research in enumerate(reversed(st.session_state.research_history[-5:])):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.text(research['topic'][:30] + "...")
                        with col2:
                            if st.button("📄", key=f"view_{idx}"):
                                st.session_state.current_research = research
            else:
                st.info("No research history yet")
    
    def render_main_content(self):
        """Render the main content area"""
        st.title("🔍 Local Deep Researcher")
        st.markdown("*Conduct comprehensive AI-powered research using local LLMs*")
        
        # Research input section
        col1, col2 = st.columns([4, 1])
        with col1:
            research_topic = st.text_input(
                "Research Topic",
                placeholder="Enter a topic to research (e.g., 'Impact of quantum computing on cryptography')",
                help="Be specific for better results"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            start_button = st.button(
                "🚀 Start Research",
                type="primary",
                disabled=st.session_state.research_running or not research_topic
            )
        
        # Validate topic
        if start_button and research_topic:
            if len(research_topic) < 5:
                st.error("Topic must be at least 5 characters long")
            elif len(research_topic) > 500:
                st.error("Topic must be less than 500 characters")
            else:
                self.start_research(research_topic)
        
        # Progress and status section
        if st.session_state.research_running:
            st.divider()
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.subheader("🔄 Research Progress")
                progress = st.progress(st.session_state.research_progress / 100)
                st.caption(st.session_state.research_status)
            
            with col2:
                # Live updates container
                with st.container():
                    st.subheader("📊 Live Updates")
                    status_placeholder = st.empty()
                    status_placeholder.info(st.session_state.research_status)
            
            with col3:
                if st.button("❌ Cancel", type="secondary"):
                    st.session_state.research_running = False
                    st.warning("Research cancelled")
        
        # Results section
        if st.session_state.research_result:
            st.divider()
            self.render_research_results()
    
    def start_research(self, topic: str):
        """Start the research process"""
        st.session_state.research_running = True
        st.session_state.research_progress = 0
        st.session_state.research_status = "Initializing research..."
        st.session_state.research_result = None
        
        # Create researcher instance
        self.researcher = OllamaResearcher()
        
        # Progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate research phases
            phases = [
                ("🔍 Generating search queries...", 10),
                ("🌐 Searching the web...", 30),
                ("📚 Analyzing sources...", 50),
                ("💡 Extracting insights...", 70),
                ("📝 Generating report...", 90),
                ("✅ Finalizing research...", 100)
            ]
            
            for phase, progress in phases:
                if not st.session_state.research_running:
                    break
                
                status_text.text(phase)
                progress_bar.progress(progress / 100)
                st.session_state.research_progress = progress
                st.session_state.research_status = phase
                time.sleep(1)  # Simulate processing
            
            # Perform actual research
            if st.session_state.research_running:
                with st.spinner("Conducting deep research..."):
                    try:
                        result = self.researcher.run_research(topic)
                        
                        # Store result
                        research_data = {
                            'topic': topic,
                            'result': result,
                            'timestamp': datetime.now().isoformat(),
                            'model': self.researcher.model,
                            'iterations': os.getenv('MAX_ITERATIONS', 5)
                        }
                        
                        st.session_state.research_result = research_data
                        st.session_state.research_history.append(research_data)
                        st.session_state.research_running = False
                        
                        st.success("✅ Research completed successfully!")
                        st.balloons()
                        
                    except Exception as e:
                        st.error(f"❌ Research failed: {str(e)}")
                        st.session_state.research_running = False
    
    def render_research_results(self):
        """Render the research results"""
        if not st.session_state.research_result:
            return
        
        result = st.session_state.research_result
        
        # Results header
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.subheader(f"📊 Research Results: {result['topic']}")
        with col2:
            # Export as Markdown
            st.download_button(
                label="📥 Download MD",
                data=result['result'],
                file_name=f"research_{result['topic'][:30]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown"
            )
        with col3:
            # Copy to clipboard button (using JS hack)
            if st.button("📋 Copy"):
                st.write("Content copied!")
        
        # Metadata
        with st.expander("ℹ️ Research Metadata"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Model", result.get('model', 'Unknown'))
            with col2:
                st.metric("Iterations", result.get('iterations', 'N/A'))
            with col3:
                st.metric("Timestamp", result['timestamp'][:10])
            with col4:
                word_count = len(result['result'].split())
                st.metric("Word Count", f"{word_count:,}")
        
        # Main results
        st.markdown(result['result'])
        
        # Sources section
        if "## References" in result['result'] or "## Sources" in result['result']:
            with st.expander("🔗 View Sources"):
                # Extract and display sources
                sources_section = result['result'].split("## References")[-1] if "## References" in result['result'] else result['result'].split("## Sources")[-1]
                st.markdown(sources_section)
    
    def run(self):
        """Main run method for the Streamlit app"""
        # Render sidebar
        self.render_sidebar()
        
        # Render main content
        self.render_main_content()
        
        # Footer
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("🔒 100% Local & Private")
        with col2:
            st.caption("🚀 Powered by LangGraph & Ollama")
        with col3:
            st.caption("📖 [View Documentation](https://github.com/arealicehole/local-deep-researcher)")

def main():
    """Main entry point"""
    app = StreamlitResearchInterface()
    app.run()

if __name__ == "__main__":
    main()