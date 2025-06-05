#!/usr/bin/env python3
"""
MCP Proxy Client for Heroku-hosted Tableau Cloud MCP Server

This script acts as a local MCP server that forwards requests to your
Heroku-hosted server, allowing Claude Desktop to work with remote MCP servers.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List

import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tableau-mcp-proxy")

# Your Heroku server URL
HEROKU_SERVER_URL = "https://your-tableau-mcp-server-4a222eaf1bc3.herokuapp.com"

# Initialize the MCP proxy server
server = Server("tableau-cloud-mcp-proxy")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available Tableau Cloud resources."""
    return [
        Resource(
            uri=AnyUrl("tableau://site/info"),
            name="Site Information",
            description="Current Tableau Cloud site details and configuration",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("tableau://users/list"),
            name="Users List", 
            description="List of all users in the Tableau Cloud site",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("tableau://projects/list"),
            name="Projects List",
            description="List of all projects in the Tableau Cloud site", 
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("tableau://workbooks/list"),
            name="Workbooks List",
            description="List of all workbooks in the Tableau Cloud site",
            mimeType="application/json",
        ),
        Resource(
            uri=AnyUrl("tableau://datasources/list"),
            name="Data Sources List",
            description="List of all data sources in the Tableau Cloud site",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read a specific Tableau Cloud resource."""
    uri_str = str(uri)
    
    # Map MCP resource URIs to HTTP endpoints
    endpoint_map = {
        "tableau://site/info": "/site",
        "tableau://users/list": "/users",
        "tableau://projects/list": "/projects", 
        "tableau://workbooks/list": "/workbooks",
        "tableau://datasources/list": "/datasources"
    }
    
    endpoint = endpoint_map.get(uri_str)
    if not endpoint:
        raise ValueError(f"Unknown resource URI: {uri}")
    
    # Make HTTP request to Heroku server
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{HEROKU_SERVER_URL}{endpoint}")
        response.raise_for_status()
        return response.text

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Tableau Cloud administration tools."""
    return [
        Tool(
            name="create_user",
            description="Create a new user in Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Username for the new user"},
                    "site_role": {"type": "string", "description": "Site role (Viewer, Explorer, Creator, SiteAdministratorExplorer, SiteAdministratorCreator)"},
                },
                "required": ["username", "site_role"]
            },
        ),
        Tool(
            name="move_workbook",
            description="Move a workbook to a different project",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook to move"},
                    "target_project_id": {"type": "string", "description": "ID of the target project"}
                },
                "required": ["workbook_id", "target_project_id"]
            },
        ),
        Tool(
            name="list_users",
            description="List all users in the Tableau Cloud site",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_projects",
            description="List all projects in the Tableau Cloud site",
            inputSchema={
                "type": "object", 
                "properties": {},
            },
        ),
        Tool(
            name="list_workbooks",
            description="List all workbooks in the Tableau Cloud site",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls by forwarding to Heroku server."""
    
    try:
        async with httpx.AsyncClient() as client:
            
            if name == "create_user":
                params = {
                    "username": arguments["username"],
                    "site_role": arguments["site_role"]
                }
                response = await client.get(f"{HEROKU_SERVER_URL}/create_user", params=params)
                
            elif name == "move_workbook":
                params = {
                    "workbook_id": arguments["workbook_id"],
                    "project_id": arguments["target_project_id"]
                }
                response = await client.get(f"{HEROKU_SERVER_URL}/move_workbook", params=params)
                
            elif name == "list_users":
                response = await client.get(f"{HEROKU_SERVER_URL}/users")
                
            elif name == "list_projects":
                response = await client.get(f"{HEROKU_SERVER_URL}/projects")
                
            elif name == "list_workbooks":
                response = await client.get(f"{HEROKU_SERVER_URL}/workbooks")
                
            else:
                raise ValueError(f"Unknown tool: {name}")
            
            response.raise_for_status()
            result = response.text
            
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP proxy server."""
    logger.info("Starting Tableau Cloud MCP Proxy Server...")
    
    # Test connection to Heroku server
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{HEROKU_SERVER_URL}/health")
            response.raise_for_status()
            logger.info("Successfully connected to Heroku server")
    except Exception as e:
        logger.error(f"Failed to connect to Heroku server: {e}")
        return
    
    # Run the MCP proxy server
    async with server.run_session() as session:
        await session.init()
        logger.info("Tableau Cloud MCP Proxy Server started")
        
        # Keep the server running
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())