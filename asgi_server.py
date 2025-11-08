"""
Combined ASGI server for Flask (OAuth/web) and MCP SSE endpoint.
This allows both synchronous Flask routes and asynchronous MCP SSE to coexist.
"""

import os
import logging
import json
import asyncio
from typing import Dict, Any
from a2wsgi import WSGIMiddleware
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, StreamingResponse
from starlette.requests import Request

# Import the Flask app
from web_server import app as flask_app, token_store, oauth_config

# Configure logging
logger = logging.getLogger(__name__)

# Import MCP components
from mcp.server.fastmcp import FastMCP
from pydantic import Field

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


# Store message queues for active SSE connections
sse_connections: Dict[str, asyncio.Queue] = {}


class MCPJsonRpcHandler:
    """Handles MCP JSON-RPC 2.0 messages"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tools = {
            "query": {
                "name": "query",
                "description": "Executes a SQL query against Salesforce Data Cloud and returns the results",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "A SQL query in the PostgreSQL dialect. Make sure to always quote all identifiers and use exact casing."
                        }
                    },
                    "required": ["sql"]
                }
            },
            "list_tables": {
                "name": "list_tables",
                "description": "Lists the available tables in Salesforce Data Cloud database",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "describe_table": {
                "name": "describe_table",
                "description": "Describes the columns of a table in Salesforce Data Cloud",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table": {
                            "type": "string",
                            "description": "The table name"
                        }
                    },
                    "required": ["table"]
                }
            }
        }

    def get_oauth_session(self):
        """Get OAuth session for the user"""
        token_info = token_store.get(self.user_id)
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

        return SimpleOAuthSession(token_info["access_token"], token_info["instance_url"])

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC message"""
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params", {})

        try:
            if method == "initialize":
                return self.handle_initialize(msg_id, params)
            elif method == "tools/list":
                return self.handle_tools_list(msg_id)
            elif method == "tools/call":
                return await self.handle_tools_call(msg_id, params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    def handle_initialize(self, msg_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "datacloud-mcp",
                    "version": "1.0.0"
                }
            }
        }

    def handle_tools_list(self, msg_id: int) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": list(self.tools.values())
            }
        }

    async def handle_tools_call(self, msg_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32602,
                    "message": f"Unknown tool: {tool_name}"
                }
            }

        try:
            oauth_session = self.get_oauth_session()

            if tool_name == "query":
                sql = arguments.get("sql")
                result = run_query(oauth_session, sql)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }

            elif tool_name == "list_tables":
                sql = f"SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0 and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '{DEFAULT_LIST_TABLE_FILTER}'"
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                tables = [x[0] for x in data]
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"tables": tables}, indent=2)
                            }
                        ]
                    }
                }

            elif tool_name == "describe_table":
                table = arguments.get("table")
                sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
                result = run_query(oauth_session, sql)
                data = result.get("data", [])
                columns = [x[0] for x in data]
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"columns": columns}, indent=2)
                            }
                        ]
                    }
                }

        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }


async def handle_mcp_sse_auth(scope, receive, send):
    """
    Custom MCP SSE endpoint with JSON-RPC 2.0 protocol implementation
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

    # Create JSON-RPC handler for this user
    handler = MCPJsonRpcHandler(user_id)

    # Create message queue for this connection
    message_queue = asyncio.Queue()
    sse_connections[user_id] = message_queue

    async def event_generator():
        """Generate SSE events"""
        try:
            # Send initial connection established event
            yield f"event: endpoint\ndata: /mcp/message?token={token}\n\n"

            # Keep connection alive and send messages from queue
            while True:
                try:
                    # Wait for messages with timeout to send keepalive
                    message = await asyncio.wait_for(message_queue.get(), timeout=30.0)
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # Send keepalive comment
                    yield ": keepalive\n\n"
        except Exception as e:
            logger.error(f"SSE generator error: {e}", exc_info=True)
        finally:
            # Clean up connection
            if user_id in sse_connections:
                del sse_connections[user_id]

    # Send SSE response
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [
            [b"content-type", b"text/event-stream"],
            [b"cache-control", b"no-cache"],
            [b"connection", b"keep-alive"],
        ],
    })

    async for event in event_generator():
        await send({
            "type": "http.response.body",
            "body": event.encode("utf-8"),
            "more_body": True,
        })

async def handle_mcp_message(scope, receive, send):
    """
    Handle incoming MCP messages from clients (POST endpoint)
    """
    from urllib.parse import parse_qs

    # Parse query string for token
    query_string = scope.get("query_string", b"").decode("utf-8")
    params = parse_qs(query_string)
    token = params.get("token", [None])[0]

    # Check authentication
    if not token or token not in token_store:
        logger.error(f"MCP Message - authentication failed for token: {token}")
        await send({
            "type": "http.response.start",
            "status": 401,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": b'{"error": "Not authenticated"}',
        })
        return

    user_id = token

    # Read request body
    body = b""
    while True:
        message = await receive()
        if message["type"] == "http.request":
            body += message.get("body", b"")
            if not message.get("more_body", False):
                break

    try:
        # Parse JSON-RPC message
        request_data = json.loads(body.decode("utf-8"))
        logger.info(f"MCP Message received: {request_data.get('method')} from user {user_id}")

        # Create handler and process message
        handler = MCPJsonRpcHandler(user_id)
        response = await handler.handle_message(request_data)

        # Send response back via SSE if connection exists, otherwise via HTTP
        if user_id in sse_connections:
            await sse_connections[user_id].put(response)
            # Also send HTTP acknowledgment
            await send({
                "type": "http.response.start",
                "status": 202,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": b'{"status": "accepted"}',
            })
        else:
            # No SSE connection, send response directly via HTTP
            await send({
                "type": "http.response.start",
                "status": 200,
                "headers": [[b"content-type", b"application/json"]],
            })
            await send({
                "type": "http.response.body",
                "body": json.dumps(response).encode("utf-8"),
            })

    except Exception as e:
        logger.error(f"Error handling MCP message: {e}", exc_info=True)
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32700,
                "message": f"Parse error: {str(e)}"
            }
        }
        await send({
            "type": "http.response.start",
            "status": 400,
            "headers": [[b"content-type", b"application/json"]],
        })
        await send({
            "type": "http.response.body",
            "body": json.dumps(error_response).encode("utf-8"),
        })


# Convert Flask app to ASGI
flask_asgi_app = WSGIMiddleware(flask_app)

# Create the combined ASGI application
async def application(scope, receive, send):
    """
    Combined ASGI application that routes:
    - /mcp/sse -> MCP SSE handler (async)
    - /mcp/message -> MCP message handler (async)
    - everything else -> Flask (OAuth, web interface, REST API)
    """
    path = scope.get("path", "")
    method = scope.get("method", "")

    if path == "/mcp/sse":
        # Route to MCP SSE auth handler
        await handle_mcp_sse_auth(scope, receive, send)
    elif path == "/mcp/message" and method == "POST":
        # Route to MCP message handler
        await handle_mcp_message(scope, receive, send)
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
