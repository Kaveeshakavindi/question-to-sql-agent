# 09/10/2026

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

from app.database import get_schema
from app.telemetry import tracer
from app.prompts import SQL_REVIEW_PROMPT


class Review(BaseModel):
    approved: bool
    issues: list[str] = Field(default_factory=list)
    suggested_fix: str | None = None


# Different role, ideally a different model/temperature than the writer
reviewer_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
).with_structured_output(Review)


def review_sql(question: str, sql: str) -> Review:
    with tracer.start_as_current_span("llm.review_sql") as span:
        span.set_attribute("user.question", question)
        span.set_attribute("reviewed.sql", sql)

        prompt = SQL_REVIEW_PROMPT.format(
            schema=get_schema(),
            question=question,
            sql=sql,
        )

        review = reviewer_llm.invoke(prompt)

        span.set_attribute("review.approved", review.approved)
        span.set_attribute("review.issues", "; ".join(review.issues))
        return review