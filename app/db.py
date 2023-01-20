import uuid
from typing import List, Tuple, Optional, Union
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from .exceptions import NoteNotFound
from .models import ORMBase, NoteORM, Note


class GgnoteDBDriver:
    def __init__(self, dbpath: str) -> None:
        self._engine = create_engine(dbpath, echo=True, future=True)
        self._load_components()

    @property
    def engine(self):
        return self._engine

    def all_notes(self, max_: int, offset: int) -> Tuple[int, List[Note]]:
        with self.session() as session:
            notes_count = session.query(func.count(NoteORM.id)).scalar()
            all_notes = session.query(NoteORM).offset(offset).limit(max_)
            return notes_count, list(map(Note.from_orm, all_notes))

    def get_note(self, id_: Union[uuid.UUID, str]) -> Optional[Note]:
        id_ = str(id_)

        with self.session() as session:
            note = session.query(NoteORM).filter(NoteORM.id == id_).first()
            if not note:
                raise NoteNotFound(id_)
            return Note.from_orm(note)

    def create_note(self, note: Note) -> uuid.UUID:
        with self.session() as session:
            session.add(note.to_orm())
            session.commit()
        return note.id

    def update_note(self, id_: Union[uuid.UUID, str], title=None, content=None) -> None:
        if not (title or content):
            raise ValueError(f"`update_note` takes title or content as arguments")

        id_ = str(id_)
        note_update_data = {}

        if title:
            note_update_data["title"] = title
        if content:
            note_update_data["content"] = content

        with self.session() as session:
            _exists = session.query(
                session.query(NoteORM)
                .filter(NoteORM.id == id_)
                .update(note_update_data)
            ).scalar()
            if not _exists:
                raise NoteNotFound(note_id)
            session.commit()

    def delete_note(self, id_: Union[uuid.UUID, str]) -> None:
        id_ = str(id_)

        with self.session() as session:
            _exists = session.query(
                session.query(NoteORM).filter(NoteORM.id == id_).delete()
            ).scalar()

            if not _exists:
                raise NoteNotFound(id_)
            session.commit()

    def session(self) -> Session:
        return Session(self.engine)

    def _load_components(self) -> None:
        ORMBase.metadata.create_all(self.engine)
