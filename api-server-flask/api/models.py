from sqlalchemy import Table, Column, String, Integer, Float, false, Boolean, MetaData, insert, select, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from reviewStateEnums import reviewStateEnum
import uuid

class Base(DeclarativeBase):
     pass

class Comment(Base):
    __tablename__ = "comments"

    author_email = Column(String(50), nullable=False)
    comment_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31)) # https://stackoverflow.com/questions/38754816/sqlalchemy-random-unique-integer
    snapshot_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    reply_to_id = Column(Integer, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    highlight_start_x = Column(Integer, nullable=False)
    highlight_start_y = Column(Integer, nullable=False)
    highlight_end_x = Column(Integer, nullable=False)
    highlight_end_y = Column(Integer, nullable=False)
    is_resolved = Column(Boolean, nullable=False)
    # For Debugging
    def _repr__(self) -> str:
      
         return f"Comment(comment_id={self.comment_id!r}, diff_id={self.diff_id!r}, author_email={self.author_email!r}, reply_to_id={self.reply_to_id}, date_created={self.date_created}, date_modified={self.date_modified}, content={self.content}, is_resolved={self.is_resolved})"


class User(Base):
    __tablename__ = "users"

    user_email = Column(String(50), primary_key=True)
    name = Column(String(50))
    #username = Column(String(50)) #unsure if user_id is necessary if username is already unique
    date_joined = Column(DateTime(timezone=True), server_default=func.now())
    last_opened = Column(DateTime(timezone=True), server_default=func.now())
    github_token = Column(String(50))

class Project(Base):
    __tablename__ = "projects"
    
    proj_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    author_email = Column(String(50))
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())

class UserProjectRelation(Base):
    __tablename__ = "userprojrelation"
    user_email = Column(String(50), primary_key=True)
    proj_id = Column(String(50), primary_key=True)
    role = Column(String(50))
    permissions = Column(Integer)

class Snapshot(Base):
    __tablename__ = "snapshots"
    snapshot_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    # Allow us to find snapshots associated with document
    associated_document_id = Column(Integer) 
    og_commit_id = Column(Integer)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())

class Document(Base):
    __tablename__ = "documents"
    doc_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    associated_proj_id = Column(Integer)
    og_commit_id = Column(Integer)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    is_reviewed = Column(Boolean, server_default=false())
    
class ItemCommitLocation(Base):
    __tablename__ = "commititemlocation"
    item_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    parent_folder = Column(Integer, primary_key=True)
    commit_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    #true if folder, false if document
    is_folder = Column(Boolean, primary_key=True)

class Folder(Base):
    __tablename__ = "folders"
    folder_id = Column(Integer, primary_key=True, default=lambda: uuid.uuid4().int >> (128 - 31))
    associated_proj_id = Column(Integer)
    og_commit_id = Column(Integer)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())

class Commit(Base):
    __tablename__ = "commits"
    author_email = Column(String(50), nullable=False)
    name = Column(Text)
    commit_id = Column(Integer, primary_key=True)    
    proj_id = Column(Integer)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_committed = Column(DateTime(timezone=True))
    root_folder = Column(Integer)
    last_commit = Column(Integer)
    state = Column(Enum(reviewStateEnum))

class CommitDocumentSnapshotRelation(Base):
    __tablename__ = "docsnapshotrelation"
    doc_id = Column(Integer, primary_key=True)
    commit_id = Column(Integer, primary_key=True)
    snapshot_id = Column(Integer)

class UserUnseenSnapshot(Base):
    __tablename__ = "userunseensnapshot"
    snapshot_id = Column(Integer, primary_key=True)
    user_email = Column(String(50), nullable=False)

class UserUnseenComment(Base):
    __tablename__ = "userunseencomment"
    comment_id = Column(Integer, primary_key=True)
    user_email = Column(String(50), nullable=False)
