#!/usr/bin/env python3
"""
Test script for the Tableau Cloud MCP Server

This script tests basic functionality without running the full MCP protocol.
"""

import asyncio
import json
from tableau_mcp_server.tableau_client import TableauCloudClient


async def test_tableau_client():
    """Test the Tableau Cloud client functionality."""
    print("Testing Tableau Cloud MCP Server...")
    
    import os
    
    # Initialize the client from environment variables
    client = TableauCloudClient(
        server_url=os.getenv("TABLEAU_SERVER_URL", "https://eu-west-1a.online.tableau.com"),
        site_id=os.getenv("TABLEAU_SITE_ID", "itsummit"),
        token_name=os.getenv("TABLEAU_TOKEN_NAME"),
        token_value=os.getenv("TABLEAU_TOKEN_VALUE")
    )
    
    try:
        # Test connection
        print("1. Testing connection to Tableau Cloud...")
        await client.connect()
        print("✅ Connected successfully!")
        
        # Test site info
        print("\n2. Testing site information retrieval...")
        site_info = await client.get_site_info()
        print("✅ Site info retrieved successfully!")
        print(f"Site info: {json.loads(site_info)['name']}")
        
        # Test listing users
        print("\n3. Testing user list retrieval...")
        users = await client.list_users()
        user_data = json.loads(users)
        print(f"✅ Found {user_data['total_count']} users")
        
        # Test listing projects
        print("\n4. Testing project list retrieval...")
        projects = await client.list_projects()
        project_data = json.loads(projects)
        print(f"✅ Found {project_data['total_count']} projects")
        
        # Test listing workbooks
        print("\n5. Testing workbook list retrieval...")
        workbooks = await client.list_workbooks()
        workbook_data = json.loads(workbooks)
        print(f"✅ Found {workbook_data['total_count']} workbooks")
        
        # Test listing data sources
        print("\n6. Testing data source list retrieval...")
        datasources = await client.list_datasources()
        datasource_data = json.loads(datasources)
        print(f"✅ Found {datasource_data['total_count']} data sources")
        
        print("\n🎉 All tests passed! The Tableau Cloud MCP Server is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_tableau_client())