#!/usr/bin/env python3
"""
Test script for the enhanced Tableau MCP Server functionality
"""

import asyncio
import json
from tableau_mcp_server.server import handle_list_tools

async def test_enhanced_tools():
    """Test that all enhanced tools are available."""
    print("Testing Enhanced Tableau MCP Server...")
    
    # Get list of available tools
    tools = await handle_list_tools()
    
    print(f"\nAvailable tools ({len(tools)}):")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Check for new search/discovery tools
    search_tools = [tool for tool in tools if 'search' in tool.name or 'get_' in tool.name]
    print(f"\nSearch and discovery tools ({len(search_tools)}):")
    for tool in search_tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Check enhanced existing tools
    enhanced_tools = [tool for tool in tools if 'accepts names' in tool.description or 'accepts name' in tool.description]
    print(f"\nEnhanced tools that accept names ({len(enhanced_tools)}):")
    for tool in enhanced_tools:
        print(f"  - {tool.name}")
    
    print("\n✅ Enhanced server test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_tools())