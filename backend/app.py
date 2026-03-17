"""
Flask application – entry point for the English Vocabulary Agent backend.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from backend.agents.vocabulary_agent import process_vocabulary
from backend.agents.homework_agent import create_homework

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app)


# ---------------------------------------------------------------------------
# Static / UI routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/vocabulary", methods=["POST"])
def vocabulary():
    """Process a vocabulary list and return translations, explanations and synonyms."""
    data = request.get_json(force=True, silent=True) or {}
    words = data.get("words", [])
    if not words or not isinstance(words, list):
        return jsonify({"error": "Provide a non-empty 'words' list."}), 400

    words = [str(w).strip() for w in words if str(w).strip()]
    if not words:
        return jsonify({"error": "All provided words are empty strings."}), 400

    try:
        result = process_vocabulary(words)
        return jsonify({"vocabulary": result})
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": str(exc)}), 500


@app.route("/api/homework", methods=["POST"])
def homework():
    """Generate homework assignments for the submitted vocabulary list."""
    data = request.get_json(force=True, silent=True) or {}
    words = data.get("words", [])
    if not words or not isinstance(words, list):
        return jsonify({"error": "Provide a non-empty 'words' list."}), 400

    words = [str(w).strip() for w in words if str(w).strip()]
    if not words:
        return jsonify({"error": "All provided words are empty strings."}), 400

    try:
        result = create_homework(words)
        return jsonify({"homework": result})
    except Exception as exc:  # pylint: disable=broad-except
        return jsonify({"error": str(exc)}), 500


@app.route("/api/process", methods=["POST"])
def process_all():
    """Run both agents in sequence and return combined results."""
    data = request.get_json(force=True, silent=True) or {}
    words = data.get("words", [])
    if not words or not isinstance(words, list):
        return jsonify({"error": "Provide a non-empty 'words' list."}), 400

    words = [str(w).strip() for w in words if str(w).strip()]
    if not words:
        return jsonify({"error": "All provided words are empty strings."}), 400

    response: dict = {}

    try:
        response["vocabulary"] = process_vocabulary(words)
    except Exception as exc:  # pylint: disable=broad-except
        response["vocabulary_error"] = str(exc)

    try:
        response["homework"] = create_homework(words)
    except Exception as exc:  # pylint: disable=broad-except
        response["homework_error"] = str(exc)

    return jsonify(response)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
