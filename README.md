# AIsecretary

Базовый каркас AI Agent API на FastAPI.

## Структура
- `app/main.py`
- `app/db.py`
- `app/models.py`
- `app/tools/tasks.py`
- `app/tools/memory.py`
- `app/services/agent.py`

## Быстрый запуск (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn sqlalchemy psycopg2-binary
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_secretary"
uvicorn app.main:app --reload
```

Проверка health endpoint:
```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```