# Heroku Deployment Guide

This guide walks you through deploying your Tableau Cloud MCP Server to Heroku.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Git**: Your code is already in a Git repository

## Deployment Options

### Option 1: One-Click Deploy (Recommended)

Click this button to deploy directly to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/petewhore/tableau-cloud-mcp-server)

You'll be prompted to enter your Tableau Cloud credentials:
- **TABLEAU_SERVER_URL**: Your Tableau Cloud server URL
- **TABLEAU_SITE_ID**: Your site ID (content URL)
- **TABLEAU_TOKEN_NAME**: Your Personal Access Token name
- **TABLEAU_TOKEN_VALUE**: Your Personal Access Token value

### Option 2: Manual CLI Deploy

1. **Login to Heroku**:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**:
   ```bash
   heroku create your-tableau-mcp-server
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set TABLEAU_SERVER_URL="your-tableau-server-url"
   heroku config:set TABLEAU_SITE_ID="your-site-id"
   heroku config:set TABLEAU_TOKEN_NAME="your-token-name"
   heroku config:set TABLEAU_TOKEN_VALUE="your-token-value"
   ```

4. **Deploy the code**:
   ```bash
   git push heroku main
   ```

5. **Scale the app**:
   ```bash
   heroku ps:scale web=1
   ```

## Verify Deployment

1. **Check app status**:
   ```bash
   heroku ps
   ```

2. **View logs**:
   ```bash
   heroku logs --tail
   ```

3. **Test the health endpoint**:
   ```bash
   curl https://your-app-name.herokuapp.com/health
   ```

## Configure Claude Desktop

Once deployed, update your Claude desktop configuration to use the remote server:

```json
{
  "mcpServers": {
    "tableau-cloud-mcp-server": {
      "command": "node",
      "args": ["-e", "
        const WebSocket = require('ws');
        const ws = new WebSocket('wss://your-app-name.herokuapp.com/mcp');
        ws.on('open', () => console.log('Connected to remote MCP server'));
        ws.on('message', (data) => process.stdout.write(data));
        process.stdin.on('data', (data) => ws.send(data));
      "]
    }
  }
}
```

## Cost Optimization

- **Eco Dynos**: Free tier with sleep mode (sufficient for development)
- **Basic Dynos**: $7/month with no sleep mode (recommended for production)
- **Auto-scaling**: Configure based on usage patterns

## Monitoring

1. **Heroku Dashboard**: Monitor app performance and logs
2. **Health Endpoint**: `GET /health` for status checks
3. **Tableau Connection**: Verify via health endpoint response

## Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all Tableau credentials are set
2. **Buildpack**: Python buildpack should auto-detect from requirements.txt
3. **Port Binding**: Heroku automatically sets the PORT environment variable

### Debug Commands

```bash
# Check environment variables
heroku config

# View recent logs
heroku logs --tail

# Restart the app
heroku restart

# Open app in browser
heroku open
```

## Security Notes

- Environment variables are encrypted at rest on Heroku
- Use Heroku's Config Vars for sensitive data (never commit secrets)
- Consider using Heroku's Private Spaces for enterprise deployments
- Regularly rotate your Tableau Personal Access Tokens

## Scaling

For high-availability production use:

```bash
# Scale to multiple dynos
heroku ps:scale web=2

# Upgrade to performance dynos
heroku ps:resize web=standard-1x
```