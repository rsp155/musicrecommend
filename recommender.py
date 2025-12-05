# recommender.py
import os
import json
import re
import requests
from models import Session, Song  # 기존 models.py 그대로 사용

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b-instruct")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "30"))

SYSTEM_PROMPT = (
    "너는 음악 추천을 위한 태그 추출기야. 사용자의 한국어/영어 설명에서 "
    "다음 5가지를 JSON으로만 출력하라.\n"
    "keys = ['genre','mood','energy','tempo','language']\n"
    "- genre: 대략적 장르 (ballad, pop, jazz, indie, r&b, hiphop 등)\n"
    "- mood: 감정/무드 (sad, calm, happy, energetic 등 1~2단어)\n"
    "- energy: low|medium|high 중 하나\n"
    "- tempo: slow|mid|fast 중 하나\n"
    "- language: ko|en|ja 등 ISO 2글자 (모르면 빈 문자열)\n"
    "설명에 없으면 빈 문자열로 두되, 추측 가능한 범위에서 간결히 채워라.\n"
    "답변은 JSON 한 줄만. 추가 문장 금지."
)

def _extract_json(text: str) -> dict:
    # 코드블록 또는 본문에서 JSON만 깔끔히 추출
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return {}
    raw = m.group(0)
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    return {}

def call_llm_tags(content: str) -> dict:
    # 내용이 비어도 방어
    if not content:
        return {}

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content}
            ],
            "stream": False
        }
        url = f"{OLLAMA_URL}/api/chat"
        r = requests.post(url, json=payload, timeout=LLM_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        # Ollama chat 응답에서 message.content에 본문 있음
        msg = (data.get("message") or {}).get("content") or ""
        obj = _extract_json(msg)
    except Exception as e:
        print(f"[LLM] 호출/파싱 오류: {e}")
        obj = {}

    # 표준화
    return normalize_tags(obj)

def normalize_tags(tags: dict) -> dict:
    # 소문자/공백정리 + 허용 값 라벨링
    g = (tags.get("genre") or "").strip().lower()
    m = (tags.get("mood") or "").strip().lower()
    e = (tags.get("energy") or "").strip().lower()
    t = (tags.get("tempo") or "").strip().lower()
    l = (tags.get("language") or "").strip().lower()

    # energy/tempo 정규화
    def snap(val, choices):
        return val if val in choices else ""
    e = snap(e, ["low", "medium", "mid", "high"]).replace("mid", "medium")
    t = snap(t, ["slow", "mid", "fast"])

    # 너무 장문이면 1~2단어로 축약
    m = re.sub(r"[^a-z ]", " ", m).strip()
    m = " ".join(m.split()[:2])

    return {
        "genre": g,
        "mood": m,
        "energy": e,
        "tempo": t,
        "language": l
    }

def recommend_songs(tags: dict, topk: int = 3) -> list:
    """
    단순 스코어 규칙:
      - 각 필드 일치 시 +1, mood 부분포함시 +0.5
      - 우선 genre, mood, energy, tempo, language 순으로 가중
    """
    if not isinstance(tags, dict):
        tags = {}

    g = (tags.get("genre") or "").lower()
    m = (tags.get("mood") or "").lower()
    e = (tags.get("energy") or "").lower()
    t = (tags.get("tempo") or "").lower()
    l = (tags.get("language") or "").lower()

    results = []
    with Session() as s:
        rows = s.query(Song).all()
        for r in rows:
            score = 0.0
            # 일치 점수
            if g and (r.genre or "").lower() == g:
                score += 1.2
            if m:
                rm = (r.mood or "").lower()
                if rm == m:
                    score += 1.1
                elif m in rm or rm in m:
                    score += 0.6
            if e and (r.energy or "").lower() == e:
                score += 1.0
            if t and (r.tempo or "").lower() == t:
                score += 0.8
            if l and (r.language or "").lower() == l:
                score += 0.5

            if score > 0:
                results.append((
                    score,
                    {
                        "title": r.title,
                        "artist": r.artist,
                        "genre": r.genre or "",
                        "mood": r.mood or "",
                        "energy": r.energy or "",
                        "tempo": r.tempo or "",
                        "language": r.language or "",
                        # 필요 시 링크도 채워 넣기
                        "links": getattr(r, "links", None) or {}
                    }
                ))

    results.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in results[:max(1, topk)]]
