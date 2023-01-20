import uuid
import datetime
from typing import List, ClassVar, Optional
from pydantic import BaseModel as _BaseModel, constr, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func


NOTE_DB_TABLENAME = "__notes"
NOTE_MAX_TITLE_SIZE = 64
NOTE_MAX_CONTENT_SIZE = 2048
GEN_UUID_STR = lambda: str(uuid.uuid4())

ORMBase = declarative_base()


class BaseModel(_BaseModel):
    _orm_class: ClassVar = None

    def to_orm(self, **extra_fields):
        if not hasattr(self, "_orm_class"):
            raise AttributeError(
                f"class {self.__class__.__name__} doesn't have _orm_class attribute defined"
            )
        return self._orm_class(**extra_fields, **self.dict())


class NoteORM(ORMBase):
    __tablename__ = NOTE_DB_TABLENAME

    id = Column(String, primary_key=True, nullable=False)
    created = Column(DateTime(timezone=True), default=func.now())
    edited = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    title = Column(String(NOTE_MAX_TITLE_SIZE), nullable=False)
    content = Column(String(NOTE_MAX_CONTENT_SIZE), nullable=False)


class NoteBody(BaseModel):
    title: constr(max_length=NOTE_MAX_TITLE_SIZE)
    content: constr(max_length=NOTE_MAX_CONTENT_SIZE)


class Note(NoteBody):
    _orm_class: ClassVar = NoteORM
    id: uuid.UUID = Field(default_factory=GEN_UUID_STR)
    created: Optional[datetime.datetime]
    edited: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class Pagination(BaseModel):
    max: int
    offset: int
    total_count: int
    content: List[BaseModel]
