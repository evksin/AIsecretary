# AI Secretary Project

## Goal
Создать AI-агента (ИИ-секретаря), который:
- управляет задачами
- запоминает информацию
- отвечает на вопросы
- вызывает инструменты (tools)
- интегрируется с Telegram через n8n

## Architecture
- Backend: FastAPI (Python)
- AI: OpenAI API (function calling)
- Database: PostgreSQL
- Automation: n8n
- Interface: Telegram bot

## Core Features
1. Task management
2. Memory (short-term + long-term)
3. Tool calling
4. Natural language understanding
5. Reminders (через n8n)

## Tools (must implement)
- create_task
- get_tasks
- search_memory
- save_memory

## Database
Use PostgreSQL with tables:
- users
- tasks
- memory

## Requirements
- Clean architecture
- Modular code
- Easy to extend tools
- Logging
- Error handling

## API
POST /agent
Request:
{
  "user_id": "string",
  "message": "string"
}

Response:
{
  "response": "string"
}