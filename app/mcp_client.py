import asyncio
import json

from mcp import Client, StdioServerParameters


server = StdioServerParameters(
    command="python",
    args=["-m", "app.mcp_server"],
)


async def _get_schema() -> str:
    async with Client(server) as client:
        response = await client.call_tool(
            "get_database_schema",
            {},
        )

        return response.content[0].text


async def _execute_sql(sql: str) -> dict:
    async with Client(server) as client:
        response = await client.call_tool(
            "execute_sql",
            {"sql": sql},
        )

        text = response.content[0].text

        return json.loads(text)


def get_schema() -> str:
    return asyncio.run(_get_schema())


def execute_sql(sql: str) -> dict:
    return asyncio.run(_execute_sql(sql))