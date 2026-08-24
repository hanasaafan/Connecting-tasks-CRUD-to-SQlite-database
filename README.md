# Connecting-tasks-CRUD-to-SQlite-database

# Task API — SQLite Edition

A simple CRUD Task API built with FastAPI, originally backed by an in-memory list (Assignment 1) and now upgraded to persist data in a real SQLite database.

## What changed from Assignment 1

The API's endpoints, request/response shapes, and status codes are all identical to before. The only thing that changed is *where the data lives* — it used to disappear every time the server restarted, and now it survives, because it's saved to a file called `tasks.db` instead of a Python list in memory.

## Why SQLite

- **Single file** — the entire database is just `tasks.db`, no server process to install or manage.
- **Zero setup** — Python's `sqlite3` module is built in; nothing extra to install for the database itself.
- **Persistence** — data survives restarts, crashes, and redeploys, because it's written to disk instead of held in RAM.
- Perfect fit for a small project like this one, where a heavier database (Postgres, MySQL) would be overkill.

## Endpoints

| Method | Route          | Description                     |
|--------|----------------|----------------------------------|
| GET    | `/tasks`       | List all tasks                  |
| GET    | `/tasks/{id}`  | Get a single task by id         |
| POST   | `/tasks`       | Create a new task               |
| PUT    | `/tasks/{id}`  | Update a task's title/done state|
| DELETE | `/tasks/{id}`  | Delete a task                   |

All writes use parameterized SQL queries (`?` placeholders) — user input is never glued directly into SQL strings, which prevents SQL injection.

## How to run it

1. Install dependencies:
```bash
   pip install fastapi uvicorn
```
2. Start the server:
```bash
   uvicorn main:app --reload
```
3. `tasks.db` is created automatically on first run, with a `tasks` table and 3 seeded example tasks — no manual setup needed.
4. Visit `http://localhost:8000/docs` for interactive Swagger docs to try every endpoint live.

## The database file

`tasks.db` lives in the project root and is created automatically the first time the app runs. It's listed in `.gitignore`, so it's **not** committed to this repo — every fresh clone starts with a clean, auto-seeded database.

## Exploring the database by hand (Stage 4)

Using [DB Browser for SQLite](https://sqlitebrowser.org/), I opened `tasks.db` directly and ran queries against it outside the API, confirming the API and the database file are always in sync — no caching, no separate "state," just one source of truth.

Example query run:
```sql
SELECT * FROM tasks WHERE done = 1;
```
Before marking anything done, this returned zero rows — confirming none of my seeded tasks start as completed. After running `UPDATE tasks SET done = 1;` in DB Browser and saving, calling `GET /tasks` from the API immediately reflected every task as done, with no server restart required.


## Status codes

| Code | Meaning                          |
|------|-----------------------------------|
| 200  | Success (GET, PUT)                |
| 201  | Task created (POST)               |
| 204  | Task deleted, no content returned |
| 400  | Invalid or empty request body     |
| 404  | Task not found                    |
