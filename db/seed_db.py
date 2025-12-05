from models import Session, Song

SEED = [
  ("lofi study", "Lo Sound", "lofi", "calm", "en", "low", "slow"),
  ("밤의 카페", "이밤", "jazz", "calm", "ko", "low", "slow"),
  ("Rain Window", "Quiet House", "indie", "calm", "en", "low", "slow"),
  ("Barbell Anthem", "Iron Crew", "hip-hop", "motivated", "en", "high", "fast"),
  ("헬스장 불꽃", "근력중", "hip-hop", "motivated", "ko", "high", "fast"),
  ("Runway", "Pulse Driver", "edm", "motivated", "en", "high", "fast"),
  ("Electro Sprint", "Voltime", "edm", "motivated", "en", "high", "fast"),
  ("그때의 우리", "담담", "ballad", "calm", "ko", "low", "slow"),
  ("Morning Light", "Skyline", "pop", "happy", "en", "medium", "mid"),
  ("Soft Focus", "Deep Work", "lofi", "focus", "en", "low", "slow"),
]

with Session() as s:
    if s.query(Song).count() == 0:
        for t,a,g,m,l,e,tempo in SEED:
            s.add(Song(title=t, artist=a, genre=g, mood=m, language=l, energy=e, tempo=tempo))
        s.commit()
        print("Seed inserted:", len(SEED))
    else:
        print("DB already has data.")
