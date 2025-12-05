# insert_csv_to_db.py
from models import Session, Song
from recommender import normalize_tags_ko
import csv, os

CSV_FILE = "songs_filled.csv"   # <- 여기 파일명만 바꾸면 됨

def main():
    path = os.path.abspath(CSV_FILE)
    print("CSV:", path)
    total = new = updated = 0
    with Session() as s, open(path, "r", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        need = ["title","artist","genre","mood","language","energy","tempo"]
        miss = [c for c in need if c not in r.fieldnames]
        if miss:
            print("CSV 컬럼 누락:", miss)
            return
        for row in r:
            t = (row["title"] or "").strip()
            a = (row["artist"] or "").strip()
            if not t or not a:
                continue
            tags = {k:(row.get(k) or "").strip() for k in ["genre","mood","language","energy","tempo"]}
            normalize_tags_ko(tags)
            ex = s.query(Song).filter(Song.title==t, Song.artist==a).first()
            if ex:
                for k,v in tags.items():
                    if v:
                        setattr(ex, k, v)
                updated += 1
            else:
                s.add(Song(title=t, artist=a, **tags))
                new += 1
            total += 1
        s.commit()
    print(f"[DONE] rows={total}, new={new}, updated={updated}")

if __name__ == "__main__":
    main()
