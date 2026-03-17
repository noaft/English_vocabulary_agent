"""
LLM client supporting Gemini and Gemma3 models via environment configuration.
"""

import os
import json
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
GEMMA3_MODEL = os.getenv("GEMMA3_MODEL", "gemma3")


def _call_gemini(prompt: str) -> str:
    """Call the Gemini API and return the text response."""
    try:
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        raise RuntimeError(f"Gemini API error: {exc}") from exc


def _call_gemma3(prompt: str) -> str:
    """Call a local Gemma3 model via the Ollama HTTP API."""
    try:
        import urllib.request

        payload = json.dumps(
            {"model": GEMMA3_MODEL, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "").strip()
    except Exception as exc:
        raise RuntimeError(f"Ollama/Gemma3 API error: {exc}") from exc


def call_llm(prompt: str) -> str:
    """
    Route the prompt to the configured LLM provider.

    Set LLM_PROVIDER=gemini  (default) to use Google Gemini.
    Set LLM_PROVIDER=gemma3          to use a local Gemma3 model via Ollama.
    """
    if LLM_PROVIDER == "gemma3":
        return _call_gemma3(prompt)
    return _call_gemini(prompt)
