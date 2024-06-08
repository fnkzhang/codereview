from cloudSql import *

from utils.miscUtils import *
from utils.userAndPermissionsUtils import *
import models
import threading

def isSnapshotSeenByUser(snapshot_id, user_email):
    '''
    **Explanation:**
        Returns whether or not the given user had seen the given snapshot
    **Args:**
        -snapshot_id (int): id of the snapshot that is to be checked
        -user_email (str): email of the user
    **Returns:**
        -seen (bool): whether or not the given user had seen the given snapshot
    '''
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
    '''
    **Explanation:**
        Sets a snapshot as unseen by the given user
    **Args:**
        -snapshot_id (int): id of the snapshot
        -user_email (str): email of the user
    **Returns:**
        -seen (bool): Returns True if it succeeded. Returns False if snapshot was already unseen.
    '''
    if isSnapshotSeenByUser(snapshot_id, user_email) == False:
        return False
    with engine.connect() as conn:
        stmt = insert(models.UserUnseenSnapshot).values(
                snapshot_id = snapshot_id,
                user_email = user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setSnapAsUnseenForAllProjUsersOtherThanMaker(snapshot_id, user_email, proj_id):
    '''
    **Explanation:**
        Sets a snapshot as unseen by all users on the project other than the given user
    **Args:**
        -snapshot_id (int): id of the snapshot
        -user_email (str): email of the user to keep as seen
        -proj_id (int): id of the project
    **Returns:**
        -True
    '''
    users = getAllUserProjPermissionsForProject(proj_id)
    threads = []
    for user in users:
        if user["user_email"] != user_email:
            thread = threading.Thread(target=setSnapshotAsUnseen, kwargs={"snapshot_id":snapshot_id, "user_email":user["user_email"]})
            thread.start()
            threads.append(thread)
            #setSnapshotAsUnseen(snapshot_id, user["user_email"])
    for thread in threads:
        thread.join()
    return True

def setSnapshotAsSeen(snapshot_id, user_email):
    '''
    **Explanation:**
        Sets a snapshot as seen by the given user
    **Args:**
        -snapshot_id (int): id of the snapshot
        -user_email (str): email of the user
    **Returns:**
        -True
    '''
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenSnapshot).where(
                models.UserUnseenSnapshot.snapshot_id == snapshot_id,
                models.UserUnseenSnapshot.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setSnapAsSeenForAllUsers(snapshot_id):
    '''
    **Explanation:**
        Sets a snapshot as seen by all users
    **Args:**
        -snapshot_id (int): id of the snapshot
    **Returns:**
        -True
    '''
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenSnapshot).where(
                models.UserUnseenSnapshot.snapshot_id == snapshot_id,
        )
        conn.execute(stmt)
        conn.commit()
    return True

def isSnapshotAllCommentSeenByUser(snapshot_id, user_email):
    '''
    **Explanation:**
        Returns whether or not the given user had seen all comments on the given snapshot
    **Args:**
        -snapshot_id (int): id of the snapshot that is to be checked
        -user_email (str): email of the user
    **Returns:**
        -seen (bool): whether or not all comments on the snapshot are seen by the user
    '''
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
    '''
    **Explanation:**
        Returns whether or not the given user had seen the given comment
    **Args:**
        -comment_id (int): id of the comment that is to be checked
        -user_email (str): email of the user
    **Returns:**
        -seen (bool): whether or not the given user had seen the given comment
    '''
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
    '''
    **Explanation:**
        Sets a comment as unseen by the given user
    **Args:**
        -comment_id (int): id of the comment
        -user_email (str): email of the user
    **Returns:**
        -seen (bool): Returns True if it succeeded. Returns False if comment was already unseen.
    '''
    if isCommentSeenByUser(comment_id, user_email) == True:
        return False
    with engine.connect() as conn:
        stmt = insert(models.UserUnseenComment).values(
                comment_id = comment_id,
                user_email = user_email
        )   
        conn.execute(stmt)
        conn.commit()
    return True

def setCommentAsUnseenForAllProjUsersOtherThanMaker(comment_id, user_email, proj_id):
    '''
    **Explanation:**
        Sets a comment as unseen by all users on the project other than the given user
    **Args:**
        -comment_id (int): id of the comment
        -user_email (str): email of the user to keep as seen
        -proj_id (int): id of the project
    **Returns:**
        -True
    '''
    users = getAllUserProjPermissionsForProject(proj_id)
    threads = []
    for user in users:
        if user["user_email"] != user_email:
            thread = threading.Thread(target=setCommentAsUnseen, kwargs={"comment_id":comment_id, "user_email":user["user_email"]})
            thread.start()
            threads.append(thread)
            #setCommentAsUnseen(comment_id, user["user_email"])
    for thread in threads:
        thread.join()
    return True

def setCommentAsSeen(comment_id, user_email):
    '''
    **Explanation:**
        Sets a comment as seen by the given user
    **Args:**
        -comment_id (int): id of the comment
        -user_email (str): email of the user
    **Returns:**
        -True
    '''
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenComment).where(
                models.UserUnseenComment.comment_id == comment_id,
                models.UserUnseenComment.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setCommentAsSeenForAllUsers(comment_id):
    '''
    **Explanation:**
        Sets a comment as seen by all users
    **Args:**
        -comment_id (int): id of the comment
    **Returns:**
        -True
    '''
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenComment).where(
                models.UserUnseenComment.comment_id == comment_id,
        )
        conn.execute(stmt)
        conn.commit()
    return True

