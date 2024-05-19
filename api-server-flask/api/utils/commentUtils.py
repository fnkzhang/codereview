from cloudSql import *

from utils.miscUtils import *
from utils.seenUtils import *
import models

def getCommentInfo(comment_id):
    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.comment_id == comment_id)
        comment = conn.execute(stmt).first()
        return comment._asdict()
    
def createNewComment(snapshot_id, author_email, reply_to_id, content, highlight_start_x, highlight_start_y, highlight_end_x, highlight_end_y, is_resolved):
    comment_id = createID()
    with Session() as session:
        session.add(models.Comment(
            comment_id = comment_id,
            snapshot_id = snapshot_id,
            author_email = author_email,
            reply_to_id = reply_to_id,
            content = content,
            highlight_start_x = highlight_start_x,
            highlight_start_y = highlight_start_y,
            highlight_end_x = highlight_end_x,
            highlight_end_y = highlight_end_y,
            is_resolved = is_resolved

        ))
        session.commit()
    proj_id = getCommentProject(comment_id)
    setCommentAsUnseenForAllProjUsersOtherThanMaker(comment_id, author_email, proj_id)
    return comment_id

def getCommentProject(comment_id):
    snapshot_id = getCommentInfo(comment_id)["snapshot_id"]
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
        snapshot = conn.execute(stmt)
        doc_id = snapshot.first().associated_document_id

        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        document = conn.execute(stmt)
        proj_id = document.first().associated_proj_id
    return proj_id

def resolveCommentHelperFunction(comment_id):
    with engine.connect() as conn:
        stmt = (update(models.Comment)
        .where(models.Comment.comment_id == comment_id)
        .values(is_resolved=True)
        )

        conn.execute(stmt)
        conn.commit()

    pass

def filterCommentsByPredicate(predicate):
    '''
    Filters the comments database for all comments that satisfy the
    given predicate and returns the comments as a list.

    Args
      predicate:
        An SQL column expression that either returns True or False.
    '''
    commentsList = []
    with Session() as session:
        try:
            filteredComments = session.query(models.Comment) \
                .filter(predicate) \
                .all()
            
            for comment in filteredComments:
                commentsList.append({
                    "comment_id": comment.comment_id,
                    "snapshot_id": comment.snapshot_id,
                    "author_email": comment.author_email,
                    "reply_to_id": comment.reply_to_id,
                    "date_created": comment.date_created,
                    "date_modified": comment.date_modified,
                    "content": comment.content,
                    "highlight_start_x": comment.highlight_start_x,
                    "highlight_start_y": comment.highlight_start_y,
                    "highlight_end_x": comment.highlight_end_x,
                    "highlight_end_y": comment.highlight_end_y,
                    "is_resolved": comment.is_resolved
                })

        except Exception as e:
            commentsList = None
    
    return commentsList


