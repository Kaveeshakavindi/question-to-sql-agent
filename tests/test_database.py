from app.database import get_schema, execute_query


def test_schema():
    schema = get_schema()

    assert "employees" in schema
    assert "departments" in schema
    assert "projects" in schema


def test_execute_query():
    result = execute_query(
        "SELECT name FROM employees"
    )

    assert len(result) > 0
    assert "name" in result[0]