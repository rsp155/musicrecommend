# recommender.py  — Ollama 연동 + 점수 기반 추천 (완전체)

from __future__ import annotations

import os
import re
import json
from typing import Dict, List

import requests
from sqlalchemy.orm import Session

from models import Song

# ===== LLM 설정 =====
# 환경변수로 바꾸고 싶으면 터미널에서:
#   setx OLLAMA_URL "http://localhost:11434"
#   setx OLLAMA_MODEL "qwen2.5:3b-instruct"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")  # 또는 "llama3.2:3b-instruct"


# ---------- 규칙기반 폴백 ----------
def _rules_fallback(user_text: str) -> dict:
    t = (user_text or "").lower()

    if any(k in t for k in ["공부", "집중", "과제", "study", "focus"]):
        return {
            "mood": "focus",
            "genre": ["lofi", "chill"],
            "situation": ["study"],
            "energy": "low-mid",
            "tempo": "medium",
        }
    if any(k in t for k in ["운동", "헬스", "workout", "달리기", "러닝"]):
        return {
            "mood": "motivated",
            "genre": ["edm", "hip-hop"],
            "situation": ["workout"],
            "energy": "high",
            "tempo": "fast",
        }
    if any(k in t for k in ["슬픔", "비", "rain", "sad", "우울"]):
        return {
            "mood": "melancholy",
            "genre": ["ballad", "indie"],
            "situation": ["rainy-day"],
            "energy": "low",
            "tempo": "slow",
        }
    if any(k in t for k in ["드라이브", "drive", "야간", "밤"]):
        return {
            "mood": "chill",
            "genre": ["synthwave", "lofi"],
            "situation": ["drive", "night"],
            "energy": "mid",
            "tempo": "medium",
        }

    # 기본값
    return {
        "mood": "focus",
        "genre": ["lofi", "chill"],
        "situation": ["study"],
        "energy": "low-mid",
        "tempo": "medium",
    }


# ---------- 유틸 ----------
def _extract_json(text: str) -> dict:
    """응답에 설명이 섞여도 JSON 객체만 추출."""
    if not text:
        return {}
    m = re.search(r"\{.*\}", text, flags=re.S)
    if not m:
        return {}
    return json.loads(m.group(0))


def _tokenize(value: str | None) -> List[str]:
    if not value:
        return []
    return [x.strip().lower() for x in value.replace("/", ",").split(",") if x.strip()]


# ---------- LLM 호출 ----------
def call_llm(user_text: str) -> dict:
    """
    Ollama Chat API로 태그를 추출.
    실패 시 규칙기반(_rules_fallback)으로 폴백.
    """
    prompt = f"""
다음 사용자의 문장을 보고, 분위기/장르/상황 태그를 JSON으로만 출력하세요.
반드시 아래 JSON 형식만 출력하고, 설명은 포함하지 마세요.

{{
  "mood": "<한 단어>",
  "genre": ["<장르>", ...],
  "situation": ["<상황>", ...],
  "energy": "<low|low-mid|mid|high>",
  "tempo": "<slow|medium|fast>"
}}

문장: {user_text}
"""

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=30,
        )
        r.raise_for_status()
        content = r.json().get("message", {}).get("content", "")
        data = _extract_json(content)

        # 최소 필드 체크
        if not isinstance(data, dict) or "mood" not in data:
            return _rules_fallback(user_text)

        # 타입 보정
        if not isinstance(data.get("genre"), list):
            data["genre"] = list(filter(None, [data.get("genre")])) if data.get("genre") else []
        if not isinstance(data.get("situation"), list):
            data["situation"] = list(filter(None, [data.get("situation")])) if data.get("situation") else []

        return data

    except Exception as e:
        print("[LLM ERROR]", repr(e))
        return _rules_fallback(user_text)


# ---------- 스코어링 & 추천 ----------
def _score_song(song: Song, tags: Dict) -> int:
    score = 0

    # mood 정확히 일치
    if tags.get("mood") and song.mood and song.mood.lower() == str(tags["mood"]).lower():
        score += 3

    # genre/situation 교집합
    wanted_genres = set(g.lower() for g in tags.get("genre", []) if g)
    wanted_situ = set(s.lower() for s in tags.get("situation", []) if s)

    song_genres = set(_tokenize(song.genre))
    song_situ = set(_tokenize(song.situation))

    score += len(wanted_genres & song_genres) * 2
    score += len(wanted_situ & song_situ) * 2

    # energy 대략 매칭
    if tags.get("energy") and song.energy and str(tags["energy"]).split("-")[0] in song.energy:
        score += 1

    # tempo(선택): fast/slow/medium 힌트
    if tags.get("tempo") and song.tempo:
        t = str(tags["tempo"]).lower()
        if (t == "fast" and song.tempo >= 120) or (t == "slow" and song.tempo <= 85) or (
            t == "medium" and 86 <= song.tempo <= 119
        ):
            score += 1

    return score


def generate_reason(song: Song, tags: Dict) -> str:
    mood = tags.get("mood") or song.mood or ""
    genre = ", ".join(tags.get("genre", [])) or song.genre or ""
    situation = ", ".join(tags.get("situation", [])) or song.situation or ""
    return f"{mood} 무드 / {genre} 느낌 / {situation} 상황에 잘 맞아서 추천해요."


def recommend_songs(db: Session, tags: Dict, limit: int = 5) -> list[dict]:
    songs: List[Song] = db.query(Song).all()

    ranked: List[tuple[int, Song]] = []
    for s in songs:
        sc = _score_song(s, tags)
        if sc > 0:
            ranked.append((sc, s))

    ranked.sort(key=lambda x: x[0], reverse=True)
    top = [s for _, s in ranked[:limit]]

    return [
        {
            **s.to_dict(),
            "reason": generate_reason(s, tags),
        }
        for s in top
    ]
