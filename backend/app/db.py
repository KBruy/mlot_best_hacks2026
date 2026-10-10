import os

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ["DATABASE_URL"]


class DatabaseUnavailable(Exception):
    pass


def connect() -> psycopg.Connection:
    try:
        return psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=3)
    except psycopg.OperationalError as e:
        raise DatabaseUnavailable from e


def get_node(node_id: int) -> dict | None:
    try:
        with connect() as conn:
            node = conn.execute(
                "SELECT id, content FROM nodes WHERE id = %s", (node_id,)
            ).fetchone()
            if node is None:
                return None
            node["choices"] = conn.execute(
                "SELECT child_id, label, legend FROM choices"
                " WHERE parent_id = %s ORDER BY child_id",
                (node_id,),
            ).fetchall()
            return node
    except psycopg.OperationalError as e:
        raise DatabaseUnavailable from e