from app.mcp_client import execute_sql, get_schema


print("\n=== CLIENT SCHEMA ===")
print(get_schema())


print("\n=== CLIENT SQL ===")
print(
    execute_sql(
        "SELECT name, salary FROM employees"
    )
)