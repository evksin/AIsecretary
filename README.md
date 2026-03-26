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

Если PostgreSQL пока не поднят, можно запустить локально на SQLite:
```powershell
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
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

## Контракт для n8n/Telegram

### Endpoint
- Метод: `POST`
- URL: `http://<host>:<port>/agent`
- `Content-Type`: `application/json`

### Request
```json
{
  "user_id": "telegram_123",
  "message": "Текст сообщения пользователя"
}
```

### Response (успех)
```json
{
  "response": "Текст ответа агента"
}
```

### Response (ошибка)
```json
{
  "error": {
    "code": "validation_error|openai_error|database_error|internal_error",
    "message": "Текст ошибки",
    "details": "Дополнительные детали"
  }
}
```

### Рекомендации по таймаутам и retry для n8n
- Таймаут HTTP-запроса к API: `30s` (минимум `20s`).
- Retry только для временных ошибок: `502`, `503`, `500`.
- Не ретраить для `422` (ошибка входных данных).
- Рекомендуемый backoff: `2s`, `5s`, `10s` (до 3 попыток).

### Пример вызова (PowerShell)
```powershell
$body = @{
    user_id = "telegram_123"
    message = "Напомни завтра позвонить клиенту"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/agent" `
  -ContentType "application/json" `
  -Body $body
```

### Пример с простым retry (PowerShell)
```powershell
$uri = "http://127.0.0.1:8000/agent"
$body = @{
    user_id = "telegram_123"
    message = "Какие у меня задачи?"
} | ConvertTo-Json

$delays = @(2, 5, 10)
for ($i = 0; $i -le $delays.Count; $i++) {
    try {
        $response = Invoke-WebRequest -Method Post -Uri $uri -ContentType "application/json" -Body $body
        $status = [int]$response.StatusCode
        if ($status -eq 200) {
            $response.Content
            break
        }
    } catch {
        $statusCode = [int]$_.Exception.Response.StatusCode
        if ($statusCode -in @(500, 502, 503) -and $i -lt $delays.Count) {
            Start-Sleep -Seconds $delays[$i]
            continue
        }
        throw
    }
}
```