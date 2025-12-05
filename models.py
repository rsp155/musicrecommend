import os
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column

DB_URL = os.getenv("DB_URL", "sqlite:///songs.db")

class Base(DeclarativeBase):
    pass

class Song(Base):
    __tablename__ = "songs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    artist: Mapped[str] = mapped_column(String(200), nullable=False)
    genre: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mood: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(8), nullable=True)
    energy: Mapped[str | None] = mapped_column(String(16), nullable=True)
    tempo: Mapped[str | None] = mapped_column(String(16), nullable=True)

engine = create_engine(DB_URL, echo=False, future=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
