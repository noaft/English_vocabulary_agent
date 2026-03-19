"""
Tests for the Vocabulary Agent and Homework Agent using mocked LLM responses.
"""

import json
import unittest
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Sample LLM responses (valid JSON that our agents expect)
# ---------------------------------------------------------------------------

VOCAB_LLM_RESPONSE = json.dumps(
    {
        "happy": {
            "translation": "มีความสุข",
            "explanation": "Feeling or showing pleasure or contentment.",
            "similar_words": ["joyful", "pleased", "content"],
        },
        "sad": {
            "translation": "เศร้า",
            "explanation": "Feeling or showing sorrow; unhappy.",
            "similar_words": ["unhappy", "sorrowful", "dejected"],
        },
    }
)

HOMEWORK_LLM_RESPONSE = json.dumps(
    {
        "title": "Vocabulary Homework: Emotions",
        "instructions": "Complete all exercises to practise your new vocabulary words.",
        "exercises": [
            {
                "type": "fill_in_the_blank",
                "description": "Fill in the blank with the correct word.",
                "questions": [
                    "She was ____ when she received a gift.",
                    "He felt ____ after hearing the bad news.",
                    "The child was ____ to see her friends.",
                ],
            },
            {
                "type": "sentence_writing",
                "description": "Write your own sentence using each word.",
                "questions": [
                    "Write a sentence using the word 'happy'.",
                    "Write a sentence using the word 'sad'.",
                ],
            },
            {
                "type": "matching",
                "description": "Match each word with its synonym.",
                "questions": [
                    "happy – ___",
                    "sad – ___",
                ],
            },
        ],
    }
)


class TestVocabularyAgent(unittest.TestCase):
    """Unit tests for the Vocabulary Agent."""

    @patch("backend.agents.vocabulary_agent.call_llm", return_value=VOCAB_LLM_RESPONSE)
    def test_process_vocabulary_returns_all_words(self, _mock):
        from backend.agents.vocabulary_agent import process_vocabulary

        result = process_vocabulary(["happy", "sad"])
        self.assertIn("happy", result)
        self.assertIn("sad", result)

    @patch("backend.agents.vocabulary_agent.call_llm", return_value=VOCAB_LLM_RESPONSE)
    def test_process_vocabulary_structure(self, _mock):
        from backend.agents.vocabulary_agent import process_vocabulary

        result = process_vocabulary(["happy", "sad"])
        for word, info in result.items():
            self.assertIn("translation", info, f"Missing 'translation' for '{word}'")
            self.assertIn("explanation", info, f"Missing 'explanation' for '{word}'")
            self.assertIn("similar_words", info, f"Missing 'similar_words' for '{word}'")
            self.assertIsInstance(info["similar_words"], list)
            self.assertEqual(len(info["similar_words"]), 3)

    @patch("backend.agents.vocabulary_agent.call_llm", return_value=VOCAB_LLM_RESPONSE)
    def test_process_vocabulary_translation_content(self, _mock):
        from backend.agents.vocabulary_agent import process_vocabulary

        result = process_vocabulary(["happy", "sad"])
        self.assertEqual(result["happy"]["translation"], "มีความสุข")
        self.assertEqual(result["sad"]["translation"], "เศร้า")

    @patch("backend.agents.vocabulary_agent.call_llm", return_value="not json {{{")
    def test_process_vocabulary_invalid_json_raises(self, _mock):
        from backend.agents.vocabulary_agent import process_vocabulary

        with self.assertRaises(ValueError):
            process_vocabulary(["happy"])

    @patch(
        "backend.agents.vocabulary_agent.call_llm",
        return_value="```json\n" + VOCAB_LLM_RESPONSE + "\n```",
    )
    def test_process_vocabulary_strips_markdown_fences(self, _mock):
        from backend.agents.vocabulary_agent import process_vocabulary

        result = process_vocabulary(["happy", "sad"])
        self.assertIn("happy", result)


class TestHomeworkAgent(unittest.TestCase):
    """Unit tests for the Homework Agent."""

    @patch("backend.agents.homework_agent.call_llm", return_value=HOMEWORK_LLM_RESPONSE)
    def test_create_homework_top_level_keys(self, _mock):
        from backend.agents.homework_agent import create_homework

        result = create_homework(["happy", "sad"])
        self.assertIn("title", result)
        self.assertIn("instructions", result)
        self.assertIn("exercises", result)

    @patch("backend.agents.homework_agent.call_llm", return_value=HOMEWORK_LLM_RESPONSE)
    def test_create_homework_exercises_structure(self, _mock):
        from backend.agents.homework_agent import create_homework

        result = create_homework(["happy", "sad"])
        exercises = result["exercises"]
        self.assertIsInstance(exercises, list)
        self.assertGreaterEqual(len(exercises), 1)
        for ex in exercises:
            self.assertIn("type", ex)
            self.assertIn("description", ex)
            self.assertIn("questions", ex)
            self.assertIsInstance(ex["questions"], list)

    @patch("backend.agents.homework_agent.call_llm", return_value="bad json")
    def test_create_homework_invalid_json_raises(self, _mock):
        from backend.agents.homework_agent import create_homework

        with self.assertRaises(ValueError):
            create_homework(["happy"])

    @patch(
        "backend.agents.homework_agent.call_llm",
        return_value="```json\n" + HOMEWORK_LLM_RESPONSE + "\n```",
    )
    def test_create_homework_strips_markdown_fences(self, _mock):
        from backend.agents.homework_agent import create_homework

        result = create_homework(["happy", "sad"])
        self.assertIn("title", result)


class TestFlaskApp(unittest.TestCase):
    """Integration-level tests for the Flask API endpoints."""

    def setUp(self):
        from backend.app import app

        app.config["TESTING"] = True
        self.client = app.test_client()

    # ------------------------------------------------------------------
    # /api/vocabulary
    # ------------------------------------------------------------------

    @patch("backend.agents.vocabulary_agent.call_llm", return_value=VOCAB_LLM_RESPONSE)
    def test_vocabulary_endpoint_success(self, _mock):
        resp = self.client.post(
            "/api/vocabulary",
            json={"words": ["happy", "sad"]},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("vocabulary", data)
        self.assertIn("happy", data["vocabulary"])

    def test_vocabulary_endpoint_missing_words(self):
        resp = self.client.post("/api/vocabulary", json={})
        self.assertEqual(resp.status_code, 400)

    def test_vocabulary_endpoint_empty_list(self):
        resp = self.client.post("/api/vocabulary", json={"words": []})
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # /api/homework
    # ------------------------------------------------------------------

    @patch("backend.agents.homework_agent.call_llm", return_value=HOMEWORK_LLM_RESPONSE)
    def test_homework_endpoint_success(self, _mock):
        resp = self.client.post(
            "/api/homework",
            json={"words": ["happy", "sad"]},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("homework", data)
        self.assertIn("title", data["homework"])

    def test_homework_endpoint_missing_words(self):
        resp = self.client.post("/api/homework", json={})
        self.assertEqual(resp.status_code, 400)

    # ------------------------------------------------------------------
    # /api/process
    # ------------------------------------------------------------------

    @patch("backend.agents.homework_agent.call_llm", return_value=HOMEWORK_LLM_RESPONSE)
    @patch("backend.agents.vocabulary_agent.call_llm", return_value=VOCAB_LLM_RESPONSE)
    def test_process_endpoint_returns_both(self, _mock_vocab, _mock_hw):
        resp = self.client.post(
            "/api/process",
            json={"words": ["happy", "sad"]},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("vocabulary", data)
        self.assertIn("homework", data)

    # ------------------------------------------------------------------
    # /health
    # ------------------------------------------------------------------

    def test_health_endpoint(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["status"], "ok")


if __name__ == "__main__":
    unittest.main()
