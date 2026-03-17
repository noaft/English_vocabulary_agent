# AGENTS.md – English Vocabulary Agent: Multi-Agent System Documentation

## Overview

This project implements a **multi-agent system** for English vocabulary learning.
Two autonomous AI agents collaborate to process a vocabulary list submitted by the
learner:

| Agent | Role |
|-------|------|
| **Vocabulary Agent** | Translates each word (to Thai), provides a clear English definition, and suggests 3 similar/related words |
| **Homework Agent** | Generates structured homework exercises (fill-in-the-blank, sentence writing, matching, etc.) based on the vocabulary list |

Both agents call the same configurable LLM backend (Gemini or Gemma3 via Ollama).

---

## Architecture

```
User (Web UI)
      │  POST /api/process  (or /api/vocabulary, /api/homework)
      ▼
  Flask Backend  (backend/app.py)
      ├── Vocabulary Agent  (backend/agents/vocabulary_agent.py)
      │         └── LLM Client  (backend/llm/llm_client.py)
      └── Homework Agent    (backend/agents/homework_agent.py)
                └── LLM Client  (backend/llm/llm_client.py)
```

### File Layout

```
English_vocabulary_agent/
├── backend/
│   ├── app.py                  # Flask API server
│   ├── requirements.txt
│   ├── agents/
│   │   ├── vocabulary_agent.py # Vocabulary Agent
│   │   └── homework_agent.py   # Homework Agent
│   ├── llm/
│   │   └── llm_client.py       # LLM routing (Gemini / Gemma3)
│   └── tests/
│       └── test_agents.py      # Unit + integration tests
├── frontend/
│   ├── index.html              # Web UI
│   ├── style.css
│   └── script.js
├── .env.example                # Environment variable template
└── AGENTS.md                   # This file
```

---

## LLM Configuration

Copy `.env.example` to `.env` and fill in the required values.

### Using Google Gemini (default)

```ini
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your key from https://aistudio.google.com/app/apikey>
GEMINI_MODEL=gemini-1.5-flash   # or gemini-1.5-pro, gemini-1.0-pro
```

The `google-generativeai` Python package is used to communicate with the Gemini API.

### Using Gemma3 via Ollama (local / private)

```ini
LLM_PROVIDER=gemma3
OLLAMA_HOST=http://localhost:11434   # default Ollama address
GEMMA3_MODEL=gemma3                 # any Ollama model tag, e.g. gemma3:27b
```

Steps to use a local model:
1. Install [Ollama](https://ollama.com).
2. Pull the model: `ollama pull gemma3`
3. Set `LLM_PROVIDER=gemma3` in `.env`.

No external API key is required for the local mode.

### Switching Models at Runtime

Change `LLM_PROVIDER` (and the relevant model name variable) in `.env` and restart
the server.  No code changes are needed.

---

## Agent Workflows

### Vocabulary Agent

**Trigger:** HTTP POST to `/api/vocabulary` with `{"words": ["word1", "word2", ...]}`

**Workflow:**
1. Receives the word list from the Flask route.
2. Constructs a structured prompt requesting JSON output with three fields per word:
   `translation`, `explanation`, and `similar_words`.
3. Calls `call_llm()` from the LLM client.
4. Parses and validates the JSON response (strips markdown code fences if present).
5. Returns a dictionary keyed by word.

**Example response:**
```json
{
  "happy": {
    "translation": "มีความสุข",
    "explanation": "Feeling or showing pleasure or contentment.",
    "similar_words": ["joyful", "pleased", "content"]
  }
}
```

### Homework Agent

**Trigger:** HTTP POST to `/api/homework` with `{"words": ["word1", "word2", ...]}`

**Workflow:**
1. Receives the word list from the Flask route.
2. Constructs a prompt requesting a JSON homework object with a `title`,
   `instructions`, and `exercises` array (each with `type`, `description`,
   and `questions`).
3. Calls `call_llm()` and parses the JSON response.
4. Returns the structured homework object.

**Supported exercise types:** `fill_in_the_blank`, `matching`, `sentence_writing`,
`true_or_false`, `multiple_choice`.

### Combined Endpoint

POST to `/api/process` runs **both** agents sequentially and returns:

```json
{
  "vocabulary": { ... },
  "homework":   { ... }
}
```

If one agent fails the other still runs; its error is included as
`vocabulary_error` or `homework_error` in the response.

---

## Running the Application

### Prerequisites

- Python 3.11+
- `pip install -r backend/requirements.txt`
- A `.env` file (copy from `.env.example`)

### Start the Server

```bash
# From the repository root
python -m backend.app
```

The web UI is then available at **http://localhost:5000**.

### Run Tests

```bash
# From the repository root
python -m pytest backend/tests/ -v
```

---

## Prompt Design

Both agents use a **system context prefix** (defined as a constant in each agent
module) that instructs the model to act as an expert English teacher and to respond
**only with valid JSON**.  This keeps output parsing simple and reliable.

To customise prompts, edit the `SYSTEM_CONTEXT` constant and the `prompt` template
string in `vocabulary_agent.py` or `homework_agent.py`.

---

## Extending the System

- **Add a new agent:** Create a new file in `backend/agents/`, import `call_llm`,
  write a prompt, parse the JSON, and add a Flask route in `backend/app.py`.
- **Add a new LLM provider:** Add a `_call_<provider>()` function in
  `backend/llm/llm_client.py` and handle the new `LLM_PROVIDER` value in `call_llm()`.
- **Change the model name:** Update `GEMINI_MODEL` or `GEMMA3_MODEL` in `.env`.
