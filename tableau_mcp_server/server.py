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
from .extended_tableau_client import ExtendedTableauCloudClient
from .langchain_integration import TableauQueryProcessor

# Make tableau_client and query_processor globally accessible
tableau_client: Optional[ExtendedTableauCloudClient] = None
query_processor: Optional[TableauQueryProcessor] = None

def get_tableau_client():
    """Get the global tableau client instance."""
    global tableau_client
    return tableau_client

def set_tableau_client(client: ExtendedTableauCloudClient):
    """Set the global tableau client instance."""
    global tableau_client, query_processor
    tableau_client = client
    
    # Initialize query processor
    import os
    openai_api_key = os.getenv("OPENAI_API_KEY")
    query_processor = TableauQueryProcessor(client, openai_api_key)

def get_query_processor():
    """Get the global query processor instance."""
    global query_processor
    return query_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tableau-mcp-server")

# Initialize the MCP server
server = Server("tableau-cloud-mcp-server")



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
    client = get_tableau_client()
    if not client:
        raise RuntimeError("Tableau client not initialized")
    
    uri_str = str(uri)
    
    if uri_str == "tableau://site/info":
        return await client.get_site_info()
    elif uri_str == "tableau://users/list":
        return await client.list_users()
    elif uri_str == "tableau://projects/list":
        return await client.list_projects()
    elif uri_str == "tableau://workbooks/list":
        return await client.list_workbooks()
    elif uri_str == "tableau://datasources/list":
        return await client.list_datasources()
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
            description="Update an existing user's properties (accepts name or ID)",
            inputSchema={
                "type": "object", 
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user to update (use this OR username)"},
                    "username": {"type": "string", "description": "Name of the user to update"},
                    "site_role": {"type": "string", "description": "New site role"},
                    "auth_setting": {"type": "string", "description": "New authentication method"}
                },
                "required": []
            },
        ),
        Tool(
            name="delete_user",
            description="Remove a user from Tableau Cloud (accepts name or ID)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user to delete (use this OR username)"},
                    "username": {"type": "string", "description": "Name of the user to delete"}
                },
                "required": []
            },
        ),
        Tool(
            name="move_workbook",
            description="Move a workbook to a different project (accepts names or IDs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook to move (use this OR workbook_name + current_project_name)"},
                    "workbook_name": {"type": "string", "description": "Name of the workbook to move"},
                    "current_project_name": {"type": "string", "description": "Current project name containing the workbook"},
                    "target_project_id": {"type": "string", "description": "ID of the target project (use this OR target_project_name)"},
                    "target_project_name": {"type": "string", "description": "Name of the target project"}
                },
                "required": []
            },
        ),
        Tool(
            name="move_datasource",
            description="Move a data source to a different project (accepts names or IDs)",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source to move (use this OR datasource_name + current_project_name)"},
                    "datasource_name": {"type": "string", "description": "Name of the data source to move"},
                    "current_project_name": {"type": "string", "description": "Current project name containing the data source"},
                    "target_project_id": {"type": "string", "description": "ID of the target project (use this OR target_project_name)"},
                    "target_project_name": {"type": "string", "description": "Name of the target project"}
                },
                "required": []
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
        Tool(
            name="search_workbooks",
            description="Search for workbooks by name, project, or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by workbook name (partial match)"},
                    "project_name": {"type": "string", "description": "Filter by project name"},
                    "tag": {"type": "string", "description": "Filter by tag"},
                    "owner_name": {"type": "string", "description": "Filter by owner name"}
                },
                "required": []
            },
        ),
        Tool(
            name="search_datasources",
            description="Search for data sources by name, project, or tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by data source name (partial match)"},
                    "project_name": {"type": "string", "description": "Filter by project name"},
                    "tag": {"type": "string", "description": "Filter by tag"},
                    "owner_name": {"type": "string", "description": "Filter by owner name"},
                    "datasource_type": {"type": "string", "description": "Filter by data source type"}
                },
                "required": []
            },
        ),
        Tool(
            name="search_users",
            description="Search for users by name, email, or site role",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by user name (partial match)"},
                    "email": {"type": "string", "description": "Search by email (partial match)"},
                    "site_role": {"type": "string", "description": "Filter by site role"}
                },
                "required": []
            },
        ),
        Tool(
            name="search_projects",
            description="Search for projects by name or description",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Search by project name (partial match)"},
                    "description": {"type": "string", "description": "Search by description (partial match)"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_workbook_by_name",
            description="Get workbook details by name and project (returns LUID for use in other operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_name": {"type": "string", "description": "Name of the workbook"},
                    "project_name": {"type": "string", "description": "Name of the project containing the workbook"}
                },
                "required": ["workbook_name", "project_name"]
            },
        ),
        Tool(
            name="get_datasource_by_name",
            description="Get data source details by name and project (returns LUID for use in other operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_name": {"type": "string", "description": "Name of the data source"},
                    "project_name": {"type": "string", "description": "Name of the project containing the data source"}
                },
                "required": ["datasource_name", "project_name"]
            },
        ),
        Tool(
            name="get_user_by_name",
            description="Get user details by name (returns LUID for use in other operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string", "description": "Name of the user"}
                },
                "required": ["username"]
            },
        ),
        Tool(
            name="get_project_by_name",
            description="Get project details by name (returns LUID for use in other operations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Name of the project"}
                },
                "required": ["project_name"]
            },
        ),
        Tool(
            name="list_groups",
            description="List all groups in the Tableau Cloud site",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="natural_language_query",
            description="Process natural language queries about Tableau content. Examples: 'Find sales dashboards', 'Show me John's workbooks', 'Get Analytics project', 'Search for data sources in Finance'",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Natural language query about Tableau content"}
                },
                "required": ["query"]
            },
        ),
        # =================================================================
        # WORKBOOK MANAGEMENT (Extended)
        # =================================================================
        Tool(
            name="publish_workbook",
            description="Publish a workbook file to Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_file_path": {"type": "string", "description": "Path to the workbook file (.twbx or .twb)"},
                    "project_id": {"type": "string", "description": "ID of the target project"},
                    "workbook_name": {"type": "string", "description": "Optional name for the workbook"},
                    "show_tabs": {"type": "boolean", "description": "Whether to show workbook tabs", "default": True},
                    "overwrite": {"type": "boolean", "description": "Whether to overwrite existing workbook", "default": False},
                    "skip_connection_check": {"type": "boolean", "description": "Skip connection validation", "default": False}
                },
                "required": ["workbook_file_path", "project_id"]
            },
        ),
        Tool(
            name="download_workbook",
            description="Download a workbook from Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook to download"},
                    "file_path": {"type": "string", "description": "Local file path to save the workbook"},
                    "include_extract": {"type": "boolean", "description": "Include extract data", "default": True}
                },
                "required": ["workbook_id", "file_path"]
            },
        ),
        Tool(
            name="get_workbook_views",
            description="Get all views in a workbook",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook"}
                },
                "required": ["workbook_id"]
            },
        ),
        Tool(
            name="get_workbook_connections",
            description="Get all data connections for a workbook",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook"}
                },
                "required": ["workbook_id"]
            },
        ),
        Tool(
            name="refresh_workbook_now",
            description="Trigger immediate refresh of workbook extracts",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook to refresh"}
                },
                "required": ["workbook_id"]
            },
        ),
        # =================================================================
        # VIEW MANAGEMENT
        # =================================================================
        Tool(
            name="list_views",
            description="List all views with optional usage statistics",
            inputSchema={
                "type": "object",
                "properties": {
                    "usage_stats": {"type": "boolean", "description": "Include usage statistics", "default": False}
                },
                "required": []
            },
        ),
        Tool(
            name="get_view_image",
            description="Download view as image (PNG) or PDF",
            inputSchema={
                "type": "object",
                "properties": {
                    "view_id": {"type": "string", "description": "ID of the view"},
                    "file_path": {"type": "string", "description": "Local file path to save the image"},
                    "image_format": {"type": "string", "description": "Format: png or pdf", "default": "png"},
                    "max_age": {"type": "integer", "description": "Maximum age of cached image in minutes", "default": 1}
                },
                "required": ["view_id", "file_path"]
            },
        ),
        # =================================================================
        # DATA SOURCE MANAGEMENT (Extended)
        # =================================================================
        Tool(
            name="publish_datasource",
            description="Publish a data source file to Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_file_path": {"type": "string", "description": "Path to the data source file (.tds or .tdsx)"},
                    "project_id": {"type": "string", "description": "ID of the target project"},
                    "datasource_name": {"type": "string", "description": "Optional name for the data source"},
                    "overwrite": {"type": "boolean", "description": "Whether to overwrite existing data source", "default": False}
                },
                "required": ["datasource_file_path", "project_id"]
            },
        ),
        Tool(
            name="download_datasource",
            description="Download a data source from Tableau Cloud",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source to download"},
                    "file_path": {"type": "string", "description": "Local file path to save the data source"},
                    "include_extract": {"type": "boolean", "description": "Include extract data", "default": True}
                },
                "required": ["datasource_id", "file_path"]
            },
        ),
        Tool(
            name="refresh_datasource_now",
            description="Trigger immediate refresh of data source extracts",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source to refresh"}
                },
                "required": ["datasource_id"]
            },
        ),
        Tool(
            name="get_datasource_connections",
            description="Get all data connections for a data source",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source"}
                },
                "required": ["datasource_id"]
            },
        ),
        # =================================================================
        # JOB AND TASK MANAGEMENT
        # =================================================================
        Tool(
            name="list_jobs",
            description="List background jobs with optional filtering by job type",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_type": {"type": "string", "description": "Filter by job type (refresh_extracts, etc.)"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_job_status",
            description="Get status of a specific background job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "ID of the job"}
                },
                "required": ["job_id"]
            },
        ),
        Tool(
            name="cancel_job",
            description="Cancel a running background job",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {"type": "string", "description": "ID of the job to cancel"}
                },
                "required": ["job_id"]
            },
        ),
        # =================================================================
        # SCHEDULE MANAGEMENT
        # =================================================================
        Tool(
            name="list_schedules",
            description="List all schedules",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="create_schedule",
            description="Create a new schedule",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the schedule"},
                    "schedule_type": {"type": "string", "description": "Type of schedule (Extract, Subscription)"},
                    "frequency": {"type": "string", "description": "Frequency (Daily, Weekly, Monthly)"},
                    "priority": {"type": "integer", "description": "Priority (1-100)", "default": 50}
                },
                "required": ["name", "schedule_type", "frequency"]
            },
        ),
        # =================================================================
        # SUBSCRIPTION MANAGEMENT
        # =================================================================
        Tool(
            name="list_subscriptions",
            description="List all subscriptions",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="create_subscription",
            description="Create a new subscription",
            inputSchema={
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Email subject"},
                    "user_id": {"type": "string", "description": "ID of the user to subscribe"},
                    "content_type": {"type": "string", "description": "Type of content (View, Workbook)"},
                    "content_id": {"type": "string", "description": "ID of the content"},
                    "schedule_id": {"type": "string", "description": "ID of the schedule"}
                },
                "required": ["subject", "user_id", "content_type", "content_id", "schedule_id"]
            },
        ),
        # =================================================================
        # FAVORITES MANAGEMENT
        # =================================================================
        Tool(
            name="list_favorites",
            description="List favorites for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user"}
                },
                "required": ["user_id"]
            },
        ),
        Tool(
            name="add_favorite",
            description="Add content to user's favorites",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "ID of the user"},
                    "content_type": {"type": "string", "description": "Type of content (Workbook, View, Datasource)"},
                    "content_id": {"type": "string", "description": "ID of the content"},
                    "label": {"type": "string", "description": "Optional label for the favorite"}
                },
                "required": ["user_id", "content_type", "content_id"]
            },
        ),
        # =================================================================
        # SITE ADMINISTRATION
        # =================================================================
        Tool(
            name="update_site",
            description="Update site settings",
            inputSchema={
                "type": "object",
                "properties": {
                    "site_name": {"type": "string", "description": "New site name"},
                    "content_url": {"type": "string", "description": "New content URL"},
                    "admin_mode": {"type": "string", "description": "Admin mode setting"},
                    "user_quota": {"type": "integer", "description": "User quota limit"},
                    "storage_quota": {"type": "integer", "description": "Storage quota in MB"},
                    "disable_subscriptions": {"type": "boolean", "description": "Disable subscriptions"}
                },
                "required": []
            },
        ),
        # =================================================================
        # TAG MANAGEMENT
        # =================================================================
        Tool(
            name="add_tags_to_workbook",
            description="Add tags to a workbook",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags to add"}
                },
                "required": ["workbook_id", "tags"]
            },
        ),
        Tool(
            name="add_tags_to_datasource",
            description="Add tags to a data source",
            inputSchema={
                "type": "object",
                "properties": {
                    "datasource_id": {"type": "string", "description": "ID of the data source"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags to add"}
                },
                "required": ["datasource_id", "tags"]
            },
        ),
        Tool(
            name="remove_tags_from_workbook",
            description="Remove tags from a workbook",
            inputSchema={
                "type": "object",
                "properties": {
                    "workbook_id": {"type": "string", "description": "ID of the workbook"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "List of tags to remove"}
                },
                "required": ["workbook_id", "tags"]
            },
        ),
        # =================================================================
        # WEBHOOK MANAGEMENT
        # =================================================================
        Tool(
            name="list_webhooks",
            description="List all webhooks",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="create_webhook",
            description="Create a new webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the webhook"},
                    "url": {"type": "string", "description": "URL endpoint for the webhook"},
                    "event": {"type": "string", "description": "Event type to trigger webhook"}
                },
                "required": ["name", "url", "event"]
            },
        ),
        Tool(
            name="delete_webhook",
            description="Delete a webhook",
            inputSchema={
                "type": "object",
                "properties": {
                    "webhook_id": {"type": "string", "description": "ID of the webhook to delete"}
                },
                "required": ["webhook_id"]
            },
        ),
        # =================================================================
        # FLOW MANAGEMENT
        # =================================================================
        Tool(
            name="list_flows",
            description="List all Tableau Prep flows",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        # =================================================================
        # ADVANCED SEARCH
        # =================================================================
        Tool(
            name="search_content",
            description="Advanced search across all content types (workbooks, data sources, flows)",
            inputSchema={
                "type": "object",
                "properties": {
                    "search_term": {"type": "string", "description": "Term to search for"},
                    "content_types": {"type": "array", "items": {"type": "string"}, "description": "Content types to search (workbooks, datasources, flows)"}
                },
                "required": ["search_term"]
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls for Tableau Cloud administration."""
    client = get_tableau_client()
    if not client:
        raise RuntimeError("Tableau client not initialized")

    try:
        if name == "create_user":
            result = await client.create_user(
                username=arguments["username"],
                site_role=arguments["site_role"],
                auth_setting=arguments.get("auth_setting", "ServerDefault")
            )
        elif name == "update_user":
            result = await client.update_user_enhanced(
                user_id=arguments.get("user_id"),
                username=arguments.get("username"),
                site_role=arguments.get("site_role"),
                auth_setting=arguments.get("auth_setting")
            )
        elif name == "delete_user":
            result = await client.delete_user_enhanced(
                user_id=arguments.get("user_id"),
                username=arguments.get("username")
            )
        elif name == "move_workbook":
            result = await client.move_workbook_enhanced(
                workbook_id=arguments.get("workbook_id"),
                workbook_name=arguments.get("workbook_name"),
                current_project_name=arguments.get("current_project_name"),
                target_project_id=arguments.get("target_project_id"),
                target_project_name=arguments.get("target_project_name")
            )
        elif name == "move_datasource":
            result = await client.move_datasource_enhanced(
                datasource_id=arguments.get("datasource_id"),
                datasource_name=arguments.get("datasource_name"),
                current_project_name=arguments.get("current_project_name"),
                target_project_id=arguments.get("target_project_id"),
                target_project_name=arguments.get("target_project_name")
            )
        elif name == "create_project":
            result = await client.create_project(
                name=arguments["name"],
                description=arguments.get("description"),
                parent_project_id=arguments.get("parent_project_id")
            )
        elif name == "grant_permissions":
            result = await client.grant_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                grantee_type=arguments["grantee_type"],
                grantee_id=arguments["grantee_id"],
                permissions=arguments["permissions"]
            )
        elif name == "revoke_permissions":
            result = await client.revoke_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                grantee_type=arguments["grantee_type"],
                grantee_id=arguments["grantee_id"],
                permissions=arguments["permissions"]
            )
        elif name == "list_content_permissions":
            result = await client.list_content_permissions(
                content_type=arguments["content_type"],
                content_id=arguments["content_id"]
            )
        elif name == "create_group":
            result = await client.create_group(
                name=arguments["name"],
                domain_name=arguments.get("domain_name")
            )
        elif name == "add_user_to_group":
            result = await client.add_user_to_group(
                group_id=arguments["group_id"],
                user_id=arguments["user_id"]
            )
        elif name == "remove_user_from_group":
            result = await client.remove_user_from_group(
                group_id=arguments["group_id"],
                user_id=arguments["user_id"]
            )
        elif name == "search_workbooks":
            result = await client.search_workbooks(
                name=arguments.get("name"),
                project_name=arguments.get("project_name"),
                tag=arguments.get("tag"),
                owner_name=arguments.get("owner_name")
            )
        elif name == "search_datasources":
            result = await client.search_datasources(
                name=arguments.get("name"),
                project_name=arguments.get("project_name"),
                tag=arguments.get("tag"),
                owner_name=arguments.get("owner_name"),
                datasource_type=arguments.get("datasource_type")
            )
        elif name == "search_users":
            result = await client.search_users(
                name=arguments.get("name"),
                email=arguments.get("email"),
                site_role=arguments.get("site_role")
            )
        elif name == "search_projects":
            result = await client.search_projects(
                name=arguments.get("name"),
                description=arguments.get("description")
            )
        elif name == "get_workbook_by_name":
            result = await client.get_workbook_by_name(
                workbook_name=arguments["workbook_name"],
                project_name=arguments["project_name"]
            )
        elif name == "get_datasource_by_name":
            result = await client.get_datasource_by_name(
                datasource_name=arguments["datasource_name"],
                project_name=arguments["project_name"]
            )
        elif name == "get_user_by_name":
            result = await client.get_user_by_name(
                username=arguments["username"]
            )
        elif name == "get_project_by_name":
            result = await client.get_project_by_name(
                project_name=arguments["project_name"]
            )
        elif name == "list_groups":
            result = await client.list_groups()
        elif name == "natural_language_query":
            processor = get_query_processor()
            if not processor:
                result = "Query processor not initialized. Please check OpenAI API key configuration."
            else:
                result = await processor.process_query(arguments["query"])
        # Extended workbook management
        elif name == "publish_workbook":
            result = await client.publish_workbook(
                workbook_file_path=arguments["workbook_file_path"],
                project_id=arguments["project_id"],
                workbook_name=arguments.get("workbook_name"),
                show_tabs=arguments.get("show_tabs", True),
                overwrite=arguments.get("overwrite", False),
                skip_connection_check=arguments.get("skip_connection_check", False)
            )
        elif name == "download_workbook":
            result = await client.download_workbook(
                workbook_id=arguments["workbook_id"],
                file_path=arguments["file_path"],
                include_extract=arguments.get("include_extract", True)
            )
        elif name == "get_workbook_views":
            result = await client.get_workbook_views(arguments["workbook_id"])
        elif name == "get_workbook_connections":
            result = await client.get_workbook_connections(arguments["workbook_id"])
        elif name == "refresh_workbook_now":
            result = await client.refresh_workbook_now(arguments["workbook_id"])
        # View management
        elif name == "list_views":
            result = await client.list_views(arguments.get("usage_stats", False))
        elif name == "get_view_image":
            result = await client.get_view_image(
                view_id=arguments["view_id"],
                file_path=arguments["file_path"],
                image_format=arguments.get("image_format", "png"),
                max_age=arguments.get("max_age", 1)
            )
        # Extended data source management
        elif name == "publish_datasource":
            result = await client.publish_datasource(
                datasource_file_path=arguments["datasource_file_path"],
                project_id=arguments["project_id"],
                datasource_name=arguments.get("datasource_name"),
                overwrite=arguments.get("overwrite", False)
            )
        elif name == "download_datasource":
            result = await client.download_datasource(
                datasource_id=arguments["datasource_id"],
                file_path=arguments["file_path"],
                include_extract=arguments.get("include_extract", True)
            )
        elif name == "refresh_datasource_now":
            result = await client.refresh_datasource_now(arguments["datasource_id"])
        elif name == "get_datasource_connections":
            result = await client.get_datasource_connections(arguments["datasource_id"])
        # Job and task management
        elif name == "list_jobs":
            result = await client.list_jobs(arguments.get("job_type"))
        elif name == "get_job_status":
            result = await client.get_job_status(arguments["job_id"])
        elif name == "cancel_job":
            result = await client.cancel_job(arguments["job_id"])
        # Schedule management
        elif name == "list_schedules":
            result = await client.list_schedules()
        elif name == "create_schedule":
            result = await client.create_schedule(
                name=arguments["name"],
                schedule_type=arguments["schedule_type"],
                frequency=arguments["frequency"],
                priority=arguments.get("priority", 50)
            )
        # Subscription management
        elif name == "list_subscriptions":
            result = await client.list_subscriptions()
        elif name == "create_subscription":
            result = await client.create_subscription(
                subject=arguments["subject"],
                user_id=arguments["user_id"],
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                schedule_id=arguments["schedule_id"]
            )
        # Favorites management
        elif name == "list_favorites":
            result = await client.list_favorites(arguments["user_id"])
        elif name == "add_favorite":
            result = await client.add_favorite(
                user_id=arguments["user_id"],
                content_type=arguments["content_type"],
                content_id=arguments["content_id"],
                label=arguments.get("label")
            )
        # Site administration
        elif name == "update_site":
            result = await client.update_site(
                site_name=arguments.get("site_name"),
                content_url=arguments.get("content_url"),
                admin_mode=arguments.get("admin_mode"),
                user_quota=arguments.get("user_quota"),
                storage_quota=arguments.get("storage_quota"),
                disable_subscriptions=arguments.get("disable_subscriptions")
            )
        # Tag management
        elif name == "add_tags_to_workbook":
            result = await client.add_tags_to_workbook(
                workbook_id=arguments["workbook_id"],
                tags=arguments["tags"]
            )
        elif name == "add_tags_to_datasource":
            result = await client.add_tags_to_datasource(
                datasource_id=arguments["datasource_id"],
                tags=arguments["tags"]
            )
        elif name == "remove_tags_from_workbook":
            result = await client.remove_tags_from_workbook(
                workbook_id=arguments["workbook_id"],
                tags=arguments["tags"]
            )
        # Webhook management
        elif name == "list_webhooks":
            result = await client.list_webhooks()
        elif name == "create_webhook":
            result = await client.create_webhook(
                name=arguments["name"],
                url=arguments["url"],
                event=arguments["event"]
            )
        elif name == "delete_webhook":
            result = await client.delete_webhook(arguments["webhook_id"])
        # Flow management
        elif name == "list_flows":
            result = await client.list_flows()
        # Advanced search
        elif name == "search_content":
            result = await client.search_content(
                search_term=arguments["search_term"],
                content_types=arguments.get("content_types")
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
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize Extended Tableau client from environment variables
    client = ExtendedTableauCloudClient(
        server_url=os.getenv("TABLEAU_SERVER_URL", "https://eu-west-1a.online.tableau.com"),
        site_id=os.getenv("TABLEAU_SITE_ID", "itsummit"),
        token_name=os.getenv("TABLEAU_TOKEN_NAME"),
        token_value=os.getenv("TABLEAU_TOKEN_VALUE")
    )
    
    await client.connect()
    set_tableau_client(client)
    logger.info("Connected to Tableau Cloud")
    
    # Run the MCP server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="tableau-cloud-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())