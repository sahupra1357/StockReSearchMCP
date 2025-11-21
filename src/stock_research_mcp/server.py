"""MCP Server for Stock Research - Main entry point."""

import asyncio
import logging
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .agents import MultiAgentOrchestrator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StockResearchMCPServer:
    """
    Multi-Agent Stock Research MCP Server
    
    Provides tools for comprehensive stock analysis using a multi-agent architecture.
    """
    
    def __init__(self):
        self.server = Server("stock-research-mcp-server")
        self.orchestrator = MultiAgentOrchestrator()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP request handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="analyze_sector",
                    description="""Comprehensive multi-agent stock analysis for a specific sector.

This tool performs a three-stage analysis:
1. Searches for all stocks in the specified sector
2. Categorizes stocks into three groups:
   - High-value: Price > $100
   - Medium-value: Price $10-$100
   - Low-value: Price < $10
3. Provides detailed analysis for each stock including:
   - Price trend analysis
   - Recent news and sentiment
   - Upcoming events
   - Investment recommendation

Example sectors: technology, healthcare, finance, energy, retail, automotive""",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sector": {
                                "type": "string",
                                "description": "The sector to analyze (e.g., technology, healthcare, finance, energy)"
                            }
                        },
                        "required": ["sector"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: dict[str, Any]
        ) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "analyze_sector":
                    return await self._handle_analyze_sector(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error handling tool call: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
    async def _handle_analyze_sector(self, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle analyze_sector tool call."""
        sector = arguments.get("sector")
        
        if not sector:
            raise ValueError("Sector parameter is required")
        
        logger.info(f"Processing sector analysis request for: {sector}")
        
        # Execute multi-agent analysis
        result = await self.orchestrator.process_sector_query(sector)
        
        if not result["success"]:
            error_msg = result.get("error", "Analysis failed")
            raise ValueError(error_msg)
        
        # Format the results
        formatted_output = self.orchestrator.format_results(result)
        
        return [TextContent(type="text", text=formatted_output)]
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Stock Research MCP Server starting...")
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="stock-research-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )


def main():
    """Main entry point."""
    server = StockResearchMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
