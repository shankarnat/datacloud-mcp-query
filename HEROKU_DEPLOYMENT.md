# Heroku Deployment Guide for ChatGPT Enterprise Knowledge

This guide walks you through deploying the Salesforce Data Cloud MCP server to Heroku and configuring it to work with ChatGPT Enterprise Knowledge.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Heroku CLI**: Install from [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
3. **Salesforce Connected App**: Follow [CONNECTED_APP_SETUP.md](CONNECTED_APP_SETUP.md) to create one
4. **ChatGPT Enterprise/Edu/Business Account**: Required for MCP server integration

## Step 1: Get Salesforce Refresh Token

Before deploying to Heroku, you need to obtain a refresh token from Salesforce:

### 1.1 Set up environment variables locally

Create a `.env` file (or set environment variables):

```bash
SF_CLIENT_ID=your_salesforce_client_id
SF_CLIENT_SECRET=your_salesforce_client_secret
SF_LOGIN_URL=login.salesforce.com
```

### 1.2 Run the server locally to get refresh token

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server (it will use stdio mode by default)
python server.py
```

The server will:
1. Open your browser for Salesforce authentication
2. After you log in, check the server logs
3. Look for: `Received refresh token - store this in SF_REFRESH_TOKEN env var for production use`
4. Copy the refresh token from your browser callback URL or check Salesforce session

**Important**: To ensure your Connected App returns a refresh token, make sure:
- In Salesforce Connected App settings, enable "Perform requests at any time (refresh_token, offline_access)"
- The OAuth scope includes `refresh_token` or `offline_access`

### 1.3 Test refresh token locally

Set the refresh token and test:

```bash
export SF_REFRESH_TOKEN=your_refresh_token_here
export MCP_TRANSPORT=http
export PORT=8000
python server.py
```

Visit `http://localhost:8000/health` to verify it's working.

## Step 2: Deploy to Heroku

### 2.1 Create Heroku App

```bash
# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-datacloud-mcp-server

# Or if you want a specific app name:
# heroku create my-company-datacloud-mcp
```

### 2.2 Set Environment Variables

```bash
# Required: Salesforce credentials
heroku config:set SF_CLIENT_ID=your_salesforce_client_id
heroku config:set SF_CLIENT_SECRET=your_salesforce_client_secret
heroku config:set SF_REFRESH_TOKEN=your_refresh_token_here

# Optional: Salesforce configuration
heroku config:set SF_LOGIN_URL=login.salesforce.com

# Required: MCP server configuration
heroku config:set MCP_TRANSPORT=http
heroku config:set MCP_PATH=/mcp

# Optional: Data Cloud configuration
heroku config:set DEFAULT_LIST_TABLE_FILTER=%
```

### 2.3 Deploy to Heroku

```bash
# Add files to git if not already done
git add .
git commit -m "Prepare for Heroku deployment"

# Deploy to Heroku
git push heroku main

# Or if you're on a different branch:
# git push heroku your-branch:main
```

### 2.4 Verify Deployment

```bash
# Check logs
heroku logs --tail

# Test the health endpoint
curl https://your-app-name.herokuapp.com/health

# The MCP endpoint should be at:
# https://your-app-name.herokuapp.com/mcp
```

## Step 3: Configure ChatGPT Enterprise Knowledge

### 3.1 Enable Developer Mode (if not already enabled)

1. Go to ChatGPT Settings
2. For Enterprise/Edu/Business: Contact your workspace admin
3. For Plus/Pro: Enable Developer Mode in settings

### 3.2 Create Custom MCP Connector

1. **Open ChatGPT** and go to **Settings**
2. Navigate to **Connectors** or **Deep Research** settings
3. Click **Add Custom Connector** or **Configure MCP Server**
4. Fill in the details:

```json
{
  "name": "Salesforce Data Cloud",
  "description": "Query Salesforce Data Cloud using SQL",
  "url": "https://your-app-name.herokuapp.com/mcp",
  "transport": "streamable-http"
}
```

### 3.3 Configure Authentication (if required)

ChatGPT may require authentication headers. If needed, you can add:

- **Custom Headers**: None required if your Heroku app is public
- **API Key**: Optional, see Step 4 for adding API key protection

### 3.4 Test the Connector

1. In ChatGPT, start a new conversation
2. Enable your "Salesforce Data Cloud" connector
3. Try a query like:
   - "List all available tables in Data Cloud"
   - "Show me the columns in the [table_name] table"
   - "Query the customer data from [table_name]"

## Step 4: Add API Key Protection (Recommended)

For production use, add API key authentication:

### 4.1 Create server wrapper with authentication

Create a new file `auth_server.py`:

```python
import os
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

API_KEY = os.getenv("API_KEY", "your-secure-api-key")

@app.api_route("/mcp", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def mcp_proxy(
    request: Request,
    x_api_key: str = Header(None)
):
    """Proxy requests to MCP server with API key authentication"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Forward to actual MCP server (running on different port or process)
    # This is a simplified example
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=f"http://localhost:8001/mcp",
            content=await request.body(),
            headers=dict(request.headers)
        )
        return StreamingResponse(
            response.aiter_bytes(),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 4.2 Set API key in Heroku

```bash
heroku config:set API_KEY=your-very-secure-random-api-key
```

### 4.3 Configure ChatGPT with API key

In ChatGPT connector settings, add custom header:
- Header Name: `X-API-Key`
- Header Value: `your-very-secure-random-api-key`

## Step 5: Monitoring and Maintenance

### View Logs

```bash
# Real-time logs
heroku logs --tail

# Recent logs
heroku logs --num 500
```

### Scale Dynos

```bash
# Use hobby or professional dynos for production
heroku ps:scale web=1:standard-1x
```

### Update Refresh Token

If your refresh token expires:

```bash
# Run locally to get new refresh token
python server.py

# Update Heroku config
heroku config:set SF_REFRESH_TOKEN=new_refresh_token_here

# Restart app
heroku restart
```

## Troubleshooting

### Issue: "OAuth authentication failed"

- **Solution**: Verify `SF_REFRESH_TOKEN` is set correctly
- Check Heroku logs: `heroku logs --tail`
- Ensure Connected App has correct permissions

### Issue: "Connection refused" from ChatGPT

- **Solution**: Verify the Heroku app is running: `heroku ps`
- Check the URL is correct (including `/mcp` path)
- Test endpoint manually: `curl https://your-app.herokuapp.com/health`

### Issue: "Token refresh failed"

- **Solution**: Refresh token may have expired
- Re-run local OAuth flow to get new refresh token
- Update Heroku config with new token

### Issue: MCP connector not appearing in ChatGPT

- **Solution**: Verify you have Enterprise/Edu/Business access
- Check Developer Mode is enabled
- Contact your workspace admin for permissions

## Security Best Practices

1. **Always use HTTPS**: Heroku provides this automatically
2. **Rotate credentials regularly**: Update refresh tokens periodically
3. **Use API key authentication**: Add custom auth layer (Step 4)
4. **Monitor logs**: Regularly check for unusual activity
5. **Limit table access**: Use `DEFAULT_LIST_TABLE_FILTER` to restrict accessible tables
6. **Review ChatGPT queries**: Monitor what queries ChatGPT is executing

## Cost Considerations

### Heroku Costs

- **Eco Dyno**: $5/month (suitable for testing)
- **Basic Dyno**: $7/month (better for production)
- **Standard Dynos**: $25-$500/month (production with autoscaling)

### Salesforce Data Cloud Costs

- Check your Salesforce Data Cloud query limits
- Monitor query volume in Salesforce

## Next Steps

1. **Add more tools**: Extend the MCP server with additional Salesforce Data Cloud features
2. **Implement caching**: Add Redis for query result caching
3. **Add monitoring**: Set up Heroku metrics and alerting
4. **Create documentation**: Document your Data Cloud schema for ChatGPT

## Support

- **Heroku Issues**: Check [Heroku Dev Center](https://devcenter.heroku.com/)
- **MCP Protocol**: See [Model Context Protocol docs](https://modelcontextprotocol.io/)
- **ChatGPT Connectors**: Contact OpenAI Enterprise support
- **This Project**: Open an issue on GitHub
