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

from flask import Flask, request, redirect, session, jsonify, render_template_string
import requests
from rfc3986 import builder as uri_builder

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


@app.route("/")
def index():
    """Home page with OAuth status and API documentation"""
    user_id = session.get("user_id")
    is_authenticated = user_id and user_id in token_store

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

            <h2>🔧 Configuration</h2>
            <p>Required environment variables:</p>
            <ul>
                <li><code>SF_CLIENT_ID</code> - Salesforce Connected App Client ID</li>
                <li><code>SF_CLIENT_SECRET</code> - Salesforce Connected App Client Secret</li>
                <li><code>HEROKU_APP_NAME</code> - Your Heroku app name (optional)</li>
                <li><code>SF_LOGIN_URL</code> - Salesforce login URL (default: login.salesforce.com)</li>
            </ul>

            <h2>📚 Documentation</h2>
            <p>This server exposes the Data Cloud MCP tools as REST API endpoints.</p>
            <p>Authenticate via OAuth 2.0 with Salesforce before making API calls.</p>
        </div>
    </body>
    </html>
    """

    from jinja2 import Template
    template = Template(html)
    return template.render(authenticated=is_authenticated)


@app.route("/oauth/login")
def oauth_login():
    """Initiate OAuth flow"""
    logger.info("Initiating OAuth login flow")

    # Mark session as permanent to persist across redirects
    session.permanent = True

    # Generate PKCE pair
    code_verifier, code_challenge = generate_pkce_pair()

    # Store code verifier in session
    session["code_verifier"] = code_verifier
    session["user_id"] = secrets.token_hex(16)

    logger.info(f"Created session for user_id: {session['user_id']}")

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
