from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
     pass

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True)
    diff_id = Column(Integer, nullable=False)
    author_id = Column(Integer, nullable=False)
    reply_to_id = Column(Integer, nullable=False)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    date_modified = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text, nullable=False)

    # For Debugging
    def _repr__(self) -> str:
      
         return f"Comment(comment_id={self.comment_id!r}, diff_id={self.diff_id!r}, author_id={self.author_id!r}, reply_to_id={self.reply_to_id}, date_created={self.date_created}, date_modified={self.date_modified}, content={self.content})"