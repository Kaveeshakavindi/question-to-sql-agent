from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job

app = FastAPI(
    title="Self-Healing SQL Agent",
)


class QueryRequest(BaseModel):
    question: str
    initial_sql: str | None = None


@app.on_event("startup")
async def startup():
    app.state.redis = await create_pool(
        RedisSettings(
            host="localhost",
            port=6379,
        )
    )


@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()


@app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
async def create_job(request: QueryRequest):

    job = await app.state.redis.enqueue_job(
        "run_agent_job",
        request.question,
        request.initial_sql,
    )

    return {
        "job_id": job.job_id,
        "status": "queued",
    }


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):

    job = Job(
        job_id,
        app.state.redis,
    )

    status = await job.status()

    if status.value == "not_found":
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    info = await job.result_info()

    result = None

    if info is not None:
        result = info.result

    return {
        "job_id": job_id,
        "status": status.value,
        "result": result,
    }