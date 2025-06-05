#!/usr/bin/env python3
"""
HTTP/WebSocket server for Tableau Cloud MCP Server

This module provides an HTTP/WebSocket interface for the MCP server,
allowing it to be deployed on cloud platforms like Heroku.
"""

import asyncio
import logging
import os
from typing import Any, Dict

from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import StdioServerTransport
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse

from .tableau_client import TableauCloudClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tableau-mcp-http-server")

# Initialize the MCP server
mcp_server = Server("tableau-cloud-mcp-server")

# Tableau client instance
tableau_client: TableauCloudClient = None

# Import all the handlers from the main server
from .server import (
    handle_list_resources,
    handle_read_resource, 
    handle_list_tools,
    handle_call_tool,
    set_tableau_client
)

# Register all handlers with the HTTP server
mcp_server.list_resources()(handle_list_resources)
mcp_server.read_resource()(handle_read_resource)
mcp_server.list_tools()(handle_list_tools)
mcp_server.call_tool()(handle_call_tool)

# Create FastAPI app
app = FastAPI(title="Tableau Cloud MCP Server", version="0.1.0")

@app.get("/")
async def root():
    """Health check endpoint."""
    return JSONResponse({
        "status": "healthy",
        "service": "tableau-cloud-mcp-server",
        "version": "0.1.0"
    })

@app.get("/health")
async def health():
    """Detailed health check."""
    global tableau_client
    
    health_status = {
        "status": "healthy",
        "tableau_connected": tableau_client is not None
    }
    
    if tableau_client:
        try:
            # Test connection by getting site info
            await tableau_client.get_site_info()
            health_status["tableau_status"] = "connected"
        except Exception as e:
            health_status["tableau_status"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
    
    return JSONResponse(health_status)

@app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol."""
    await websocket.accept()
    
    # Create transport for this WebSocket connection
    transport = WebSocketServerTransport(websocket)
    
    async with mcp_server.run_session(transport) as session:
        await session.init()
        logger.info("MCP WebSocket session started")
        
        # Keep the session alive
        try:
            await asyncio.Future()  # Run forever
        except asyncio.CancelledError:
            logger.info("MCP WebSocket session ended")

class WebSocketServerTransport:
    """WebSocket transport for MCP server."""
    
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self._closed = False
    
    async def read_message(self):
        """Read a message from the WebSocket."""
        if self._closed:
            raise EOFError("Transport closed")
        
        try:
            data = await self.websocket.receive_text()
            return data
        except Exception as e:
            self._closed = True
            raise EOFError(f"WebSocket read error: {e}")
    
    async def write_message(self, message: str):
        """Write a message to the WebSocket."""
        if self._closed:
            raise EOFError("Transport closed")
        
        try:
            await self.websocket.send_text(message)
        except Exception as e:
            self._closed = True
            raise EOFError(f"WebSocket write error: {e}")
    
    async def close(self):
        """Close the WebSocket connection."""
        if not self._closed:
            self._closed = True
            try:
                await self.websocket.close()
            except Exception:
                pass

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
    set_tableau_client(tableau_client)
    logger.info(f"Connected to Tableau Cloud site: {site_id}")

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        await initialize_tableau_client()
        logger.info("Tableau Cloud MCP HTTP Server started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Tableau client: {e}")
        raise

def main():
    """Main entry point for the HTTP server."""
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting Tableau Cloud MCP HTTP Server on {host}:{port}")
    
    uvicorn.run(
        "tableau_mcp_server.http_server:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()