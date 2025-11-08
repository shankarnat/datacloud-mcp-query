"""
Web server wrapper for the MCP server to run on Heroku.
Provides OAuth authentication flow and REST API endpoints for MCP tools.
"""

from __future__ import annotations

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional
import base64
import hashlib
import secrets

from flask import Flask, request, redirect, session, jsonify, render_template_string, Response, stream_with_context
import requests
from rfc3986 import builder as uri_builder
from mcp.server.fastmcp import FastMCP
from pydantic import Field

from oauth import OAuthConfig
from connect_api_dc_sql import run_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))

# Configure session for production HTTPS
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookie
    SESSION_COOKIE_SAMESITE='Lax',  # Allow cookie during OAuth redirects
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),  # Session expires after 2 hours
)

# Global OAuth config
oauth_config: Optional[OAuthConfig] = None

# In-memory token storage (for production, use Redis or a database)
token_store = {}

# Create MCP server instance
mcp = FastMCP("DataCloud MCP Server")

# Non-auth configuration for MCP tools
DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


def get_app_url():
    """Get the application URL from environment or request"""
    heroku_app_name = os.getenv("HEROKU_APP_NAME")
    if heroku_app_name:
        return f"https://{heroku_app_name}.herokuapp.com"

    # Fallback to request-based URL
    return request.url_root.rstrip('/')


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge for OAuth flow"""
    code_verifier = (
        base64.urlsafe_b64encode(secrets.token_bytes(32))
        .decode("utf-8")
        .rstrip("=")
    )

    challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = (
        base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
    )

    return code_verifier, code_challenge


# Define MCP tools
@mcp.tool(description="Executes a SQL query and returns the results")
def query(
    sql: str = Field(
        description="A SQL query in the PostgreSQL dialect. Make sure to always quote all identifiers and use exact casing. To formulate the query, first verify which tables and fields to use through the list_tables or describe_table tools."
    ),
):
    """Execute SQL query against Data Cloud"""
    # Get current user's token
    user_id = session.get("user_id")
    if not user_id or user_id not in token_store:
        raise Exception("Not authenticated. Please authenticate first.")

    token_info = token_store[user_id]

    # Create simple OAuth session
    class SimpleOAuthSession:
        def __init__(self, token, instance_url):
            self._token = token
            self._instance_url = instance_url

        def get_token(self):
            return self._token

        def get_instance_url(self):
            return self._instance_url

    oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
    return run_query(oauth_session, sql)


@mcp.tool(description="Lists the available tables in the database")
def list_tables() -> list[str]:
    """List all available tables in Data Cloud"""
    # Get current user's token
    user_id = session.get("user_id")
    if not user_id or user_id not in token_store:
        raise Exception("Not authenticated. Please authenticate first.")

    token_info = token_store[user_id]

    sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{DEFAULT_LIST_TABLE_FILTER}'"

    class SimpleOAuthSession:
        def __init__(self, token, instance_url):
            self._token = token
            self._instance_url = instance_url

        def get_token(self):
            return self._token

        def get_instance_url(self):
            return self._instance_url

    oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
    result = run_query(oauth_session, sql)
    data = result.get("data", [])
    return [x[0] for x in data]


@mcp.tool(description="Describes the columns of a table")
def describe_table(
    table: str = Field(description="The table name"),
) -> list[str]:
    """Get column information for a specific table"""
    # Get current user's token
    user_id = session.get("user_id")
    if not user_id or user_id not in token_store:
        raise Exception("Not authenticated. Please authenticate first.")

    token_info = token_store[user_id]

    sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"

    class SimpleOAuthSession:
        def __init__(self, token, instance_url):
            self._token = token
            self._instance_url = instance_url

        def get_token(self):
            return self._token

        def get_instance_url(self):
            return self._instance_url

    oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
    result = run_query(oauth_session, sql)
    data = result.get("data", [])
    return [x[0] for x in data]


@app.route("/")
def index():
    """Home page with OAuth status and API documentation"""
    user_id = session.get("user_id")
    is_authenticated = user_id and user_id in token_store

    # Debug logging
    logger.info(f"Index page - user_id from session: {user_id}")
    logger.info(f"Index page - user in token_store: {user_id in token_store if user_id else False}")
    logger.info(f"Index page - is_authenticated: {is_authenticated}")
    logger.info(f"Index page - token_store keys: {list(token_store.keys())}")

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Cloud MCP Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 { color: #0176d3; }
            .status {
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
                font-weight: bold;
            }
            .authenticated { background-color: #d4edda; color: #155724; }
            .not-authenticated { background-color: #f8d7da; color: #721c24; }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 5px;
                background-color: #0176d3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }
            .button:hover { background-color: #014486; }
            .endpoint {
                background-color: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #0176d3;
                border-radius: 3px;
            }
            code {
                background-color: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            pre {
                background-color: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌐 Data Cloud MCP Server</h1>
            <p>Model Context Protocol server for Salesforce Data Cloud SQL queries</p>

            <div class="status {{ 'authenticated' if authenticated else 'not-authenticated' }}">
                {% if authenticated %}
                    ✓ Authenticated with Salesforce
                {% else %}
                    ✗ Not authenticated
                {% endif %}
            </div>

            <div>
                {% if not authenticated %}
                    <a href="/oauth/login" class="button">🔐 Login with Salesforce</a>
                {% else %}
                    <a href="/oauth/logout" class="button">🚪 Logout</a>
                {% endif %}
            </div>

            <h2>📡 API Endpoints</h2>

            <div class="endpoint">
                <strong>POST /api/query</strong>
                <p>Execute a SQL query against Data Cloud</p>
                <pre><code>{
  "sql": "SELECT * FROM table_name LIMIT 10"
}</code></pre>
            </div>

            <div class="endpoint">
                <strong>GET /api/list_tables</strong>
                <p>List all available tables in Data Cloud</p>
            </div>

            <div class="endpoint">
                <strong>POST /api/describe_table</strong>
                <p>Get column information for a specific table</p>
                <pre><code>{
  "table": "table_name"
}</code></pre>
            </div>

            <h2>🔌 MCP Integration (ChatGPT)</h2>

            <div class="endpoint">
                <strong>GET /mcp/sse</strong>
                <p>Model Context Protocol (MCP) Server-Sent Events endpoint for ChatGPT</p>
                {% if authenticated %}
                    <p style="color: #155724;">✓ You are authenticated! You can use this endpoint in ChatGPT.</p>
                    <p><strong>Get your MCP URL with authentication token:</strong></p>
                    <a href="/api/get_mcp_token" class="button" target="_blank">📋 Get MCP Token for ChatGPT</a>
                    <p style="margin-top: 10px; font-size: 14px;">Click the button above to get your personalized MCP URL with authentication token</p>
                {% else %}
                    <p style="color: #721c24;">⚠ You must login first before using the MCP endpoint.</p>
                {% endif %}
                <p><strong>Available Tools:</strong></p>
                <ul>
                    <li><code>query</code> - Execute SQL queries</li>
                    <li><code>list_tables</code> - List available tables</li>
                    <li><code>describe_table</code> - Get table schema</li>
                </ul>
            </div>

            <h2>🔧 Configuration</h2>
            <p>Required environment variables:</p>
            <ul>
                <li><code>SF_CLIENT_ID</code> - Salesforce Connected App Client ID</li>
                <li><code>SF_CLIENT_SECRET</code> - Salesforce Connected App Client Secret</li>
                <li><code>HEROKU_APP_NAME</code> - Your Heroku app name (optional)</li>
                <li><code>SF_LOGIN_URL</code> - Salesforce login URL (default: login.salesforce.com)</li>
            </ul>

            <h2>📚 Documentation</h2>
            <p>This server exposes the Data Cloud MCP tools via:</p>
            <ul>
                <li><strong>REST API</strong> - For custom integrations</li>
                <li><strong>MCP SSE</strong> - For ChatGPT and other MCP clients</li>
            </ul>
            <p>Authenticate via OAuth 2.0 with Salesforce before making API calls.</p>
        </div>
    </body>
    </html>
    """

    from jinja2 import Template
    template = Template(html)
    return template.render(authenticated=is_authenticated, request=request)


@app.route("/oauth/login")
def oauth_login():
    """Initiate OAuth flow"""
    logger.info("Initiating OAuth login flow")

    # Mark session as permanent to persist across redirects
    session.permanent = True

    # Check if already authenticated
    existing_user_id = session.get("user_id")
    if existing_user_id and existing_user_id in token_store:
        logger.info(f"User {existing_user_id} already authenticated, redirecting to home")
        return redirect("/")

    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Reuse existing user_id if present, otherwise create new one
    if "user_id" not in session:
        session["user_id"] = secrets.token_hex(16)
        logger.info(f"Created NEW session for user_id: {session['user_id']}")
    else:
        # Clear any old token for this user_id before restarting login
        if session["user_id"] in token_store:
            del token_store[session["user_id"]]
        logger.info(f"Reusing session for user_id: {session['user_id']}, cleared old token")

    # Store code verifier in session
    session["code_verifier"] = code_verifier

    # Build authorization URL
    app_url = get_app_url()
    redirect_uri = f"{app_url}/oauth/callback"

    login_url = f"https://{oauth_config.login_root}/services/oauth2/authorize"

    auth_url = (
        uri_builder.URIBuilder(path=login_url)
        .add_query_from({
            "client_id": oauth_config.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "api cdp_query_api cdp_profile_api",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        })
        .finalize()
        .unsplit()
    )

    logger.info(f"Redirecting to Salesforce for authorization")
    return redirect(auth_url)


@app.route("/oauth/callback")
def oauth_callback():
    """Handle OAuth callback from Salesforce"""
    logger.info("Received OAuth callback")

    # Get authorization code from query params
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        error_description = request.args.get("error_description", "Unknown error")
        logger.error(f"OAuth error: {error} - {error_description}")
        return f"<h1>Authentication Error</h1><p>{error}: {error_description}</p>", 400

    if not code:
        logger.error("No authorization code received")
        return "<h1>Authentication Error</h1><p>No authorization code received</p>", 400

    # Get code verifier from session
    code_verifier = session.get("code_verifier")
    user_id = session.get("user_id")

    logger.info(f"Callback - user_id in session: {user_id}, has code_verifier: {bool(code_verifier)}")

    if not code_verifier:
        logger.error("No code verifier found in session - session may have expired or cookies not set")
        return "<h1>Authentication Error</h1><p>Session expired. Please try again.</p>", 400

    # Exchange code for token
    app_url = get_app_url()
    redirect_uri = f"{app_url}/oauth/callback"
    token_url = f"https://{oauth_config.login_root}/services/oauth2/token"

    try:
        response = requests.post(
            token_url,
            {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": oauth_config.client_id,
                "client_secret": oauth_config.client_secret,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
            headers={"Accept": "application/json"},
            timeout=30,
        )

        response.raise_for_status()
        auth_info = response.json()

        # Store token in memory (for production, use Redis or a database)
        token_store[user_id] = {
            "access_token": auth_info["access_token"],
            "instance_url": auth_info["instance_url"],
            "expires_at": datetime.now() + timedelta(minutes=110),
        }

        logger.info(f"Successfully authenticated user {user_id}")
        return redirect("/")

    except requests.exceptions.RequestException as e:
        logger.error(f"Token exchange failed: {e}")
        return f"<h1>Authentication Error</h1><p>Failed to exchange code for token: {e}</p>", 500


@app.route("/oauth/logout")
def oauth_logout():
    """Logout and clear session"""
    user_id = session.get("user_id")
    if user_id and user_id in token_store:
        del token_store[user_id]
    session.clear()
    logger.info("User logged out")
    return redirect("/")


def get_user_token():
    """Get the current user's access token"""
    user_id = session.get("user_id")
    if not user_id or user_id not in token_store:
        return None, None

    token_info = token_store[user_id]

    # Check if token is expired
    if datetime.now() > token_info["expires_at"]:
        del token_store[user_id]
        return None, None

    return token_info["access_token"], token_info["instance_url"]


@app.route("/api/query", methods=["POST"])
def api_query():
    """Execute a SQL query"""
    token, instance_url = get_user_token()
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    sql = data.get("sql")

    if not sql:
        return jsonify({"error": "Missing 'sql' parameter"}), 400

    try:
        # Create a simple OAuth session object
        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token, instance_url)
        result = run_query(oauth_session, sql)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/list_tables", methods=["GET"])
def api_list_tables():
    """List all tables"""
    token, instance_url = get_user_token()
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    try:
        filter_pattern = os.getenv("DEFAULT_LIST_TABLE_FILTER", "%")
        sql = f"""
            SELECT c.relname as table_name
            FROM pg_catalog.pg_namespace n
            JOIN pg_catalog.pg_class c ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
            AND c.relkind = 'r'
            AND c.relname LIKE '{filter_pattern}'
            ORDER BY c.relname
        """

        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token, instance_url)
        result = run_query(oauth_session, sql)

        # Extract table names from result
        tables = [row["table_name"] for row in result.get("data", [])]

        return jsonify({"tables": tables})

    except Exception as e:
        logger.error(f"List tables failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/describe_table", methods=["POST"])
def api_describe_table():
    """Describe a table's columns"""
    token, instance_url = get_user_token()
    if not token:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json()
    table_name = data.get("table")

    if not table_name:
        return jsonify({"error": "Missing 'table' parameter"}), 400

    try:
        sql = f"""
            SELECT a.attname as column_name
            FROM pg_catalog.pg_namespace n
            JOIN pg_catalog.pg_class c ON n.oid = c.relnamespace
            JOIN pg_catalog.pg_attribute a ON c.oid = a.attrelid
            WHERE n.nspname = 'public'
            AND c.relname = '{table_name}'
            AND a.attnum > 0
            AND NOT a.attisdropped
            ORDER BY a.attnum
        """

        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token, instance_url)
        result = run_query(oauth_session, sql)

        # Extract column names from result
        columns = [row["column_name"] for row in result.get("data", [])]

        return jsonify({"columns": columns})

    except Exception as e:
        logger.error(f"Describe table failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/debug/session")
def debug_session():
    """Debug endpoint to check session status"""
    user_id = session.get("user_id")
    code_verifier = session.get("code_verifier")

    return jsonify({
        "session_user_id": user_id,
        "has_code_verifier": bool(code_verifier),
        "user_in_token_store": user_id in token_store if user_id else False,
        "token_store_users": list(token_store.keys()),
        "session_permanent": session.permanent,
        "flask_secret_key_set": bool(os.getenv("FLASK_SECRET_KEY")),
    })


@app.route("/debug/clear_all_tokens")
def debug_clear_all_tokens():
    """Debug endpoint to clear all tokens and sessions (use with caution!)"""
    global token_store
    old_count = len(token_store)
    token_store.clear()
    session.clear()
    logger.info(f"Cleared all tokens ({old_count} entries) and current session")
    return jsonify({
        "message": f"Cleared {old_count} tokens and current session",
        "token_store_now_empty": len(token_store) == 0,
    })


@app.route("/api/get_mcp_token")
def get_mcp_token():
    """
    Get MCP authentication token for ChatGPT integration

    This endpoint returns your user_id which can be used as a token
    in the MCP SSE endpoint URL for ChatGPT.
    """
    user_id = session.get("user_id")
    if not user_id or user_id not in token_store:
        return jsonify({
            "error": "Not authenticated",
            "message": "Please login first at /oauth/login"
        }), 401

    app_url = get_app_url()
    mcp_url = f"{app_url}/mcp/sse?token={user_id}"

    return jsonify({
        "token": user_id,
        "mcp_url": mcp_url,
        "instructions": [
            "Copy the mcp_url below",
            "Go to ChatGPT → Settings → Company Knowledge or MCP Connectors",
            "Add a new MCP server with this URL",
            "The token is embedded in the URL and will authenticate your requests"
        ],
        "expires": "Token is valid for 2 hours (session lifetime)"
    })


@app.route("/mcp/sse")
def mcp_sse():
    """
    MCP Server-Sent Events endpoint for ChatGPT MCP connector

    Authentication:
    - Via session cookie (from web login), OR
    - Via ?token=<auth_token> query parameter

    Usage in ChatGPT:
    Add this URL: https://your-app-name.herokuapp.com/mcp/sse?token=<your_token>
    """
    # Check authentication - either session or token
    user_id = None

    # Try session-based auth first
    session_user_id = session.get("user_id")
    if session_user_id and session_user_id in token_store:
        user_id = session_user_id
        logger.info(f"MCP SSE - authenticated via session: {user_id}")
    else:
        # Try token-based auth
        auth_token = request.args.get("token") or request.headers.get("X-Auth-Token")
        if auth_token and auth_token in token_store:
            user_id = auth_token
            logger.info(f"MCP SSE - authenticated via token: {user_id}")

    if not user_id:
        logger.error("MCP SSE - authentication failed")
        return jsonify({
            "error": "Not authenticated",
            "message": "Please authenticate first. Get your token from /api/get_mcp_token after logging in."
        }), 401

    logger.info(f"MCP SSE connection requested for user: {user_id}")

    # Import SSE transport from MCP SDK
    from mcp.server.sse import SseServerTransport
    from mcp.server import Server
    import mcp.types as types
    import asyncio
    from collections.abc import Sequence

    # Create server instance
    server = Server("datacloud-mcp")

    # Register list_resources handler
    @server.list_resources()
    async def handle_list_resources() -> list[types.Resource]:
        return []

    # Register list_prompts handler
    @server.list_prompts()
    async def handle_list_prompts() -> list[types.Prompt]:
        return []

    # Register list_tools handler
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="query",
                description="Executes a SQL query and returns the results",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "A SQL query in the PostgreSQL dialect. Make sure to always quote all identifiers and use exact casing."
                        }
                    },
                    "required": ["sql"]
                }
            ),
            types.Tool(
                name="list_tables",
                description="Lists the available tables in the database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                }
            ),
            types.Tool(
                name="describe_table",
                description="Describes the columns of a table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "The table name"
                        }
                    },
                    "required": ["table"]
                }
            ),
        ]

    # Register call_tool handler
    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict
    ) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        # Get token info from session
        token_info = token_store.get(user_id)
        if not token_info:
            return [types.TextContent(type="text", text="Error: Not authenticated")]

        try:
            # Create OAuth session
            class SimpleOAuthSession:
                def __init__(self, token, instance_url):
                    self._token = token
                    self._instance_url = instance_url

                def get_token(self):
                    return self._token

                def get_instance_url(self):
                    return self._instance_url

            oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])

            # Execute the requested tool
            if name == "query":
                sql = arguments.get("sql")
                result = run_query(oauth_session, sql)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "list_tables":
                sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{DEFAULT_LIST_TABLE_FILTER}'"
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                tables = [x[0] for x in data]
                return [types.TextContent(type="text", text=json.dumps(tables, indent=2))]

            elif name == "describe_table":
                table = arguments.get("table")
                sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                columns = [x[0] for x in data]
                return [types.TextContent(type="text", text=json.dumps(columns, indent=2))]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Create SSE transport
    async def run_sse():
        async with SseServerTransport("/messages") as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    # Run the async server
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(run_sse())
        finally:
            loop.close()

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


def init_app():
    """Initialize the application"""
    global oauth_config

    # Load OAuth config from environment
    client_id = os.getenv("SF_CLIENT_ID")
    client_secret = os.getenv("SF_CLIENT_SECRET")
    login_root = os.getenv("SF_LOGIN_URL", "login.salesforce.com")

    if not client_id or not client_secret:
        logger.error("Missing required environment variables: SF_CLIENT_ID and/or SF_CLIENT_SECRET")
        raise ValueError("SF_CLIENT_ID and SF_CLIENT_SECRET must be set")

    oauth_config = OAuthConfig(
        client_id=client_id,
        client_secret=client_secret,
        login_root=login_root,
        redirect_uri="",  # Will be set dynamically
    )

    logger.info("Application initialized successfully")


# Initialize on module load
init_app()


if __name__ == "__main__":
    # Run locally for testing
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
