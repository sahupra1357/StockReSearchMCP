"""Example script showing how to use the orchestrator directly."""

import asyncio
from stock_research_mcp.agents import MultiAgentOrchestrator


async def main():
    """Run example analysis."""
    orchestrator = MultiAgentOrchestrator()
    
    # Analyze technology sector
    print("Starting analysis...\n")
    result = await orchestrator.process_sector_query("technology")
    
    # Format and display results
    formatted = orchestrator.format_results(result)
    print(formatted)
    
    # You can also access raw data
    if result["success"]:
        print(f"\n\nRaw data structure:")
        print(f"Total stocks: {result['total_stocks']}")
        print(f"High-value stocks: {len(result['categorized_stocks']['high'])}")
        print(f"Medium-value stocks: {len(result['categorized_stocks']['medium'])}")
        print(f"Low-value stocks: {len(result['categorized_stocks']['low'])}")


if __name__ == "__main__":
    asyncio.run(main())
