# Claude Desktop App Configuration

This guide explains how to configure the Claude desktop app to use your Tableau Cloud MCP server.

## Setup Instructions

### 1. Locate Claude Configuration Directory

The Claude desktop app configuration file location depends on your system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### 2. Install the MCP Server Package

Make sure your MCP server is installed and accessible:

```bash
# Navigate to your project directory
cd /path/to/tableau-cloud-mcp-server

# Install the package
pip install -e .
```

### 3. Configure Claude Desktop

First, copy and customize the configuration template:

```bash
# Copy the template
cp claude_desktop_config.example.json claude_desktop_config.json

# Edit with your actual Tableau Cloud credentials
# Replace the placeholder values with your real:
# - TABLEAU_SERVER_URL (e.g., https://eu-west-1a.online.tableau.com)
# - TABLEAU_SITE_ID (your site ID)
# - TABLEAU_TOKEN_NAME (your PAT name)
# - TABLEAU_TOKEN_VALUE (your PAT value)

# IMPORTANT: Update the Python command path if needed
# The template uses /usr/bin/python3, but you may need:
# - /usr/local/bin/python3 (Homebrew)
# - /opt/homebrew/bin/python3 (M1 Mac Homebrew)
# - ~/.pyenv/shims/python (pyenv)
# - /path/to/your/venv/bin/python (virtual environment)
# Check with: which python3
#
# If using a virtual environment, make sure to:
# 1. Activate your venv: source /path/to/venv/bin/activate
# 2. Install the package: pip install -e .
# 3. Use the venv Python: /path/to/venv/bin/python
```

Then copy the configured file to the Claude configuration directory:

**macOS:**
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Claude

# Copy the configuration file
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
# Create the directory if it doesn't exist
mkdir %APPDATA%\Claude

# Copy the configuration file
copy claude_desktop_config.json %APPDATA%\Claude\claude_desktop_config.json
```

### 4. Restart Claude Desktop App

After placing the configuration file, restart the Claude desktop app to load the MCP server.

### 5. Verify Connection

Once restarted, you should be able to use commands like:

- "List all users in my Tableau Cloud site"
- "Show me all projects"
- "Move workbook [ID] to project [ID]"
- "Create a new user named [username]"

## Configuration Details

The configuration file includes:
- **Server Command**: Points to your installed MCP server
- **Environment Variables**: Your Tableau Cloud credentials
- **Server Name**: `tableau-cloud-mcp-server`

## Troubleshooting

1. **Server not found**: Ensure the MCP server package is installed in the same Python environment Claude is using
2. **Connection errors**: Verify your Tableau Cloud credentials in the configuration
3. **Permission errors**: Check that the configuration file is readable by the Claude app

## Security Note

The configuration file contains your Tableau Cloud credentials. Ensure it has appropriate file permissions:

```bash
chmod 600 ~/Library/Application\ Support/Claude/claude_desktop_config.json
```