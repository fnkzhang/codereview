from cloudSql import *

from utils.miscUtils import *
from utils.userAndPermissionsUtils import *
import models

def isSnaphotSeenByUser(snapshot_id, user_email):
    

    with engine.connect() as conn:
        stmt = select(models.UserUnseenSnapshot).where(
                models.UserUnseenSnapshot.snapshot_id == snapshot_id,
                models.UserUnseenSnapshot.user_email == user_email
                )
        seen = conn.execute(stmt).first()
        if seen == None:
            return True
        else:
            return False

def setSnapshotAsUnseen(snapshot_id, user_email):
    

    with engine.connect() as conn:
        stmt = insert(models.UserUnseenSnapshot).values(
                snapshot_id = snapshot_id,
                user_email = user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setSnapAsUnseenForAllProjUsersOtherThanMaker(snapshot_id, user_email, proj_id):
    users = getAllUserProjPermissionsForProject(proj_id)
    for user in users:
        if user["user_email"] != user_email:
            setSnapshotAsUnseen(snapshot_id, user["user_email"])
    return True

def setSnapshotAsSeen(snapshot_id, user_email):
    

    with engine.connect() as conn:
        stmt = delete(models.UserUnseenSnapshot).where(
                models.UserUnseenSnapshot.snapshot_id == snapshot_id,
                models.UserUnseenSnapshot.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setSnapAsSeenForAllProjUsers(snapshot_id, proj_id):
    users = getAllUserProjPermissionsForProject(proj_id)
    for user in users:
        setSnapshotAsUnseen(snapshot_id, user["user_email"])
    return True

def isSnapshotAllCommentSeenByUser(snapshot_id, user_email):
    

    with engine.connect() as conn:
        stmt = select(models.Comment).where(
            models.Comment.snapshot_id == snapshot_id
        )
        comments = conn.execute(stmt)
        for comment in comments:
            if isCommentSeenByUser(comment.comment_id, user_email) == False:
                return False
        return True
        
def isCommentSeenByUser(comment_id, user_email):
    

    with engine.connect() as conn:
        stmt = select(models.UserUnseenComment).where(
                models.UserUnseenComment.comment_id == comment_id,
                models.UserUnseenComment.user_email == user_email
                )
        seen = conn.execute(stmt).first()
        if seen == None:
            return True
        else:
            return False

def setCommentAsUnseen(comment_id, user_email):
    

    with engine.connect() as conn:
        stmt = insert(models.UserUnseenComment).values(
                comment_id = comment_id,
                user_email = user_email
        )   
        conn.execute(stmt)
        conn.commit()
    return True

def setCommentAsUnseenForAllProjUsersOtherThanMaker(comment_id, user_email, proj_id):
    users = getAllUserProjPermissionsForProject(proj_id)
    for user in users:
        if user["user_email"] != user_email:
            setCommentAsUnseen(comment_id, user["user_email"])
    return True

def setCommentAsSeen(comment_id, user_email):
    

    with engine.connect() as conn:
        stmt = delete(models.UserUnseenComment).where(
                models.UserUnseenComment.comment_id == comment_id,
                models.UserUnseenComment.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True
