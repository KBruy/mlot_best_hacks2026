import os

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel

DATABASE_URL = os.environ["DATABASE_URL"]

app = FastAPI()


class Choice(BaseModel):
    child_id: int
    label: str
    legend: str


class Node(BaseModel):
    id: int
    content: str
    choices: list[Choice]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/nodes/{node_id}", response_model=Node)
def get_node(node_id: int):
    try:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=3) as conn:
            node = conn.execute("SELECT id, content FROM nodes WHERE id = %s", (node_id,)).fetchone()
            choices = conn.execute(
                "SELECT child_id, label, legend FROM choices WHERE parent_id = %s ORDER BY child_id",
                (node_id,),
            ).fetchall()
    except psycopg.Error:
        raise HTTPException(503, "Baza danych jest niedostępna.")
    if node is None:
        raise HTTPException(404, "Nie ma takiego węzła.")
    return {**node, "choices": choices}
