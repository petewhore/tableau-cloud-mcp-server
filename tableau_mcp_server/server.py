#!/usr/bin/env python3
"""
Tableau Cloud MCP Server

An MCP server that provides tools for administering Tableau Cloud deployments.
Supports content management, user administration, and permission management.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import tableauserverclient as TSC
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

from .tableau_client import TableauCloudClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tableau-mcp-server")

# Initialize the MCP server
server = Server("tableau-cloud-mcp-server")

# Tableau client instance
tableau_client: Optional[TableauCloudClient] = None


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
    if not tableau_client:
        raise RuntimeError("Tableau client not initialized")
    
    uri_str = str(uri)
    
    if uri_str == "tableau://site/info":
        return await tableau_client.get_site_info()
    elif uri_str == "tableau://users/list":
        return await tableau_client.list_users()
    elif uri_str == "tableau://projects/list":
        return await tableau_client.list_projects()
    elif uri_str == "tableau://workbooks/list":
        return await tableau_client.list_workbooks()
    elif uri_str == "tableau://datasources/list":
        return await tableau_client.list_datasources()
    else:
        raise ValueError(f"Unknown resource URI: {uri}")


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
                    "auth_setting": {"type": "string", "description": "Authentication method (ServerDefault, SAML, OpenID)", "default": "ServerDefault"}
                },
                "required": ["username", "site_role"]
            },
        ),
        Tool(
            name="update_user",
            description="Update an existing user's properties",
            inputSchema={
                "type": "object", 
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user to update"},
                    "site_role": {"type": "string", "description": "New site role"},
                    "auth_setting": {"type": "string", "description": "New authentication method"}
                },
                "required": ["user_id"]
            },
        ),
        Tool(
            name="delete_user",
            description="Remove a user from Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user to delete"}
                },
                "required": ["user_id"]
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
            name="move_datasource",
            description="Move a data source to a different project",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source to move"},
                    "target_project_id": {"type": "string", "description": "ID of the target project"}
                },
                "required": ["datasource_id", "target_project_id"]
            },
        ),
        Tool(
            name="create_project",
            description="Create a new project in Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the new project"},
                    "description": {"type": "string", "description": "Description of the project"},
                    "parent_project_id": {"type": "string", "description": "ID of parent project (for nested projects)"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="grant_permissions",
            description="Grant permissions to a user or group for a content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_type": {"type": "string", "description": "Type of content (workbook, datasource, project)", "enum": ["workbook", "datasource", "project"]},
                    "content_id": {"type": "string", "description": "ID of the content item"},
                    "grantee_type": {"type": "string", "description": "Type of grantee (user, group)", "enum": ["user", "group"]},
                    "grantee_id": {"type": "string", "description": "ID of the user or group"},
                    "permissions": {"type": "array", "items": {"type": "string"}, "description": "List of permissions to grant"}
                },
                "required": ["content_type", "content_id", "grantee_type", "grantee_id", "permissions"]
            },
        ),
        Tool(
            name="revoke_permissions",
            description="Revoke permissions from a user or group for a content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_type": {"type": "string", "description": "Type of content (workbook, datasource, project)", "enum": ["workbook", "datasource", "project"]},
                    "content_id": {"type": "string", "description": "ID of the content item"},
                    "grantee_type": {"type": "string", "description": "Type of grantee (user, group)", "enum": ["user", "group"]},
                    "grantee_id": {"type": "string", "description": "ID of the user or group"},
                    "permissions": {"type": "array", "items": {"type": "string"}, "description": "List of permissions to revoke"}
                },
                "required": ["content_type", "content_id", "grantee_type", "grantee_id", "permissions"]
            },
        ),
        Tool(
            name="list_content_permissions",
            description="List all permissions for a content item",
            inputSchema={
                "type": "object",
                "properties": {
                    "content_type": {"type": "string", "description": "Type of content (workbook, datasource, project)", "enum": ["workbook", "datasource", "project"]},
                    "content_id": {"type": "string", "description": "ID of the content item"}
                },
                "required": ["content_type", "content_id"]
            },
        ),
        Tool(
            name="create_group",
            description="Create a new group in Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the new group"},
                    "domain_name": {"type": "string", "description": "Domain name for local groups"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="add_user_to_group",
            description="Add a user to a group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": "ID of the group"},
                    "user_id": {"type": "string", "description": "ID of the user to add"}
                },
                "required": ["group_id", "user_id"]
            },
        ),
        Tool(
            name="remove_user_from_group", 
            description="Remove a user from a group",
            inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": "ID of the group"},
                    "user_id": {"type": "string", "description": "ID of the user to remove"}
                },
                "required": ["group_id", "user_id"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for Tableau Cloud administration."""
    if not tableau_client:
        raise RuntimeError("Tableau client not initialized")

    try:
        if name == "create_user":
            result = await tableau_client.create_user(
                username=arguments["username"],
                site_role=arguments["site_role"],
                auth_setting=arguments.get("auth_setting", "ServerDefault")
            )
        elif name == "update_user":
            result = await tableau_client.update_user(
                user_id=arguments["user_id"],
                site_role=arguments.get("site_role"),
                auth_setting=arguments.get("auth_setting")
            )
        elif name == "delete_user":
            result = await tableau_client.delete_user(arguments["user_id"])
        elif name == "move_workbook":
            result = await tableau_client.move_workbook(
                workbook_id=arguments["workbook_id"],
                target_project_id=arguments["target_project_id"]
            )
        elif name == "move_datasource":
            result = await tableau_client.move_datasource(
                datasource_id=arguments["datasource_id"],
                target_project_id=arguments["target_project_id"]
            )
        elif name == "create_project":
            result = await tableau_client.create_project(
                name=arguments["name"],
                description=arguments.get("description"),
                parent_project_id=arguments.get("parent_project_id")
            )
        elif name == "grant_permissions":
            result = await tableau_client.grant_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                grantee_type=arguments["grantee_type"],
                grantee_id=arguments["grantee_id"],
                permissions=arguments["permissions"]
            )
        elif name == "revoke_permissions":
            result = await tableau_client.revoke_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                grantee_type=arguments["grantee_type"],
                grantee_id=arguments["grantee_id"],
                permissions=arguments["permissions"]
            )
        elif name == "list_content_permissions":
            result = await tableau_client.list_content_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"]
            )
        elif name == "create_group":
            result = await tableau_client.create_group(
                name=arguments["name"],
                domain_name=arguments.get("domain_name")
            )
        elif name == "add_user_to_group":
            result = await tableau_client.add_user_to_group(
                group_id=arguments["group_id"],
                user_id=arguments["user_id"]
            )
        elif name == "remove_user_from_group":
            result = await tableau_client.remove_user_from_group(
                group_id=arguments["group_id"],
                user_id=arguments["user_id"]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Main entry point for the MCP server."""
    import os
    global tableau_client
    
    # Initialize Tableau client from environment variables
    tableau_client = TableauCloudClient(
        server_url=os.getenv("TABLEAU_SERVER_URL", "https://eu-west-1a.online.tableau.com"),
        site_id=os.getenv("TABLEAU_SITE_ID", "itsummit"),
        token_name=os.getenv("TABLEAU_TOKEN_NAME"),
        token_value=os.getenv("TABLEAU_TOKEN_VALUE")
    )
    
    await tableau_client.connect()
    logger.info("Connected to Tableau Cloud")
    
    # Run the MCP server
    async with server.run_session() as session:
        await session.init()
        logger.info("Tableau Cloud MCP Server started")
        
        # Keep the server running
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    asyncio.run(main())