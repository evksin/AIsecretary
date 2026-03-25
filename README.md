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
pip install fastapi uvicorn sqlalchemy psycopg2-binary openai
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_secretary"
$env:OPENAI_API_KEY = "your_openai_api_key"
uvicorn app.main:app --reload
```

Проверка health endpoint:
```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

Проверка `POST /agent`:
```powershell
$body = @{
    user_id = "telegram_123"
    message = "Добавь задачу купить молоко"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/agent" -ContentType "application/json" -Body $body
```

Формат ошибок API (стабильный для интеграций):
```json
{
  "error": {
    "code": "validation_error|openai_error|database_error|internal_error",
    "message": "Текст ошибки",
    "details": "Дополнительные детали"
  }
}
```