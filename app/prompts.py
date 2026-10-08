SQL_GENERATION_PROMPT = """
You are a SQL query generation assistant.

Your job is to convert a user's natural-language question
into a valid SQLite SQL query.

You are given the database schema below.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

Rules:
1. Generate SQLite-compatible SQL.
2. Use only tables and columns that appear in the provided schema.
3. Return only the SQL query.
4. Do not use markdown code fences.
5. Do not explain the query.

SQL:
"""


SQL_CORRECTION_PROMPT = """
You are a SQL debugging assistant.

A SQL query generated for a SQLite database failed during execution.

DATABASE SCHEMA:
{schema}

USER QUESTION:
{question}

FAILED SQL:
{sql}

DATABASE ERROR:
{error}

Your task is to correct the SQL query.

Rules:
1. Generate valid SQLite-compatible SQL.
2. Use only tables and columns that exist in the database schema.
3. Fix the specific error instead of changing the user's intended question.
4. Return only the corrected SQL query.
5. Do not use markdown code fences.
6. Do not explain the correction.

CORRECTED SQL:
"""