from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import db

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
def read_node(node_id: int):
    try:
        node = db.get_node(node_id)
    except db.DatabaseUnavailable:
        raise HTTPException(503, "Baza danych jest niedostępna.")
    if node is None:
        raise HTTPException(404, "Nie ma takiego węzła.")
    return node