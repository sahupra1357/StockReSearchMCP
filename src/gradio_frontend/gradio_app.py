"""
Gradio Web Interface for Stock Research MCP Server

A user-friendly web interface to interact with the multi-agent stock research system.
"""

import gradio as gr
import asyncio
import logging
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import MCP server components
from stock_research_mcp.agents import MultiAgentOrchestrator
from stock_research_mcp.agents.streaming_builder import get_streaming_builder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockResearchGradioApp:
    """Gradio web interface for stock research."""
    
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.builder = get_streaming_builder()
        self.chroma_checked = False
        logger.info("Stock Research Gradio App initialized")
    
    async def check_and_build_chroma(self, progress=gr.Progress()):
        """Check if ChromaDB exists and build if needed."""
        if not self.chroma_checked:
            self.chroma_checked = True
            
            if not self.builder.is_chroma_db_built():
                logger.info("ChromaDB not found. Building...")
                progress(0, desc="Building ChromaDB index (first-time setup)...")
                
                build_messages = []
                build_messages.append("\n" + "=" * 80)
                build_messages.append("📦 FIRST-TIME SETUP: BUILDING CHROMADB INDEX")
                build_messages.append("=" * 80)
                build_messages.append("\nℹ️  This is a one-time setup. The database will be stored permanently.\n")
                
                i = 0
                async for progress_msg in self.builder.build_with_streaming():
                    build_messages.append(progress_msg)
                    i += 1
                    if i % 10 == 0:
                        progress(i / 8000, desc=f"Building ChromaDB: {i}/8000 companies processed")
                
                build_messages.append("\n" + "=" * 80)
                build_messages.append("✅ ChromaDB build complete!")
                build_messages.append("=" * 80 + "\n")
                
                return "\n".join(build_messages)
            else:
                logger.info("ChromaDB already exists")
                return "✅ ChromaDB database ready!"
        return ""
    
    async def analyze_sector_async(self, sector: str, progress=gr.Progress()):
        """Analyze a sector using the multi-agent system."""
        if not sector or not sector.strip():
            return "⚠️ Please enter a sector name (e.g., technology, healthcare, finance)"
        
        try:
            # Check and build ChromaDB if needed
            progress(0.1, desc="Checking ChromaDB...")
            build_output = await self.check_and_build_chroma(progress)
            
            # Run analysis
            progress(0.3, desc=f"Analyzing {sector} sector...")
            logger.info(f"Starting analysis for sector: {sector}")
            
            result = await self.orchestrator.process_sector_query(sector)
            
            if not result["success"]:
                error_msg = result.get("error", "Analysis failed")
                logger.error(f"Analysis failed: {error_msg}")
                return f"❌ Error: {error_msg}"
            
            progress(0.9, desc="Formatting results...")
            
            # Format results
            formatted_output = self.orchestrator.format_results(result)
            
            # Combine build output (if any) with analysis results
            if build_output:
                return build_output + "\n\n" + formatted_output
            else:
                return formatted_output
                
        except Exception as e:
            logger.error(f"Error in analysis: {e}", exc_info=True)
            return f"❌ Error: {str(e)}"
    
    def analyze_sector(self, sector: str, progress=gr.Progress()):
        """Synchronous wrapper for async analysis."""
        return asyncio.run(self.analyze_sector_async(sector, progress))
    
    def get_example_sectors(self) -> List[List[str]]:
        """Get example sectors for quick testing."""
        return [
            ["technology"],
            ["healthcare"],
            ["finance"],
            ["energy"],
            ["biotechnology"],
            ["semiconductors"],
            ["renewable energy"],
            ["artificial intelligence"],
            ["e-commerce"],
            ["pharmaceuticals"]
        ]
    
    def get_database_status(self) -> str:
        """Check ChromaDB database status."""
        try:
            if self.builder.is_chroma_db_built():
                persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./output/chroma_db")
                return f"✅ ChromaDB is ready\n📂 Location: {persist_dir}"
            else:
                return "⚠️ ChromaDB not built yet. It will be built automatically on your first analysis."
        except Exception as e:
            return f"❌ Error checking database: {str(e)}"
    
    def build_interface(self) -> gr.Blocks:
        """Build the Gradio interface."""
        
        with gr.Blocks(
            title="Stock Research MCP Server"
        ) as interface:
            
            gr.Markdown(
                """
                # 📊 Stock Research Multi-Agent System
                
                Comprehensive stock analysis powered by a multi-agent architecture with ChromaDB semantic search.
                
                ### How it works:
                1. **Search Agent** - Finds stocks in your sector using ChromaDB semantic search on SEC filings
                2. **Categorization Agent** - Groups stocks by price (High: >$100, Medium: $10-$100, Low: <$10)
                3. **Analysis Agent** - Provides detailed analysis with news, events, and recommendations
                
                ### Features:
                - 🔍 **Semantic Search**: Query any industry using natural language
                - 📈 **Real-time Data**: Live stock prices from Yahoo Finance
                - 📰 **News & Events**: Latest market information
                - 💡 **AI Recommendations**: Investment insights for each stock
                """
            )
            
            with gr.Row():
                with gr.Column(scale=2):
                    sector_input = gr.Textbox(
                        label="Enter Sector or Industry",
                        placeholder="e.g., technology, biotechnology, semiconductors, renewable energy...",
                        lines=1
                    )
                    
                    with gr.Row():
                        analyze_btn = gr.Button("🔍 Analyze Sector", variant="primary", size="lg")
                        clear_btn = gr.ClearButton([sector_input], value="Clear", size="lg")
                    
                    gr.Markdown("### 💡 Example Sectors")
                    gr.Examples(
                        examples=self.get_example_sectors(),
                        inputs=sector_input,
                        label="Click to try:"
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### ℹ️ Quick Info")
                    
                    db_status = gr.Textbox(
                        label="Database Status",
                        value=self.get_database_status(),
                        interactive=False,
                        lines=3
                    )
                    
                    refresh_db_btn = gr.Button("🔄 Refresh Status", size="sm")
                    refresh_db_btn.click(
                        fn=self.get_database_status,
                        outputs=db_status
                    )
                    
                    gr.Markdown(
                        """
                        ### 📋 Tips:
                        - Be specific with sector names
                        - First query may take 20-40 mins (one-time ChromaDB build)
                        - Subsequent queries are instant
                        - Try natural language: "AI companies", "electric vehicles", etc.
                        """
                    )
            
            gr.Markdown("---")
            
            output_text = gr.Textbox(
                label="Analysis Results",
                lines=30,
                max_lines=50,
                interactive=False
            )
            
            analyze_btn.click(
                fn=self.analyze_sector,
                inputs=sector_input,
                outputs=output_text
            )
            
            gr.Markdown(
                """
                ---
                ### 🔧 Technical Details
                
                **Architecture:**
                - Multi-agent orchestrator coordinates three specialized agents
                - ChromaDB for semantic search on SEC filing data
                - OpenAI embeddings for text similarity
                - Yahoo Finance API for real-time stock data
                
                **Data Sources:**
                - SEC EDGAR filings (10-K, 20-F, S-1, 10-Q)
                - Yahoo Finance (real-time prices, company info)
                - ChromaDB vector database (8000+ companies)
                
                **Environment Variables Required:**
                - `OPENAI_API_KEY` - For embeddings
                - `CHROMA_PERSIST_DIR` - Database location (default: ./output/chroma_db)
                - `USE_REAL_API` - Use real APIs (set to "true")
                - `USE_CHROMA_SECTORS` - Use ChromaDB semantic search (set to "true")
                
                Built with ❤️ using Python, MCP, ChromaDB, and Gradio
                """
            )
        
        return interface


def main():
    """Launch the Gradio app."""
    logger.info("Starting Stock Research Gradio App...")
    
    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set. ChromaDB features may not work.")
    
    app = StockResearchGradioApp()
    interface = app.build_interface()
    
    # Launch the interface
    interface.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,  # Set to True to create public link
        show_error=True
    )


if __name__ == "__main__":
    main()
