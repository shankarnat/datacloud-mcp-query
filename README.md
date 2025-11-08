# Data 360 Query MCP Server

This MCP server provides a seamless integration between Cursor and Salesforce Data Cloud (formerly known as CDP), allowing you to execute SQL queries directly from Cursor. The server handles OAuth authentication with Salesforce and provides tools for exploring and querying Data Cloud tables.

## Features

- Execute SQL queries against Salesforce Data Cloud
- List available tables in the database
- Describe table columns and structure
- Automatic OAuth2 authentication flow with Salesforce

## Adding to Cursor

1. Clone this repository to your local machine
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Connect to the MCP server in Cursor:
   - Open Cursor IDE.
   - Go to **Cursor Settings** → **MCP**.
   - Click on **Add new global MCP server**.
   - Fill in the details:
   ```json
       "mcpServers": {
         ...
        "datacloud": {
          "command": "<path to python>",
          "args": [
            "<full path to>/server.py"
          ],
          "env": {
            "SF_CLIENT_ID": "<Client Id>",
            "SF_CLIENT_SECRET": "<Client Secret>>"
          },
          "disabled": false,
          "autoApprove": ["suggest_table_and_fields", "describe_table", "list_tables"]
        }
        ...
      }
   ```
   - Enable the MCP server and click refresh which should show the tool list

## Configuration

The server requires the following environment variables:

### Required Environment Variables

- `SF_CLIENT_ID`: Your Salesforce OAuth client ID
- `SF_CLIENT_SECRET`: Your Salesforce OAuth client secret

See [Connected App Setup Guide](CONNECTED_APP_SETUP.md) for instructions on how to obtain these credentials.

### Optional Environment Variables

- `SF_LOGIN_URL`: The Salesforce login URL (default: 'login.salesforce.com')
- `SF_CALLBACK_URL`: The OAuth callback URL for the authentication flow (default: 'http://localhost:5556/Callback'). This URL must be registered in your Salesforce connected app settings. See [Connected App Setup Guide](CONNECTED_APP_SETUP.md) for detailed instructions.
- `DEFAULT_LIST_TABLE_FILTER`: Filter pattern for listing tables (default: '%'). You can use this to filter for example to known "curated" tables that all share the same prefix. You can use the SQL Like syntax to express the filters.

## Available Tools

The server provides the following tools:

1. **query**: Execute SQL queries against Data Cloud
   - Supports PostgreSQL dialect
   - Returns query results in a structured format

2. **list_tables**: List all available tables in Data Cloud
   - Filtered by `DEFAULT_LIST_TABLE_FILTER` pattern

3. **describe_table**: Get detailed information about a specific table
   - Shows column names and structure

## Authentication

The server implements an OAuth2 flow with Salesforce:
- Automatically opens a browser window for authentication
- Handles token exchange and refresh
- Maintains session for subsequent queries
- Token expires after 110 minutes and is automatically refreshed

## Deploying to Heroku

This MCP server can also be deployed to Heroku as a web service, allowing you to access it from anywhere and share it with your team.

### Prerequisites

- A Heroku account ([sign up here](https://signup.heroku.com/))
- Heroku CLI installed ([installation guide](https://devcenter.heroku.com/articles/heroku-cli))
- A Salesforce Connected App configured (see [Connected App Setup Guide](CONNECTED_APP_SETUP.md))

### Deployment Steps

1. **Clone this repository and navigate to it:**
   ```bash
   git clone <repository-url>
   cd datacloud-mcp-query
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app:**
   ```bash
   heroku create your-app-name
   ```
   Note: Replace `your-app-name` with your desired app name. Heroku will give you a URL like `https://your-app-name.herokuapp.com`

4. **Update your Salesforce Connected App callback URL:**
   - Go to your Salesforce Connected App settings
   - Add the callback URL: `https://your-app-name.herokuapp.com/oauth/callback`
   - Make sure to keep the localhost callback URL if you also want to use it locally

5. **Set environment variables on Heroku:**
   ```bash
   heroku config:set SF_CLIENT_ID="your_client_id"
   heroku config:set SF_CLIENT_SECRET="your_client_secret"
   heroku config:set HEROKU_APP_NAME="your-app-name"

   # Optional configurations
   heroku config:set SF_LOGIN_URL="login.salesforce.com"
   heroku config:set DEFAULT_LIST_TABLE_FILTER="%"
   ```

6. **Deploy to Heroku:**
   ```bash
   git push heroku main
   ```
   Or if you're on a different branch:
   ```bash
   git push heroku your-branch:main
   ```

7. **Open your app:**
   ```bash
   heroku open
   ```
   This will open your browser to `https://your-app-name.herokuapp.com`

### Using the Heroku Deployment

Once deployed, your MCP server will be accessible as a web application with the following features:

#### Web Interface

- **Home Page (`/`)**: Shows authentication status and API documentation
- **Login (`/oauth/login`)**: Initiates OAuth flow with Salesforce
- **Logout (`/oauth/logout`)**: Clears authentication session

#### REST API Endpoints

After authenticating via the web interface, you can use the following API endpoints:

1. **Execute SQL Query**
   ```bash
   POST /api/query
   Content-Type: application/json

   {
     "sql": "SELECT * FROM your_table LIMIT 10"
   }
   ```

2. **List Tables**
   ```bash
   GET /api/list_tables
   ```

3. **Describe Table**
   ```bash
   POST /api/describe_table
   Content-Type: application/json

   {
     "table": "your_table_name"
   }
   ```

#### Example API Usage with cURL

```bash
# First, authenticate in your browser by visiting:
# https://your-app-name.herokuapp.com/oauth/login

# Then make API calls (you'll need to include session cookies)
curl -X POST https://your-app-name.herokuapp.com/api/query \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your-session-cookie>" \
  -d '{"sql": "SELECT * FROM your_table LIMIT 10"}'
```

### Monitoring Your Heroku App

- **View logs:**
  ```bash
  heroku logs --tail
  ```

- **Check app status:**
  ```bash
  heroku ps
  ```

- **Access Heroku dashboard:**
  Visit [dashboard.heroku.com](https://dashboard.heroku.com/) to manage your app

### Environment Variables Reference

See `.env.example` for a complete list of configuration options.

### Troubleshooting Heroku Deployment

- **OAuth callback errors**: Ensure the callback URL in your Salesforce Connected App matches exactly: `https://your-app-name.herokuapp.com/oauth/callback`
- **App not responding**: Check logs with `heroku logs --tail` to see any errors
- **Environment variables not set**: Verify with `heroku config` that all required variables are set
- **Python version issues**: The app uses Python 3.11.14 as specified in `runtime.txt`