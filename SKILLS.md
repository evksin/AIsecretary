# Coding Skills & Rules

## General
- Always write clean, modular Python code
- Use FastAPI best practices
- Use async where appropriate
- Keep functions small and readable

## Architecture
- Separate layers:
  - API
  - Services
  - Tools
  - Database
- No business logic inside routes

## Database
- Use SQLAlchemy ORM
- Use PostgreSQL
- Use migrations-ready structure

## AI Integration
- Use OpenAI function calling
- Tools must be callable functions
- Agent decides which tool to use

## Tools Design
Each tool:
- separate function
- clear input/output
- no side effects outside DB

## Code Style
- Type hints required
- Pydantic for schemas
- Logging for all actions

## Don't
- Don't hardcode logic in one file
- Don't mix AI logic and DB logic