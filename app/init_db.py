import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "company.db"


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    # Departments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    # Employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            salary REAL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # Projects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department_id INTEGER,
            budget REAL,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    """)

    # Departments
    cursor.executemany(
        """
        INSERT OR IGNORE INTO departments (id, name)
        VALUES (?, ?)
        """,
        [
            (1, "Engineering"),
            (2, "Finance"),
            (3, "Human Resources"),
        ],
    )

    # Employees
    cursor.executemany(
        """
        INSERT OR IGNORE INTO employees
        (id, name, department_id, salary)
        VALUES (?, ?, ?, ?)
        """,
        [
            (1, "Alice", 1, 85000),
            (2, "Bob", 2, 72000),
            (3, "Carol", 1, 95000),
            (4, "David", 3, 68000),
            (5, "Emma", 1, 91000),
        ],
    )

    # Projects
    cursor.executemany(
        """
        INSERT OR IGNORE INTO projects
        (id, name, department_id, budget)
        VALUES (?, ?, ?, ?)
        """,
        [
            (1, "Payment Platform", 1, 500000),
            (2, "Credit Risk System", 2, 300000),
            (3, "HR Portal", 3, 150000),
        ],
    )

    connection.commit()
    connection.close()

    print(f"Database created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()