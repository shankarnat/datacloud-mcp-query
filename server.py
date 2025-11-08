import json
import logging
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import requests
import os
from oauth import OAuthConfig, OAuthSession
from connect_api_dc_sql import run_query

# Get logger for this module
logger = logging.getLogger(__name__)


# Create an MCP server
mcp = FastMCP("Salesforce Data Cloud MCP Server")

# Global config and session - initialized lazily to avoid startup crashes
sf_org: OAuthConfig = None
oauth_session: OAuthSession = None

# Non-auth configuration
DEFAULT_LIST_TABLE_FILTER = os.getenv('DEFAULT_LIST_TABLE_FILTER', '%')


def get_oauth_session() -> OAuthSession:
    """Lazy initialization of OAuth session to avoid startup crashes"""
    global sf_org, oauth_session
    if oauth_session is None:
        sf_org = OAuthConfig.from_env()
        oauth_session = OAuthSession(sf_org)
    return oauth_session


# Add a custom route for health check / info
@mcp.custom_route("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "Salesforce Data Cloud MCP Server"}


@mcp.tool(description="Executes a SQL query and returns the results")
def query(
    sql: str = Field(
        description="A SQL query in the PostgreSQL dialect make sure to always quote all identifies and use the exact casing. To formulate the query first verify which tables and fields to use through the suggest fields tool (or if it is broken through the list tables / describe tables call). Before executing the tool provide the user a succinct summary (targeted to low code users) on the semantics of the query"),
):
    # Returns both data and metadata
    return run_query(get_oauth_session(), sql)


@mcp.tool(description="Lists the available tables in the database")
def list_tables() -> list[str]:
    sql = "SELECT c.relname AS TABLE_NAME FROM pg_catalog.pg_namespace n, pg_catalog.pg_class c LEFT JOIN pg_catalog.pg_description d ON (c.oid = d.objoid AND d.objsubid = 0  and d.classoid = 'pg_class'::regclass) WHERE c.relnamespace = n.oid AND c.relname LIKE '%s'" % DEFAULT_LIST_TABLE_FILTER
    result = run_query(get_oauth_session(), sql)
    # Extract data from the result dictionary
    data = result.get("data", [])
    return [x[0] for x in data]


@mcp.tool(description="Describes the columns of a table")
def describe_table(
    table: str = Field(description="The table name"),
) -> list[str]:
    sql = f"SELECT a.attname FROM pg_catalog.pg_namespace n JOIN pg_catalog.pg_class c ON (c.relnamespace = n.oid) JOIN pg_catalog.pg_attribute a ON (a.attrelid = c.oid) JOIN pg_catalog.pg_type t ON (a.atttypid = t.oid) LEFT JOIN pg_catalog.pg_attrdef def ON (a.attrelid = def.adrelid AND a.attnum = def.adnum) LEFT JOIN pg_catalog.pg_description dsc ON (c.oid = dsc.objoid AND a.attnum = dsc.objsubid) LEFT JOIN pg_catalog.pg_class dc ON (dc.oid = dsc.classoid AND dc.relname = 'pg_class') LEFT JOIN pg_catalog.pg_namespace dn ON (dc.relnamespace = dn.oid AND dn.nspname = 'pg_catalog') WHERE a.attnum > 0 AND NOT a.attisdropped AND c.relname='{table}'"
    result = run_query(get_oauth_session(), sql)
    # Extract data from the result dictionary
    data = result.get("data", [])
    return [x[0] for x in data]


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger.info("Starting MCP server")

    # Check if we should run in HTTP mode (for Heroku/production) or stdio mode (for local development)
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "http":
        # Heroku/production mode - use streamable HTTP via uvicorn
        import uvicorn

        port = int(os.getenv("PORT", 8000))
        host = os.getenv("HOST", "0.0.0.0")

        logger.info(f"Starting MCP server with streamable HTTP on {host}:{port}")

        # Get the Starlette ASGI app from FastMCP
        http_app = mcp.streamable_http_app()

        # Run with uvicorn - explicitly set workers=1 since we're passing app object directly
        # (Heroku sets WEB_CONCURRENCY which causes issues with app objects)
        uvicorn.run(http_app, host=host, port=port, workers=1)
    else:
        # Local development mode - use stdio
        logger.info("Starting MCP server with stdio transport")
        mcp.run()
