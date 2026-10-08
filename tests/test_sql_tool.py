from app.mcp_client import execute_sql


def test_execute_sql_success():
    result = execute_sql(
        "SELECT name FROM employees"
    )

    assert result["success"] is True
    assert result["error"] is None
    assert len(result["result"]) == 5


def test_execute_sql_error():
    result = execute_sql(
        "SELECT missing_column FROM employees"
    )

    assert result["success"] is False
    assert "no such column" in result["error"]
    assert result["stacktrace"] is not None


def test_execute_sql_malformed():
    result = execute_sql(
        "THIS IS NOT VALID SQL"
    )

    assert result["success"] is False
    assert result["error"] is not None
    assert result["stacktrace"] is not None