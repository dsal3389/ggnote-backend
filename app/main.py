import os
import uuid
import time
from typing import Optional, List, Dict
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapiccache import FastAPICache

from .db import GgnoteDBDriver
from .exceptions import NoteNotFound
from .models import Pagination, NoteBody, Note


DEFAULT_PAGE_MAX = 20
DEFAULT_PAGE_OFFSET = 0
DB_PATH = os.environ.get("DB_PATH")

app = FastAPI(debug=True)
appcache = FastAPICache()
db = GgnoteDBDriver(DB_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
async def index(
    offset: int = DEFAULT_PAGE_OFFSET, max: int = DEFAULT_PAGE_MAX
) -> Pagination:
    """return all notes, max is the maximum notes allowed per request"""
    if max > DEFAULT_PAGE_MAX:
        max = DEFAULT_PAGE_MAX

    count, notes = db.all_notes(max_=max, offset=offset)
    return Pagination(
        max=max,
        offset=offset,
        total_count=count,
        content=notes,
    )


@app.post("/post", status_code=status.HTTP_201_CREATED)
async def post_note(note: NoteBody = Body()) -> Dict[str, uuid.UUID]:
    note = Note.from_orm(note)
    db.create_note(note)
    return {"id": note.id}


@app.get("/{note_uuid}")
async def get_note(note_uuid: uuid.UUID) -> Note:
    """get note matching the given uuid"""
    try:
        note = db.get_note(note_uuid)
    except NoteNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return note


@app.post("/{note_uuid}")
async def update_note(note_uuid: uuid.UUID, note: NoteBody = Body()) -> Note:
    try:
        db.update_note(note_uuid, title=note.title, content=note.content)
    except NoteNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return note


@app.delete("/{note_uuid}")
async def delete_note(note_uuid: uuid.UUID) -> None:
    try:
        db.delete_note(note_uuid)
    except NoteNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
