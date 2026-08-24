from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import sqlite3

app = FastAPI()

DB_NAME = "tasks.db"

conn = sqlite3.connect(DB_NAME, check_same_thread=False)
conn.row_factory = sqlite3.Row

conn.execute("""CREATE TABLE IF NOT EXISTS tasks(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
done BOOLEAN NOT NULL)""")
conn.commit()

cursor = conn.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]

if count == 0:
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy milk", 0))
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Study Python", 0))
    conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Finish assignment", 0))
    conn.commit()


@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def read_health():
    return {"status": "ok"}


def row_to_task(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.get("/tasks")
def get_tasks():
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    return [row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return row_to_task(row)


class TaskCreate(BaseModel):
    title: str


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if task.title.strip() == "":
        return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})

    cur = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, 0))
    conn.commit()

    new_id = cur.lastrowid
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    return row_to_task(row)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    if task.title is None and task.done is None:
        return JSONResponse(status_code=400, content={"error": "Request body cannot be empty"})

    new_title = row["title"]
    if task.title is not None:
        if task.title.strip() == "":
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
        new_title = task.title

    new_done = row["done"] if task.done is None else int(task.done)

    conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, task_id))
    conn.commit()

    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return row_to_task(updated)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    return Response(status_code=204)

