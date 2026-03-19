"""
Vocabulary Agent: translates, explains, and suggests similar words for a
given vocabulary list using the configured LLM.
"""

import json
from backend.llm import call_llm


SYSTEM_CONTEXT = (
    "You are an expert English vocabulary teacher. "
    "Respond only with valid JSON, no extra text."
)


def process_vocabulary(words: list[str]) -> dict:
    """
    For each word in *words* return a dict with:
      - translation  (Thai translation)
      - explanation  (definition in simple English)
      - similar_words (list of 3 synonyms or related words)

    Returns::

        {
          "word1": {
              "translation": "...",
              "explanation": "...",
              "similar_words": ["...", "...", "..."]
          },
          ...
        }
    """
    word_list = ", ".join(words)
    prompt = f"""{SYSTEM_CONTEXT}

Given these English words: {word_list}

Return a JSON object where each key is a word from the list and the value is
an object with exactly these fields:
  "translation"  : Thai translation of the word
  "explanation"  : a clear, simple English definition (1-2 sentences)
  "similar_words": a JSON array of exactly 3 synonyms or closely related words

Example structure (do NOT copy the example values):
{{
  "happy": {{
    "translation": "มีความสุข",
    "explanation": "Feeling or showing pleasure or contentment.",
    "similar_words": ["joyful", "pleased", "content"]
  }}
}}

Now provide the result for: {word_list}"""

    raw = call_llm(prompt)
    try:
        # Strip markdown code fences if the model returns them
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned.strip())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Vocabulary agent returned invalid JSON: {exc}\nRaw: {raw}") from exc
