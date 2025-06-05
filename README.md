# Tableau Cloud MCP Server

An MCP (Model Context Protocol) server that provides tools for administering Tableau Cloud deployments. This server enables automated management of users, content, and permissions through a standardized interface.

## Features

### Content Management
- Move workbooks between projects
- Move data sources between projects
- List all workbooks and data sources
- Create new projects

### User Management
- Create new users
- Update user properties (site role, authentication)
- Delete users
- List all users

### Permission Management
- Grant permissions to users/groups on content
- Revoke permissions from users/groups
- List all permissions for content items

### Group Management
- Create new groups
- Add users to groups
- Remove users from groups

### Site Administration
- View site information and configuration
- List all projects

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Configuration

The server connects to your Tableau Cloud site using Personal Access Token authentication. Configure your connection using environment variables:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Tableau Cloud credentials:
   ```bash
   TABLEAU_SERVER_URL=https://your-region.online.tableau.com
   TABLEAU_SITE_ID=your-site-id
   TABLEAU_TOKEN_NAME=your-token-name
   TABLEAU_TOKEN_VALUE=your-token-value
   ```

3. The server will automatically load these environment variables on startup.

## Usage

### Option 1: Heroku Deployment (Recommended)
Deploy to Heroku to avoid local environment issues:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/petewhore/tableau-cloud-mcp-server)

See [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md) for detailed instructions.

### Option 2: Local Development
Run the MCP server locally:

```bash
python -m tableau_mcp_server.server
```

### Claude Desktop App Integration
To use this MCP server with the Claude desktop app:

**For Heroku deployment**: See [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md)
**For local setup**: See [CLAUDE_SETUP.md](CLAUDE_SETUP.md)

Quick local setup:
1. Copy and customize `claude_desktop_config.example.json` with your credentials
2. Place the configured file in your Claude app configuration directory  
3. Restart Claude desktop app
4. Start using Tableau Cloud commands in Claude!

## Available Tools

### User Management
- `create_user` - Create a new user
- `update_user` - Update user properties
- `delete_user` - Remove a user

### Content Management  
- `move_workbook` - Move workbook to different project
- `move_datasource` - Move data source to different project
- `create_project` - Create a new project

### Permission Management
- `grant_permissions` - Grant permissions to user/group
- `revoke_permissions` - Revoke permissions from user/group  
- `list_content_permissions` - List all permissions for content

### Group Management
- `create_group` - Create a new group
- `add_user_to_group` - Add user to group
- `remove_user_from_group` - Remove user from group

## Available Resources

- `tableau://site/info` - Site configuration and details
- `tableau://users/list` - List of all users
- `tableau://projects/list` - List of all projects  
- `tableau://workbooks/list` - List of all workbooks
- `tableau://datasources/list` - List of all data sources

## Security

This server uses Personal Access Token authentication for secure access to Tableau Cloud. Ensure your tokens are kept secure and follow Tableau Cloud security best practices.

## Requirements

- Python 3.8+
- Tableau Cloud site with API access
- Personal Access Token with appropriate permissions