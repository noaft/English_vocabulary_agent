"""
Homework Agent: generates homework assignments based on a vocabulary list
using the configured LLM.
"""

import json
from backend.llm import call_llm


SYSTEM_CONTEXT = (
    "You are a creative English teacher specialising in vocabulary homework. "
    "Respond only with valid JSON, no extra text."
)


def create_homework(words: list[str]) -> dict:
    """
    Generate a structured homework assignment for the given vocabulary list.

    Returns::

        {
          "title": "...",
          "instructions": "...",
          "exercises": [
            {
              "type": "fill_in_the_blank | matching | sentence_writing | ...",
              "description": "...",
              "questions": ["...", ...]
            },
            ...
          ]
        }
    """
    word_list = ", ".join(words)
    prompt = f"""{SYSTEM_CONTEXT}

Create an engaging English homework assignment for a learner studying these
vocabulary words: {word_list}

Return a single JSON object with exactly these top-level fields:
  "title"       : a descriptive title for the homework
  "instructions": overall instructions for the student
  "exercises"   : a JSON array of at least 3 exercise objects

Each exercise object must have:
  "type"        : one of "fill_in_the_blank", "matching", "sentence_writing",
                  "true_or_false", or "multiple_choice"
  "description" : a short description of what the student should do
  "questions"   : a JSON array of question strings (at least 3 per exercise)

Make all exercises educational, clear, and appropriate for an intermediate
English learner.

Vocabulary words: {word_list}"""

    raw = call_llm(prompt)
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Homework agent returned invalid JSON: {exc}\nRaw: {raw}") from exc
