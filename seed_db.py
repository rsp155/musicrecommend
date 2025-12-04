from __future__ import annotations

from models import Song, get_session_local, init_db

SONGS = [
    # Focus / Study
    {"title": "Midnight Focus", "artist": "LoFi Haze", "genre": "lofi", "mood": "focus", "situation": "study", "energy": "low-mid", "tempo": 95, "language": "en"},
    {"title": "Notebook Beats", "artist": "Paper & Pen", "genre": "chill, lofi", "mood": "focus", "situation": "study", "energy": "low-mid", "tempo": 88, "language": "en"},
    {"title": "Late Night Code", "artist": "Debug Loops", "genre": "lofi", "mood": "focus", "situation": "study, night", "energy": "low-mid", "tempo": 92, "language": "en"},
    {"title": "Rain on Glass", "artist": "Cafe Ambience", "genre": "ambient", "mood": "focus", "situation": "study, rainy-day", "energy": "low", "tempo": 70, "language": "en"},
    {"title": "Quiet Library", "artist": "Soft Pages", "genre": "chill", "mood": "focus", "situation": "study", "energy": "low", "tempo": 80, "language": "en"},

    # Workout
    {"title": "Runway", "artist": "Pulse Driver", "genre": "edm", "mood": "motivated", "situation": "workout, running", "energy": "high", "tempo": 128, "language": "en"},
    {"title": "Barbell Anthem", "artist": "Iron Crew", "genre": "hip-hop", "mood": "motivated", "situation": "workout, gym", "energy": "high", "tempo": 100, "language": "en"},
    {"title": "Electro Sprint", "artist": "Voltline", "genre": "edm", "mood": "motivated", "situation": "workout", "energy": "high", "tempo": 132, "language": "en"},

    # Chill drive / Night
    {"title": "Neon Streets", "artist": "RetroRun", "genre": "synthwave, lofi", "mood": "chill", "situation": "drive, night", "energy": "mid", "tempo": 110, "language": "en"},
    {"title": "Moonlight Ride", "artist": "Afterglow", "genre": "synthwave", "mood": "chill", "situation": "drive, night", "energy": "mid", "tempo": 105, "language": "en"},

    # Rainy / Sad
    {"title": "Umbrella Walk", "artist": "Blue Alley", "genre": "indie", "mood": "melancholy", "situation": "rainy-day", "energy": "low", "tempo": 78, "language": "en"},
    {"title": "Window Raindrops", "artist": "Quiet House", "genre": "ballad", "mood": "melancholy", "situation": "rainy-day", "energy": "low", "tempo": 72, "language": "en"},

    # Happy / Bright
    {"title": "Sunny Morning", "artist": "Acoustic Band", "genre": "acoustic, pop", "mood": "happy", "situation": "daily", "energy": "mid", "tempo": 110, "language": "en"},
    {"title": "Picnic Day", "artist": "Polaroid", "genre": "indie pop", "mood": "happy", "situation": "outdoor", "energy": "mid", "tempo": 118, "language": "en"},

    # Korean tags
    {"title": "밤샘과제", "artist": "공대감성", "genre": "lofi", "mood": "focus", "situation": "study, night", "energy": "low-mid", "tempo": 92, "language": "ko"},
    {"title": "퇴근길 드라이브", "artist": "야간운전", "genre": "synthwave", "mood": "chill", "situation": "drive, night", "energy": "mid", "tempo": 108, "language": "ko"},
    {"title": "비 오는 오후", "artist": "창가", "genre": "ballad", "mood": "melancholy", "situation": "rainy-day", "energy": "low", "tempo": 76, "language": "ko"},
    {"title": "헬스장 불꽃", "artist": "근력충", "genre": "hip-hop", "mood": "motivated", "situation": "workout", "energy": "high", "tempo": 102, "language": "ko"},
    {"title": "주말 소풍", "artist": "햇살", "genre": "acoustic, pop", "mood": "happy", "situation": "outdoor", "energy": "mid", "tempo": 112, "language": "ko"},
]


def main():
    init_db()
    SessionLocal = get_session_local()
    session = SessionLocal()

    # 이미 비슷한 제목이 있으면 중복 삽입 방지
    existing_titles = {s.title for s in session.query(Song).all()}

    inserted = 0
    for item in SONGS:
        if item["title"] in existing_titles:
            continue
        song = Song(**item)
        session.add(song)
        inserted += 1

    session.commit()
    session.close()
    print(f"✅ Seed done. Inserted: {inserted}")


if __name__ == "__main__":
    main()
