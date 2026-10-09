from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from opentelemetry import trace

from app.agent import generate_sql, correct_sql, revise_sql
from app.reviewer_agent import review_sql
from app.mcp_client import execute_sql, get_schema
from app.telemetry import setup_telemetry, tracer

setup_telemetry()

MAX_ATTEMPTS = 3
MAX_REVIEW_ROUNDS = 2
READ_ONLY_FORBIDDEN = ("insert", "update", "delete", "drop", "alter", "create", "pragma")


tracer = trace.get_tracer("self-healing-sql-agent")


class AgentState(TypedDict):
    question: str
    schema: str
    sql: str
    result: list[dict] | None
    error: str | None
    stacktrace: str | None
    attempts: int
    review_approved: bool
    review_feedback: str | None
    review_rounds: int


def generate_sql_node(state: AgentState) -> AgentState:
    """Generate the initial SQL query."""

    sql = generate_sql(state["question"])

    return {
        **state,
        "sql": sql,
    }


def execute_sql_node(state: AgentState) -> AgentState:
    """Execute the current SQL query."""

    with tracer.start_as_current_span("sql.execute") as span:

        span.set_attribute("db.system", "sqlite")
        span.set_attribute("db.statement", state["sql"])

        execution = execute_sql(state["sql"])

        if execution["success"]:
            span.set_attribute("sql.success", True)
        else:
            span.set_attribute("sql.success", False)
            span.set_attribute(
                "exception.message",
                execution["error"],
            )
            span.set_attribute(
                "exception.stacktrace",
                execution["stacktrace"],
            )

        return {
            **state,
            "result": execution["result"],
            "error": execution["error"],
            "stacktrace": execution["stacktrace"],
        }

def correct_sql_node(state: AgentState) -> AgentState:
    """Correct the SQL using the database error."""

    corrected_sql = correct_sql(
        question=state["question"],
        sql=state["sql"],
        error=state["error"],
    )

    return {**state, "sql": corrected_sql, "attempts": state["attempts"] + 1, "review_rounds": 0}

def review_sql_node(state: AgentState) -> AgentState:
    sql = state["sql"]

    # Deterministic guardrail first: no LLM needed to block writes
    if any(kw in sql.lower().split() for kw in READ_ONLY_FORBIDDEN):
        return {
            **state,
            "review_approved": False,
            "review_feedback": "Query must be read-only (SELECT only).",
            "review_rounds": state["review_rounds"] + 1,
        }

    review = review_sql(state["question"], sql)
    feedback = "\n".join(review.issues)
    if review.suggested_fix:
        feedback += f"\nSuggested fix: {review.suggested_fix}"

    return {
        **state,
        "review_approved": review.approved,
        "review_feedback": None if review.approved else feedback,
        "review_rounds": state["review_rounds"] + 1,
    }


def revise_sql_node(state: AgentState) -> AgentState:
    revised = revise_sql(
        question=state["question"],
        sql=state["sql"],
        feedback=state["review_feedback"],
    )
    return {**state, "sql": revised}


def after_review(state: AgentState) -> str:
    # The DB is the final judge, so cap review rounds and let execution decide
    if state["review_approved"] or state["review_rounds"] >= MAX_REVIEW_ROUNDS:
        return "execute"
    return "revise"


def should_generate(state: AgentState) -> str:
    """Determine whether SQL needs to be generated."""

    if state["sql"]:
        return "execute"

    return "generate"


def should_continue(state: AgentState) -> str:
    """Decide whether to finish or attempt SQL correction."""

    if state["error"] is None:
        return "success"

    if state["attempts"] >= MAX_ATTEMPTS:
        return "failed"

    return "correct"


def build_graph():
    """Build the self-healing SQL agent graph."""

    graph = StateGraph(AgentState)

    graph.add_node("generate_sql", generate_sql_node)
    graph.add_node("execute_sql", execute_sql_node)
    graph.add_node("correct_sql", correct_sql_node)
    graph.add_node("review_sql", review_sql_node)
    graph.add_node("revise_sql", revise_sql_node)

    graph.add_conditional_edges(START, should_generate,
    {"generate": "generate_sql", "execute": "review_sql"}) # start edge

    graph.add_edge("generate_sql", "review_sql")
    graph.add_edge("revise_sql", "review_sql")
    graph.add_edge("correct_sql", "review_sql")
    graph.add_conditional_edges("review_sql", after_review,
    {"execute": "execute_sql", "revise": "revise_sql"})

    graph.add_conditional_edges("execute_sql", should_continue,
    {"success": END, "correct": "correct_sql", "failed": END,}, # end edge
    )

    return graph.compile()


sql_agent = build_graph()


def run_sql_agent(
    question: str,
    initial_sql: str | None = None,
) -> dict:
    """Run the self-healing SQL agent."""

    with tracer.start_as_current_span("agent.run") as span:

        span.set_attribute("user.question", question)

        initial_state: AgentState = {
            "question": question,
            "schema": get_schema(),
            "sql": initial_sql or "",
            "result": None,
            "error": None,
            "stacktrace": None,
            "attempts": 0,
            "review_approved": False,
            "review_feedback": None,
            "review_rounds": 0,
        }

        result = sql_agent.invoke(initial_state)

        span.set_attribute(
            "agent.attempts",
            result["attempts"],
        )

        span.set_attribute(
            "agent.success",
            result["error"] is None,
        )

        return result