import contextlib
import logging
import os
import sqlite3
from typing import Any, List

from rich import print

from models import User

logger = logging.getLogger(__name__)

DB_FILENAME = os.path.realpath("data/test.db")


def _get_connection() -> sqlite3.Connection:
    try:
        conn = sqlite3.connect(DB_FILENAME)
    except sqlite3.Error:
        logger.exception("Unable to get database")
        raise
    else:
        return conn


@contextlib.contextmanager
def connection_context():
    conn = _get_connection()
    cur = conn.cursor()

    yield cur

    conn.commit()
    cur.close()
    conn.close()


def get_challenges_for_candidate(cpf: str) -> List[Any]:
    query = f"""
        SELECT title, score FROM challenges c
        JOIN users u
        ON u.id = c.user_id
        WHERE u.cpf='{cpf}';
    """
    print("-" * 50)
    print(f"[bold]Executing query:[/bold] [green]{query}[/green]")
    print(f"[bold]{'-' * 50}[/bold]")

    with connection_context() as cur:
        cur.execute(query)
        results = cur.fetchall()

        return results


def get_users() -> List[Any]:
    query = "SELECT id, cpf, email, birth_date, phone_number FROM users;"
    with connection_context() as cur:
        cur.execute(query)
        return cur.fetchall()


def get_user_by_cpf(cpf: str) -> Any:
    query = f"SELECT id, cpf, email, birth_date, phone_number FROM users WHERE cpf='{cpf}';"
    with connection_context() as cur:
        cur.execute(query)
        return cur.fetchone()


def create_user(user: "User") -> Any:
    query = f"""
        INSERT INTO users (cpf, email, birth_date, phone_number)
        VALUES ('{user.cpf}', '{user.email}', '{user.birth_date}', '{user.phone_number}')
        RETURNING id, cpf, email, birth_date, phone_number;
    """
    with connection_context() as cur:
        cur.execute(query)
        return cur.fetchone()


def update_user(cpf: str, user_data: dict) -> Any:
    set_clause = ", ".join([f"{key} = '{value}'" for key, value in user_data.items()])
    query = f"""
        UPDATE users
        SET {set_clause}
        WHERE cpf = '{cpf}'
        RETURNING id, cpf, email, birth_date, phone_number;
    """
    with connection_context() as cur:
        cur.execute(query)
        return cur.fetchone()


def delete_user(cpf: str) -> Any:
    query = f"DELETE FROM users WHERE cpf = '{cpf}';"
    with connection_context() as cur:
        cur.execute(query)
        return cur.rowcount > 0
