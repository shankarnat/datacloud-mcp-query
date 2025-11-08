"""
Combined ASGI server for Flask (OAuth/web) and MCP SSE endpoint.
This allows both synchronous Flask routes and asynchronous MCP SSE to coexist.
"""

import os
import logging
from a2wsgi import WSGIMiddleware
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from starlette.requests import Request

# Import the Flask app
from web_server import app as flask_app, token_store, oauth_config

# Configure logging
logger = logging.getLogger(__name__)

# Import MCP components - use FastMCP for easier SSE support
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import json

# Import query execution function
from connect_api_dc_sql import run_query

DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


def create_mcp_instance(user_id: str) -> FastMCP:
    """Create and configure a FastMCP instance for a specific user"""
    mcp = FastMCP("datacloud-mcp")

    # Store user_id in the MCP instance for access in tool functions
    mcp._user_id = user_id

    @mcp.tool(description="Executes a SQL query against Salesforce Data Cloud and returns the results")
    def query(
        sql: str = Field(description="A SQL query in the PostgreSQL dialect. Make sure to always quote all identifiers and use exact casing.")
    ):
        # Get token info for this user
        token_info = token_store.get(user_id)
        if not token_info:
            raise Exception("Not authenticated - token expired")

        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
        logger.info(f"Executing query for user {user_id}: {sql[:100]}...")
        return run_query(oauth_session, sql)

    @mcp.tool(description="Lists the available tables in Salesforce Data Cloud database")
    def list_tables() -> list[str]:
        # Get token info for this user
        token_info = token_store.get(user_id)
        if not token_info:
            raise Exception("Not authenticated - token expired")

        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
        sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{DEFAULT_LIST_TABLE_FILTER}'"
        logger.info(f"Listing tables for user {user_id}")
        result = run_query(oauth_session, sql)
        data = result.get("data", [])
        return [x[0] for x in data]

    @mcp.tool(description="Describes the columns of a table in Salesforce Data Cloud")
    def describe_table(
        table: str = Field(description="The table name")
    ) -> list[str]:
        # Get token info for this user
        token_info = token_store.get(user_id)
        if not token_info:
            raise Exception("Not authenticated - token expired")

        class SimpleOAuthSession:
            def __init__(self, token, instance_url):
                self._token = token
                self._instance_url = instance_url

            def get_token(self):
                return self._token

            def get_instance_url(self):
                return self._instance_url

        oauth_session = SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])
        sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
        logger.info(f"Describing table {table} for user {user_id}")
        result = run_query(oauth_session, sql)
        data = result.get("data", [])
        return [x[0] for x in data]

    return mcp


# Cache MCP instances by user_id to avoid recreating them for each request
mcp_instances = {}

async def handle_mcp_sse_auth(scope, receive, send):
    """
    Wrapper to handle authentication before passing to MCP SSE endpoint
    """
    # Parse query string for token
    from urllib.parse import parse_qs
    query_string = scope.get("query_string", b"").decode("utf-8")
    params = parse_qs(query_string)
    token = params.get("token", [None])[0]

    # Check authentication
    if not token or token not in token_store:
        logger.error(f"MCP SSE - authentication failed for token: {token}")
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error": "Not authenticated", "message": "Please authenticate first. Get your token from /api/get_mcp_token after logging in."}',
        })
        return

    user_id = token
    logger.info(f"MCP SSE - authenticated via token: {user_id}")

    # Get or create MCP instance for this user
    if user_id not in mcp_instances:
        mcp_instances[user_id] = create_mcp_instance(user_id)

    mcp = mcp_instances[user_id]

    # Get the FastMCP SSE ASGI app
    try:
        # FastMCP provides an SSE endpoint via mcp.get_asgi_app()
        # or we can use mcp.sse_server_params() to get the SSE transport
        mcp_sse_app = mcp.get_asgi_app(transport="sse")
        await mcp_sse_app(scope, receive, send)
    except AttributeError:
        # If get_asgi_app doesn't work, try alternative
        try:
            #Fast MCP should expose an SSE app somehow
            # Let's try calling the underlying MCP server's SSE functionality
            logger.error("FastMCP SSE integration not available")
            await send({
                "type": "http.response.start",
                "status": 503,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": b"MCP SSE endpoint is being configured. FastMCP SSE integration needs to be implemented.",
            })
        except Exception as e:
            logger.error(f"MCP SSE error: {e}", exc_info=True)
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": f"MCP Server Error: {str(e)}".encode(),
            })
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        await send({
            "type": "http.response.start",
            "status": 500,
            "headers": [[b"content-type", b"text/plain"]],
        })
        await send({
            "type": "http.response.body",
            "body": f"MCP Server Error: {str(e)}".encode(),
        })

# Convert Flask app to ASGI
flask_asgi_app = WSGIMiddleware(flask_app)

# Create the combined ASGI application
async def application(scope, receive, send):
    """
    Combined ASGI application that routes:
    - /mcp/sse -> MCP SSE handler (async)
    - everything else -> Flask (OAuth, web interface, REST API)
    """
    path = scope.get("path", "")

    if path == "/mcp/sse":
        # Route to MCP SSE auth handler
        await handle_mcp_sse_auth(scope, receive, send)
    else:
        # Route to Flask for everything else
        await flask_asgi_app(scope, receive, send)


# For local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(
        "asgi_server:application",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
