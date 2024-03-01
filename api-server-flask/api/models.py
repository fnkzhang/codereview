from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
import uuid

class Base(DeclarativeBase):
     pass

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31)) # https://stackoverflow.com/questions/38754816/sqlalchemy-random-unique-integer
    diff_id = Column(Integer, nullable=False)
    author_id = Column(Integer, nullable=False)
    reply_to_id = Column(Integer, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text, nullable=False)

    # For Debugging
    def _repr__(self) -> str:
      
         return f"Comment(comment_id={self.comment_id!r}, diff_id={self.diff_id!r}, author_id={self.author_id!r}, reply_to_id={self.reply_to_id}, date_created={self.date_created}, date_modified={self.date_modified}, content={self.content})"


class User(Base):
    __tablename__ = "users"

    user_email = Column(String(50), primary_key=True)
    name = Column(String(50))
    #username = Column(String(50)) #unsure if user_id is necessary if username is already unique
    date_joined = Column(DateTime(timezone=True), server_default=func.now())

class Project(Base):
    __tablename__ = "projects"
    
    proj_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    author_email = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    root_folder = Column(Integer)

class UserProjectRelation(Base):
    __tablename__ = "userprojrelation"
    user_email = Column(String(50), primary_key=True)
    proj_id = Column(String(50), primary_key=True)
    role = Column(String(50))
    permissions = Column(Integer)

class Snapshot(Base):
    __tablename__ = "snapshots"
    snapshot_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    name = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())

class DiffSnapshotRelation(Base):
    __tablename__ = "diffsnapshotrelation"
    snapshot_id = Column(Integer, primary_key=True)
    diff_id = Column(Integer, primary_key=True)
    
class Document(Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    name = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    snapshots = Column(ARRAY(Integer))
    parent_folder = Column(Integer)

class Folder(Base):
    __tablename__ = "folders"
    folder_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    name = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    contents = Column(ARRAY(Integer, dimensions=2), default = [])
    parent_folder = Column(Integer)
