"""Test script to verify the MCP server installation."""

import asyncio
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stock_research_mcp.agents import MultiAgentOrchestrator
from stock_research_mcp.types import Stock


async def test_agents():
    """Test all agents are working."""
    print("=" * 60)
    print("Testing Stock Research MCP Server Components")
    print("=" * 60)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Test 1: Stock Search Agent
    print("\n✓ Test 1: Stock Search Agent")
    search_result = await orchestrator.search_agent.search_stocks_by_sector("technology")
    assert search_result.success, "Search agent failed"
    stocks = [Stock(**s) for s in search_result.data["stocks"]]
    print(f"  Found {len(stocks)} technology stocks")
    
    # Test 2: Stock Categorization Agent
    print("\n✓ Test 2: Stock Categorization Agent")
    categorize_result = await orchestrator.categorization_agent.categorize_stocks(stocks)
    assert categorize_result.success, "Categorization agent failed"
    print(f"  High: {len(categorize_result.data['high'])} stocks")
    print(f"  Medium: {len(categorize_result.data['medium'])} stocks")
    print(f"  Low: {len(categorize_result.data['low'])} stocks")
    
    # Test 3: Stock Analysis Agent
    print("\n✓ Test 3: Stock Analysis Agent")
    test_stock = stocks[0]
    category = orchestrator.categorization_agent.get_category_for_stock(test_stock)
    analysis_result = await orchestrator.analysis_agent.analyze_stock(test_stock, category)
    assert analysis_result.success, "Analysis agent failed"
    print(f"  Analyzed {test_stock.symbol} successfully")
    print(f"  Found {len(analysis_result.data['analysis']['news'])} news items")
    print(f"  Found {len(analysis_result.data['analysis']['events'])} events")
    
    # Test 4: Full Orchestration
    print("\n✓ Test 4: Multi-Agent Orchestration")
    full_result = await orchestrator.process_sector_query("healthcare")
    assert full_result["success"], "Orchestration failed"
    print(f"  Processed {full_result['total_stocks']} healthcare stocks")
    
    # Test 5: Output Formatting
    print("\n✓ Test 5: Output Formatting")
    formatted = orchestrator.format_results(full_result)
    assert len(formatted) > 100, "Formatting failed"
    print(f"  Generated {len(formatted)} characters of formatted output")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    print("\nYour MCP server is ready to use!")
    print("\nNext steps:")
    print("1. Configure Claude Desktop (see QUICKSTART.md)")
    print("2. Restart Claude Desktop")
    print("3. Try: 'Analyze stocks in the technology sector'")
    print("\n" + "=" * 60)


def main():
    """Run all tests."""
    try:
        asyncio.run(test_agents())
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
