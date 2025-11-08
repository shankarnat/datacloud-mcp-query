"""
Combined ASGI server for Flask (OAuth/web) and MCP SSE endpoint.
This allows both synchronous Flask routes and asynchronous MCP SSE to coexist.
"""

import os
import logging
from a2wsgi import WSGIMiddleware
from urllib.parse import parse_qs

# Import the Flask app
from web_server import app as flask_app, token_store, oauth_config

# Configure logging
logger = logging.getLogger(__name__)

# Import MCP components
from mcp.server.sse import SseServerTransport
from mcp.server import Server
import mcp.types as types
from collections.abc import Sequence
import json

# Import query execution function
from connect_api_dc_sql import run_query

DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


def create_mcp_server(user_id: str) -> Server:
    """Create and configure an MCP server instance for a specific user"""
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
                description="Executes a SQL query against Salesforce Data Cloud and returns the results",
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
                description="Lists the available tables in Salesforce Data Cloud database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                }
            ),
            types.Tool(
                name="describe_table",
                description="Describes the columns of a table in Salesforce Data Cloud",
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
        # Get token info
        token_info = token_store.get(user_id)
        if not token_info:
            return [types.TextContent(type="text", text="Error: Not authenticated - token expired")]

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
                logger.info(f"Executing query for user {user_id}: {sql[:100]}...")
                result = run_query(oauth_session, sql)
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            elif name == "list_tables":
                sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{DEFAULT_LIST_TABLE_FILTER}'"
                logger.info(f"Listing tables for user {user_id}")
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                tables = [x[0] for x in data]
                return [types.TextContent(type="text", text=json.dumps(tables, indent=2))]

            elif name == "describe_table":
                table = arguments.get("table")
                sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
                logger.info(f"Describing table {table} for user {user_id}")
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                columns = [x[0] for x in data]
                return [types.TextContent(type="text", text=json.dumps(columns, indent=2))]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    return server


async def handle_mcp_sse(scope, receive, send):
    """Handle MCP SSE endpoint at the ASGI level"""
    # Parse query string for token
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

    # Create MCP server instance for this user
    server = create_mcp_server(user_id)

    # Create SSE transport - it IS an ASGI application
    sse = SseServerTransport("/message", server)

    try:
        # Call the SSE transport as an ASGI app
        await sse(scope, receive, send)
    except Exception as e:
        logger.error(f"MCP server error: {e}", exc_info=True)
        # Try to send error response if possible
        try:
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [[b"content-type", b"text/plain"]],
            })
            await send({
                "type": "http.response.body",
                "body": f"MCP Server Error: {str(e)}".encode(),
            })
        except:
            pass


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
        # Route to MCP SSE handler
        await handle_mcp_sse(scope, receive, send)
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
