#!/usr/bin/env python3
"""
Simple test for natural language query functionality
"""

import asyncio
from tableau_mcp_server.server import handle_list_tools

async def test_nl_tool():
    """Test that natural language tool is available."""
    print("🔍 Testing Natural Language Query Tool Availability...")
    
    tools = await handle_list_tools()
    
    # Find the natural language tool
    nl_tool = None
    for tool in tools:
        if tool.name == "natural_language_query":
            nl_tool = tool
            break
    
    if nl_tool:
        print("✅ Natural Language Query tool found!")
        print(f"   Description: {nl_tool.description}")
        print(f"   Input schema: {nl_tool.inputSchema}")
        
        # Show example usage
        print("\n📝 Example queries you can use:")
        examples = [
            "Find sales dashboards",
            "Search for workbooks in Finance project", 
            "Show me John's workbooks",
            "Get data sources tagged with customer",
            "Find users with Creator role"
        ]
        
        for i, example in enumerate(examples, 1):
            print(f"   {i}. {example}")
        
        print(f"\n📊 Total tools available: {len(tools)}")
        print("   Including enhanced search tools:")
        search_tools = [t.name for t in tools if 'search' in t.name or 'get_' in t.name]
        for tool_name in search_tools:
            print(f"     - {tool_name}")
        
        return True
    else:
        print("❌ Natural Language Query tool not found")
        return False

async def main():
    print("🧪 Testing Natural Language Integration\n")
    success = await test_nl_tool()
    
    if success:
        print("\n🎉 Integration successful!")
        print("\n💡 Next steps:")
        print("   1. Set OPENAI_API_KEY environment variable for full LLM support")
        print("   2. Use 'natural_language_query' tool with queries like:")
        print("      'Find all sales dashboards in Finance project'")
        print("   3. Fallback pattern matching works without OpenAI API key")
    else:
        print("\n❌ Integration failed")

if __name__ == "__main__":
    asyncio.run(main())