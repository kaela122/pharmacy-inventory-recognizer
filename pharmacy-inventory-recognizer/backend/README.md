# Backend (FastAPI)

Full step-by-step setup is in the main **`README.md`** at the project root.

Quick start (from this `backend/` folder):
```
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
Docs open at http://127.0.0.1:8000/docs

The database and demo data are created automatically on first run. The `.env` file selects
SQLite (default, no setup) or PostgreSQL. The automata code lives in `app/automata/`.
