#!/usr/bin/env python3
"""
Simple HTTP server for Tableau Cloud MCP Server

A basic HTTP server that provides Tableau Cloud administration tools
via standard HTTP endpoints, designed for Heroku deployment.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List

from .tableau_client import TableauCloudClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tableau-simple-server")

# Global tableau client
tableau_client: TableauCloudClient = None

async def initialize_tableau_client():
    """Initialize the Tableau Cloud client."""
    global tableau_client
    
    # Get configuration from environment variables
    server_url = os.getenv("TABLEAU_SERVER_URL")
    site_id = os.getenv("TABLEAU_SITE_ID") 
    token_name = os.getenv("TABLEAU_TOKEN_NAME")
    token_value = os.getenv("TABLEAU_TOKEN_VALUE")
    
    if not all([server_url, site_id, token_name, token_value]):
        raise ValueError("Missing required Tableau Cloud environment variables")
    
    # Initialize Tableau client
    tableau_client = TableauCloudClient(
        server_url=server_url,
        site_id=site_id,
        token_name=token_name,
        token_value=token_value
    )
    
    await tableau_client.connect()
    logger.info(f"Connected to Tableau Cloud site: {site_id}")

async def handle_request(path: str, query_params: Dict[str, str] = None) -> Dict[str, Any]:
    """Handle HTTP requests."""
    global tableau_client
    
    if not tableau_client:
        return {"error": "Tableau client not initialized"}
    
    try:
        if path == "/health":
            # Health check
            try:
                await tableau_client.get_site_info()
                return {
                    "status": "healthy",
                    "tableau_connected": True,
                    "service": "tableau-cloud-mcp-server"
                }
            except Exception as e:
                return {
                    "status": "degraded", 
                    "tableau_connected": False,
                    "error": str(e)
                }
        
        elif path == "/users":
            return json.loads(await tableau_client.list_users())
        
        elif path == "/projects":
            return json.loads(await tableau_client.list_projects())
        
        elif path == "/workbooks":
            return json.loads(await tableau_client.list_workbooks())
        
        elif path == "/datasources":
            return json.loads(await tableau_client.list_datasources())
        
        elif path == "/site":
            return json.loads(await tableau_client.get_site_info())
        
        elif path == "/create_user" and query_params:
            username = query_params.get("username")
            site_role = query_params.get("site_role", "Viewer")
            if not username:
                return {"error": "username parameter required"}
            
            result = await tableau_client.create_user(username, site_role)
            return json.loads(result)
        
        elif path == "/move_workbook" and query_params:
            workbook_id = query_params.get("workbook_id")
            project_id = query_params.get("project_id")
            if not workbook_id or not project_id:
                return {"error": "workbook_id and project_id parameters required"}
            
            result = await tableau_client.move_workbook(workbook_id, project_id)
            return json.loads(result)
        
        else:
            return {
                "service": "tableau-cloud-mcp-server",
                "version": "0.1.0",
                "endpoints": [
                    "/health",
                    "/users", 
                    "/projects",
                    "/workbooks",
                    "/datasources",
                    "/site",
                    "/create_user?username=<name>&site_role=<role>",
                    "/move_workbook?workbook_id=<id>&project_id=<id>"
                ]
            }
    
    except Exception as e:
        logger.error(f"Error handling request {path}: {str(e)}")
        return {"error": str(e)}

# Simple HTTP server using Python's built-in modules
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
        
        # Handle the request
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(handle_request(path, query_params))
            loop.close()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())

def main():
    """Main entry point for the simple HTTP server."""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Initialize Tableau client
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(initialize_tableau_client())
        logger.info("Tableau client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Tableau client: {e}")
        return
    finally:
        loop.close()
    
    # Start HTTP server
    server = HTTPServer((host, port), SimpleHTTPRequestHandler)
    logger.info(f"Starting Tableau Cloud HTTP Server on {host}:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()