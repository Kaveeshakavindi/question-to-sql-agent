from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.database import get_schema
from app.telemetry import tracer
from app.prompts import (
    SQL_GENERATION_PROMPT,
    SQL_CORRECTION_PROMPT,
    SQL_REVISION_PROMPT
)

load_dotenv()


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
)


def generate_sql(question: str) -> str:
    """Generate a SQLite query from a natural-language question."""

    with tracer.start_as_current_span("llm.generate_sql") as span:

        span.set_attribute("gen_ai.request.model", "gemini-2.5-flash")
        span.set_attribute("user.question", question)

        schema = get_schema()

        prompt = SQL_GENERATION_PROMPT.format(
            schema=schema,
            question=question,
        )

        response = llm.invoke(prompt)

        sql = response.content.strip()

        span.set_attribute("generated.sql", sql)

        return sql


def correct_sql(
    question: str,
    sql: str,
    error: str,
) -> str:
    """Correct a failed SQL query using the database error."""

    with tracer.start_as_current_span("llm.correct_sql") as span:

        span.set_attribute("gen_ai.request.model", "gemini-2.5-flash")
        span.set_attribute("user.question", question)
        span.set_attribute("failed.sql", sql)
        span.set_attribute("database.error", error)

        schema = get_schema()

        prompt = SQL_CORRECTION_PROMPT.format(
            schema=schema,
            question=question,
            sql=sql,
            error=error,
        )

        response = llm.invoke(prompt)

        corrected_sql = response.content.strip()

        span.set_attribute(
            "corrected.sql",
            corrected_sql,
        )

        return corrected_sql
    
def revise_sql(
    question: str,
    sql: str,
    feedback: str,
) -> str:
    """Revise a SQL query based on the reviewer's feedback."""

    with tracer.start_as_current_span("llm.revise_sql") as span:

        span.set_attribute("gen_ai.request.model", "gemini-2.5-flash")
        span.set_attribute("user.question", question)
        span.set_attribute("original.sql", sql)
        span.set_attribute("reviewer.feedback", feedback)

        schema = get_schema()

        prompt = SQL_REVISION_PROMPT.format(
            schema=schema,
            question=question,
            sql=sql,
            feedback=feedback,
        )

        response = llm.invoke(prompt)

        revised_sql = response.content.strip()

        span.set_attribute("revised.sql", revised_sql)

        return revised_sql