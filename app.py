from __future__ import annotations

from flask import Flask, jsonify, render_template, request
from sqlalchemy.orm import Session

from models import get_session_local, init_db
from recommender import call_llm, recommend_songs

app = Flask(__name__)

# Initialize DB and session factory
init_db()
SessionLocal = get_session_local()


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend_api():
    """Handle recommendation requests from the frontend."""
    data = request.get_json(force=True)
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "내용을 입력해주세요."}), 400

    # Step 1: LLM tagging (stubbed)
    tags = call_llm(content)
    print("TAGS:", tags)

    # Step 2: Query songs
    db: Session = SessionLocal()
    try:
        tracks = recommend_songs(db, tags)
    finally:
        db.close()

    print("TRACKS:", tracks)

    # Build response
    response = {"query_summary": content, "tags": tags, "tracks": tracks}
    return jsonify(response)


if __name__ == "__main__":
    # Running via `python app.py` will start the Flask development server
    app.run(host="0.0.0.0", port=5000, debug=True)
