from __future__ import annotations

from pathlib import Path
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "music.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()


class Song(Base):
    """Represents a song in the catalog that can be recommended."""
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    genre = Column(String, nullable=True)      # e.g., 'lofi', 'pop'
    mood = Column(String, nullable=True)       # e.g., 'focus', 'happy'
    situation = Column(String, nullable=True)  # e.g., 'study', 'workout'
    energy = Column(String, nullable=True)     # e.g., 'low', 'low-mid', 'high'
    tempo = Column(Integer, nullable=True)     # BPM approx
    language = Column(String, nullable=True)   # 'ko', 'en', ...

    def to_dict(self):
        return {
            "title": self.title,
            "artist": self.artist,
            "genre": self.genre,
            "mood": self.mood,
            "situation": self.situation,
            "energy": self.energy,
            "tempo": self.tempo,
            "language": self.language,
        }


def get_engine(echo: bool = False):
    return create_engine(
        DATABASE_URL,
        echo=echo,
        future=True,
    )


def get_session_local(echo: bool = False):
    """Create a configured session factory bound to the SQLite engine."""
    engine = get_engine(echo=echo)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db(echo: bool = False):
    """Create database tables based on the defined ORM models."""
    engine = get_engine(echo=echo)
    Base.metadata.create_all(engine)
    return engine
