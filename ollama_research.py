#!/usr/bin/env python3
"""
Ollama Research System for local-deep-researcher
Complete local research using Ollama models
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OllamaResearcher:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "deepseek-r1:8b")
        self.verify_connection()
    
    def verify_connection(self) -> bool:
        """Verify Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Connected to Ollama at {self.ollama_url}")
                
                # Check available models
                model_names = [m['name'] for m in models.get('models', [])]
                if model_names:
                    print(f"📦 Available models: {', '.join(model_names)}")
                    
                    # Check if our model is available
                    if self.model not in model_names:
                        print(f"⚠️  Model {self.model} not found. Pulling it now...")
                        self.pull_model(self.model)
                else:
                    print(f"⚠️  No models found. Pulling {self.model}...")
                    self.pull_model(self.model)
                
                return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to Ollama at {self.ollama_url}")
            print(f"Please ensure Ollama is running:")
            print(f"  sudo systemctl start ollama")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def pull_model(self, model_name: str):
        """Pull a model if it's not available"""
        print(f"📥 Pulling model {model_name}... This may take a few minutes...")
        try:
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        print(f"  {data['status']}", end='\r')
            print(f"\n✅ Model {model_name} pulled successfully!")
        except Exception as e:
            print(f"❌ Failed to pull model: {e}")
    
    def query_ollama(self, prompt: str) -> str:
        """Send a query to Ollama and get response"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": float(os.getenv("TEMPERATURE", 0.7)),
                        "num_ctx": int(os.getenv("NUM_CTX", 8192)),
                        "num_predict": int(os.getenv("MAX_TOKENS", 4096))
                    }
                },
                timeout=int(os.getenv("REQUEST_TIMEOUT", 120))
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                print(f"❌ Error from Ollama: {response.status_code}")
                return ""
        except Exception as e:
            print(f"❌ Error querying Ollama: {e}")
            return ""
    
    def search_web(self, query: str) -> List[Dict]:
        """Search the web using DuckDuckGo"""
        try:
            from duckduckgo_search import DDGS
            
            print(f"🔎 Searching for: {query}")
            ddgs = DDGS()
            results = list(ddgs.text(
                query, 
                max_results=int(os.getenv("MAX_SEARCH_RESULTS", 10))
            ))
            return results
        except Exception as e:
            print(f"⚠️  Search error: {e}")
            return []
    
    def iterative_research(self, topic: str) -> str:
        """Perform iterative deep research"""
        research_context = []
        search_queries = []
        
        # Generate initial search queries
        print("\n📋 Generating research queries...")
        query_prompt = f"""Generate 3-5 specific search queries to research the topic: "{topic}"
        
        Return only the queries, one per line, no numbering or bullets."""
        
        queries_response = self.query_ollama(query_prompt)
        initial_queries = [q.strip() for q in queries_response.split('\n') if q.strip()][:5]
        
        if not initial_queries:
            initial_queries = [topic]
        
        search_queries.extend(initial_queries)
        
        # Iterative research loop
        max_iterations = int(os.getenv("MAX_ITERATIONS", 5))
        for iteration in range(max_iterations):
            print(f"\n🔄 Research iteration {iteration + 1}/{max_iterations}")
            
            if iteration < len(search_queries):
                query = search_queries[iteration]
                
                # Search the web
                search_results = self.search_web(query)
                
                if search_results:
                    # Summarize search results
                    results_text = "\n\n".join([
                        f"Title: {r.get('title', 'No title')}\n"
                        f"Content: {r.get('body', '')[:500]}...\n"
                        f"Source: {r.get('href', '')}"
                        for r in search_results[:5]
                    ])
                    
                    # Extract key insights
                    print("💭 Analyzing search results...")
                    analysis_prompt = f"""Analyze these search results about "{topic}":

{results_text}

Provide:
1. Key findings (3-5 bullet points)
2. Important facts discovered
3. Areas that need more research

Be concise and factual."""
                    
                    analysis = self.query_ollama(analysis_prompt)
                    research_context.append({
                        'query': query,
                        'iteration': iteration + 1,
                        'findings': analysis,
                        'sources': [r.get('href', '') for r in search_results[:5]]
                    })
                    
                    # Generate follow-up queries if needed
                    if iteration < max_iterations - 1:
                        followup_prompt = f"""Based on this research about "{topic}":

{analysis}

What specific question should we research next to deepen our understanding?
Provide only one specific search query."""
                        
                        followup = self.query_ollama(followup_prompt).strip()
                        if followup and followup not in search_queries:
                            search_queries.append(followup)
                            print(f"📌 Next query: {followup}")
        
        # Generate final comprehensive report
        print("\n📝 Generating comprehensive research report...")
        
        context_summary = "\n\n".join([
            f"**Iteration {ctx['iteration']} - Query: {ctx['query']}**\n{ctx['findings']}"
            for ctx in research_context
        ])
        
        report_prompt = f"""Create a comprehensive research report on: "{topic}"

Based on this iterative research:

{context_summary}

Structure the report with:

# {topic}

## Executive Summary
[Provide a concise overview of the key findings]

## Introduction
[Brief introduction to the topic]

## Key Findings
[Detailed findings organized by themes]

## Analysis
[In-depth analysis of the research]

## Implications
[What this means and why it matters]

## Conclusions
[Summary and final thoughts]

## Areas for Further Research
[Topics that warrant additional investigation]

## Sources
[List the main sources used]

Use markdown formatting. Be comprehensive yet concise."""
        
        final_report = self.query_ollama(report_prompt)
        
        # Add sources appendix
        all_sources = []
        for ctx in research_context:
            all_sources.extend(ctx.get('sources', []))
        
        unique_sources = list(set(filter(None, all_sources)))
        
        if unique_sources:
            final_report += "\n\n---\n\n## References\n\n"
            for i, source in enumerate(unique_sources, 1):
                final_report += f"{i}. {source}\n"
        
        return final_report
    
    def run_research(self, topic: str):
        """Execute the research process"""
        if not self.verify_connection():
            print("\n💡 To start Ollama:")
            print("   sudo systemctl start ollama")
            print("   ollama pull deepseek-r1:8b")
            sys.exit(1)
        
        print(f"\n🔬 Starting deep research on: {topic}")
        print(f"🤖 Using model: {self.model}")
        print(f"🔄 Max iterations: {os.getenv('MAX_ITERATIONS', 5)}")
        
        # Create output directory
        output_dir = Path(os.getenv("RESEARCH_OUTPUT_DIR", "./research_output"))
        output_dir.mkdir(exist_ok=True)
        
        # Perform research
        result = self.iterative_research(topic)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        output_file = output_dir / f"{safe_topic}_{timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Research Report: {topic}\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {self.model}\n")
            f.write(f"**Iterations:** {os.getenv('MAX_ITERATIONS', 5)}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"\n✅ Research completed!")
        print(f"📄 Results saved to: {output_file}")
        
        # Display preview
        print("\n📖 Report Preview:")
        print("=" * 50)
        lines = result.split('\n')[:20]
        print('\n'.join(lines))
        if len(result.split('\n')) > 20:
            print("\n... [Full report saved to file]")
        
        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Ollama Deep Research System")
        print("=" * 40)
        print("\nUsage: python ollama_research.py 'Your research topic'")
        print("\nExample topics:")
        print("  - 'Latest developments in quantum computing'")
        print("  - 'Security best practices for Fedora 42'")
        print("  - 'How to optimize neural networks for edge devices'")
        print("  - 'Impact of AI on cybersecurity'")
        print("\nCurrent configuration:")
        print(f"  Model: {os.getenv('OLLAMA_MODEL', 'deepseek-r1:8b')}")
        print(f"  Max iterations: {os.getenv('MAX_ITERATIONS', 5)}")
        print(f"  Search engine: {os.getenv('SEARCH_ENGINE', 'duckduckgo')}")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    researcher = OllamaResearcher()
    researcher.run_research(topic)