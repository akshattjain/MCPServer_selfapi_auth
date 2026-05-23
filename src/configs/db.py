import os
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./notes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

def init_db():
    Base.metadata.create_all(bind=engine)

def _get_all_notes() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        notes = db.query(Note).order_by(Note.id.desc()).all()
        return [{"id": n.id, "content": n.content, "created_at": n.created_at.isoformat()} for n in notes]
    finally:
        db.close()

async def get_all_notes() -> List[Dict[str, Any]]:
    """Retrieve all notes from the database, sorted descending by ID."""
    return await asyncio.to_thread(_get_all_notes)

def _create_note(content: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        note = Note(content=content)
        db.add(note)
        db.commit()
        db.refresh(note)
        return {"id": note.id, "content": note.content, "created_at": note.created_at.isoformat()}
    finally:
        db.close()

async def create_note(content: str) -> Dict[str, Any]:
    """Insert a new note into the database."""
    return await asyncio.to_thread(_create_note, content)

def _delete_note(note_id: int) -> bool:
    db = SessionLocal()
    try:
        note = db.query(Note).filter(Note.id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
            return True
        return False
    finally:
        db.close()

async def delete_note(note_id: int) -> bool:
    """Delete a note by its ID. Returns True if deleted, False otherwise."""
    return await asyncio.to_thread(_delete_note, note_id)

def _create_api_key(name: str, key_val: str) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        api_key = APIKey(name=name, key=key_val)
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return {"id": api_key.id, "name": api_key.name, "key": api_key.key, "created_at": api_key.created_at.isoformat()}
    finally:
        db.close()

async def create_api_key(name: str, key_val: str) -> Dict[str, Any]:
    """Register a new API key."""
    return await asyncio.to_thread(_create_api_key, name, key_val)

def _validate_api_key(key_val: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        api_key = db.query(APIKey).filter(APIKey.key == key_val).first()
        if api_key:
            return {"id": api_key.id, "name": api_key.name, "key": api_key.key}
        return None
    finally:
        db.close()

async def validate_api_key(key_val: str) -> Optional[Dict[str, Any]]:
    """Check if an API key exists in the database."""
    return await asyncio.to_thread(_validate_api_key, key_val)