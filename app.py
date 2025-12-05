# app.py
import os
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from recommender import call_llm_tags, recommend_songs

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")

INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <title>MoodSync</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="/static/style.css" />
</head>
<body>
  <div class="wrap">
    <h1>🎵 MoodSync</h1>

    <div class="cols">
      <section class="left">
        <h2>상황 / 분위기 설명</h2>
        <textarea id="situation" placeholder="예: 어제 여자 친구랑 헤어졌어, 차분하고 슬픈 발라드"></textarea>
        <div class="row">
          <button id="btn-voice" class="btn-secondary">🎙️ 음성 입력</button>
          <span id="voice-status" class="status"></span>
          <button id="btn-recommend">추천 받기</button>
        </div>
      </section>

      <section class="right">
        <h2>추천 결과</h2>
        <div id="results" class="results">
          <div class="empty">조건에 맞는 곡을 찾지 못했습니다.</div>
        </div>
      </section>
    </div>

    <p class="tip">Tip: 제목이나 아티스트를 클릭하면 바로 검색 링크로 이동합니다.</p>
  </div>

  <script src="/static/app.js"></script>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(INDEX_HTML)

@app.get("/favicon.ico")
def favicon():
    return send_from_directory(STATIC_DIR, "favicon.ico", as_attachment=False)

@app.post("/api/recommend")
def api_recommend():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()

    tags = call_llm_tags(content) or {}
    results = recommend_songs(tags, topk=3)

    payload = {
        "results": results,
        "tags": {
            "genre": tags.get("genre", ""),
            "mood": tags.get("mood", ""),
            "energy": tags.get("energy", ""),
            "tempo": tags.get("tempo", ""),
            "language": tags.get("language", "")
        }
    }
    return jsonify(payload)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=True)
