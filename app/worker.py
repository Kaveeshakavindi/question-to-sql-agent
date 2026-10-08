from app.graph import run_sql_agent
from arq.connections import RedisSettings


async def run_agent_job(ctx, question: str, initial_sql: str | None = None):
    result = run_sql_agent(
        question=question,
        initial_sql=initial_sql,
    )

    if result["error"] is not None:
        raise RuntimeError(
            f"SQL agent failed after {result['attempts']} attempts: "
            f"{result['error']}"
        )

    return result


class WorkerSettings:
    functions = [run_agent_job]
    redis_settings = RedisSettings(
        host="localhost",
        port=6379,
    )