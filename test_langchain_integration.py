#!/usr/bin/env python3
"""
Test script for LangChain integration with Tableau MCP Server
"""

import asyncio
import json
from tableau_mcp_server.langchain_integration import (
    SearchWorkbooksTool, 
    SearchDatasourcesTool, 
    SearchUsersTool, 
    GetContentByNameTool,
    TableauQueryProcessor,
    EXAMPLE_QUERIES
)

class MockTableauClient:
    """Mock Tableau client for testing natural language parsing."""
    
    async def search_workbooks(self, name=None, project_name=None, owner_name=None, tag=None):
        """Mock workbook search."""
        result = {
            "workbooks": [
                {
                    "id": "wb123",
                    "name": "Sales Dashboard Q4",
                    "project_name": "Finance",
                    "owner_id": "user456",
                    "tags": ["sales", "quarterly"]
                }
            ],
            "total_count": 1,
            "search_params": {
                "name": name,
                "project_name": project_name,
                "owner_name": owner_name,
                "tag": tag
            }
        }
        return json.dumps(result, indent=2)
    
    async def search_datasources(self, name=None, project_name=None, owner_name=None, datasource_type=None, tag=None):
        """Mock datasource search."""
        result = {
            "datasources": [
                {
                    "id": "ds789",
                    "name": "Customer Database",
                    "project_name": "Marketing",
                    "type": "postgres",
                    "tags": ["customer", "production"]
                }
            ],
            "total_count": 1,
            "search_params": {
                "name": name,
                "project_name": project_name,
                "owner_name": owner_name,
                "datasource_type": datasource_type,
                "tag": tag
            }
        }
        return json.dumps(result, indent=2)
    
    async def search_users(self, name=None, email=None, site_role=None):
        """Mock user search."""
        result = {
            "users": [
                {
                    "id": "user123",
                    "name": "John Doe",
                    "email": "john.doe@company.com",
                    "site_role": "Creator"
                }
            ],
            "total_count": 1,
            "search_params": {
                "name": name,
                "email": email,
                "site_role": site_role
            }
        }
        return json.dumps(result, indent=2)
    
    def get_workbook_by_name(self, workbook_name, project_name):
        """Mock get workbook by name."""
        result = {
            "id": "wb456",
            "name": workbook_name,
            "project_name": project_name,
            "found": True
        }
        return json.dumps(result, indent=2)
    
    def get_user_by_name(self, username):
        """Mock get user by name."""
        result = {
            "id": "user789",
            "name": username,
            "found": True
        }
        return json.dumps(result, indent=2)

async def test_query_parsing():
    """Test natural language query parsing."""
    print("🧪 Testing Natural Language Query Parsing...\n")
    
    mock_client = MockTableauClient()
    
    # Test workbook search parsing
    print("📊 Testing Workbook Search Parsing:")
    wb_tool = SearchWorkbooksTool(tableau_client=mock_client)
    
    test_queries = [
        "sales dashboards",
        "workbooks in finance project", 
        "dashboards created by john",
        "workbooks tagged with quarterly"
    ]
    
    for query in test_queries:
        print(f"  Query: '{query}'")
        parsed = wb_tool._parse_search_query(query)
        print(f"  Parsed: {parsed}")
        result = await wb_tool._run(query)
        search_params = json.loads(result)["search_params"]
        print(f"  Search params: {search_params}")
        print()
    
    # Test datasource search parsing
    print("🗄️  Testing Datasource Search Parsing:")
    ds_tool = SearchDatasourcesTool(tableau_client=mock_client)
    
    ds_queries = [
        "customer data sources",
        "postgres datasources in marketing project",
        "data sources created by admin"
    ]
    
    for query in ds_queries:
        print(f"  Query: '{query}'")
        parsed = ds_tool._parse_search_query(query)
        print(f"  Parsed: {parsed}")
        result = await ds_tool._run(query)
        search_params = json.loads(result)["search_params"]
        print(f"  Search params: {search_params}")
        print()
    
    # Test user search parsing
    print("👥 Testing User Search Parsing:")
    user_tool = SearchUsersTool(tableau_client=mock_client)
    
    user_queries = [
        "john doe",
        "users with creator role",
        "john.doe@company.com"
    ]
    
    for query in user_queries:
        print(f"  Query: '{query}'")
        parsed = user_tool._parse_search_query(query)
        print(f"  Parsed: {parsed}")
        result = await user_tool._run(query)
        search_params = json.loads(result)["search_params"]
        print(f"  Search params: {search_params}")
        print()
    
    # Test content retrieval parsing
    print("🎯 Testing Content Retrieval Parsing:")
    content_tool = GetContentByNameTool(tableau_client=mock_client)
    
    content_queries = [
        "get workbook 'Sales Dashboard' from Finance project",
        "find user john.doe"
    ]
    
    for query in content_queries:
        print(f"  Query: '{query}'")
        parsed = content_tool._parse_content_query(query)
        print(f"  Parsed: {parsed}")
        result = content_tool._run(query)
        print(f"  Result: {json.loads(result)}")
        print()

async def test_query_processor():
    """Test the full query processor."""
    print("🚀 Testing Full Query Processor (without OpenAI)...\n")
    
    mock_client = MockTableauClient()
    processor = TableauQueryProcessor(mock_client, openai_api_key=None)
    
    # Test some example queries
    test_queries = [
        "Find sales dashboards",
        "Search for users",
        "Get workbook 'Q4 Report' from Finance project",
        "Show me data sources in marketing"
    ]
    
    for query in test_queries:
        print(f"Query: '{query}'")
        try:
            result = await processor.process_query(query)
            # Parse and pretty print if it's JSON
            try:
                parsed_result = json.loads(result)
                print(f"Result: {json.dumps(parsed_result, indent=2)}")
            except:
                print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50)

async def test_server_integration():
    """Test server integration."""
    print("⚙️  Testing Server Integration...\n")
    
    from tableau_mcp_server.server import handle_list_tools
    
    # Get list of tools to verify natural_language_query is included
    tools = await handle_list_tools()
    
    nl_tool = None
    for tool in tools:
        if tool.name == "natural_language_query":
            nl_tool = tool
            break
    
    if nl_tool:
        print("✅ Natural language query tool found in server:")
        print(f"  Name: {nl_tool.name}")
        print(f"  Description: {nl_tool.description}")
        print(f"  Schema: {nl_tool.inputSchema}")
    else:
        print("❌ Natural language query tool not found in server")
    
    print(f"\nTotal tools available: {len(tools)}")

async def main():
    """Run all tests."""
    print("🔬 Testing LangChain Integration for Tableau MCP Server\n")
    print("=" * 60)
    
    await test_query_parsing()
    print("=" * 60)
    
    await test_query_processor()
    print("=" * 60)
    
    await test_server_integration()
    print("=" * 60)
    
    print("📋 Example queries you can now use:")
    for i, query in enumerate(EXAMPLE_QUERIES[:5], 1):
        print(f"  {i}. {query}")
    
    print("\n✅ LangChain integration testing completed!")
    print("\n💡 To use with OpenAI LLM, set OPENAI_API_KEY environment variable")

if __name__ == "__main__":
    asyncio.run(main())