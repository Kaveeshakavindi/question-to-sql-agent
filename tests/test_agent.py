from app.graph import sql_agent
from app.database import get_schema


def test_self_healing():

    initial_state = {
        "question": "Which employees earn more than 80000?",
        "schema": get_schema(),
        "sql": "SELECT name, department FROM employees",
        "result": None,
        "error": None,
        "stacktrace": None,
        "attempts": 0,
    }

    result = sql_agent.invoke(initial_state)

    print("\nFINAL RESULT:")
    print(result)

    assert result["error"] is None
    assert result["result"] is not None