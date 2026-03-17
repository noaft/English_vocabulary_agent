# English Vocabulary Agent

A **multi-agent AI system** for English vocabulary learning, built with Python (Flask) and a clean web UI.

## Features

| Agent | What it does |
|-------|-------------|
| **Vocabulary Agent** | Translates words (to Thai), gives definitions, and suggests 3 synonyms |
| **Homework Agent** | Creates structured exercises (fill-in-the-blank, matching, sentence writing …) |

Both agents use a configurable LLM backend – **Google Gemini** (cloud) or **Gemma3 via Ollama** (local/private).

## Quick Start

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Configure your LLM credentials
cp .env.example .env
# then edit .env – add your GEMINI_API_KEY or set LLM_PROVIDER=gemma3

# 3. Start the server
python -m backend.app

# 4. Open http://localhost:5000 in your browser
```

## Running Tests

```bash
python -m pytest backend/tests/ -v
```

## LLM Configuration

Edit `.env` to switch between providers:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `gemini` | `gemini` or `gemma3` |
| `GEMINI_API_KEY` | — | Google AI Studio API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `GEMMA3_MODEL` | `gemma3` | Ollama model tag |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |

See **[AGENTS.md](AGENTS.md)** for full architecture, agent workflow, and extension guide.
