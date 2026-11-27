# AI-Health-Assistant backend

This backend provides the API foundation for the AI-Health-Coach application.

## Features

- health check endpoint
- chat endpoint for AI assistance interactions
- minimal configuration via environment variables

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment variables

Set values in a `.env` file or via your shell:

```bash
LLM_MODEL=local-default
```
