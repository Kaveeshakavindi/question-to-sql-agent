from mcp.server import MCPServer

from app.database import execute_query, get_schema
import traceback

mcp = MCPServer("sql-server")


@mcp.tool()
def get_database_schema() -> str:
    """Return the schema of the SQLite database."""
    return get_schema()


@mcp.tool()
def execute_sql(sql: str) -> dict:
    """Execute a SQL query against the SQLite database."""
    try:
        result = execute_query(sql)

        return {
            "success": True,
            "sql": sql,
            "result": result,
            "error": None,
            "stacktrace": None,
        }

    except Exception as e:
        return {
            "success": False,
            "sql": sql,
            "result": None,
            "error": str(e),
            "stacktrace": traceback.format_exc(),
        }


if __name__ == "__main__":
    mcp.run()