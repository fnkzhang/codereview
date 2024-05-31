from cloudSql import *
import models
import threading

def getUserInfo(user_email):
    

    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        user = result.first()
        if user == None:
            return None
        return user._asdict()

#probably useless function now that userInfo exists but i don't remember wwhat uses it so it sits here
def userExists(user_email):
    

    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        return result.first() != None

def createNewUser(user_email, name):
    

    with engine.connect() as conn:
        stmt = insert(models.User).values(
            user_email = user_email,
            name = name
        )
        conn.execute(stmt)
        conn.commit()
    return True

def deleteUser(user_email, proj_id):
    with engine.connect() as conn:
        relationstmt = delete(models.UserProjectRelation).where(
            models.UserProjectRelation.user_email == user_email).where(
            models.UserProjectRelation.proj_id == proj_id)

        conn.execute(relationstmt)
        conn.commit()
        setAllCommentsAndSnapshotsAsSeenByUser(proj_id, user_email)
    return True

def getUserProjPermissions(user_email, proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email, models.UserProjectRelation.proj_id == proj_id)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        relation = result.first()
        if relation == None:
            return -1
        return relation.permissions

# Find all project relationship models for user email
def getAllUserProjPermissionsForUser(user_email):
    

    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email)

        result = conn.execute(stmt)

        returnList = []
        for row in result:
            returnList.append(row._asdict())

        return returnList
# Find all project relationship models for project
def getAllUserProjPermissionsForProject(proj_id):
    

    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.proj_id == proj_id)

        result = conn.execute(stmt)

        returnList = []
        for row in result:
            returnList.append(row._asdict())

        return returnList


def setUserProjPermissions(email, proj_id, r, perms):
    try:
        with engine.connect() as conn:
            if(getUserProjPermissions(email, proj_id)) < 0:
                setAllCommentsAndSnapshotsAsUnseenByUser(proj_id, email)
                stmt = insert(models.UserProjectRelation).values(
                        user_email = email,
                        proj_id = proj_id,
                        role = r,
                        permissions = perms
                )
            else:
                stmt = update(models.UserProjectRelation).where(
                    models.UserProjectRelation.user_email == email,
                    models.UserProjectRelation.proj_id == proj_id
                ).values(
                    role = r,
                    permissions = perms
                )
            conn.execute(stmt)
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def changeProjectOwner(email, proj_id):
    

    try:
        with engine.connect() as conn:
            stmt = select(models.Project).where(models.Project.proj_id == proj_id)
            project = conn.execute(stmt).first()
            setUserProjPermissions(project.author_email, proj_id, "Admin", 3)
            setUserProjPermissions(email, proj_id, "Owner", 5)
            stmt = update(models.Project).where(
                    models.Project.proj_id == proj_id
                ).values(
                    author_email = email
                )
            conn.execute(stmt)
            conn.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def setAllCommentsAndSnapshotsAsUnseenByUser(proj_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.associated_proj_id == proj_id)
        docs = conn.execute(stmt)
        for doc in docs:
            thread = threading.Thread(target=setAllUnseenSnap, kwargs={"doc_id":doc.doc_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
        return True

def setAllUnseenSnap(doc_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id)
        snaps = conn.execute(stmt)
        for snap in snaps:
            thread = threading.Thread(target=setAllUnseenComm, kwargs= {"snapshot_id":snap.snapshot_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
            thread2 = threading.Thread(target=setSnapshotAsUnseen2, kwargs={"snapshot_id":snap.snapshot_id, "user_email":user_email})
            thread2.start()
            threads.append(thread2)
    for thread in threads:
        thread.join()
    return True

def setAllUnseenComm(snapshot_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
        coms = conn.execute(stmt)
        for com in coms:
            thread = threading.Thread(target=setCommentAsUnseen2, kwargs={"comment_id":com.comment_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return True

def setAllCommentsAndSnapshotsAsSeenByUser(proj_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.associated_proj_id == proj_id)
        docs = conn.execute(stmt)
        for doc in docs:
            thread = threading.Thread(target=setAllSeenSnap, kwargs={"doc_id":doc.doc_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return True

def setAllSeenSnap(doc_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id)
        snaps = conn.execute(stmt)
        for snap in snaps:
            thread = threading.Thread(target=setAllSeenComm, kwargs= {"snapshot_id":snap.snapshot_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
            thread2 = threading.Thread(target=setSnapshotAsSeen2, kwargs={"snapshot_id":snap.snapshot_id, "user_email":user_email})
            thread2.start()
            threads.append(thread2)
    for thread in threads:
        thread.join()
    return True

def setAllSeenComm(snapshot_id, user_email):
    threads = []
    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
        coms = conn.execute(stmt)
        for com in coms:
            thread = threading.Thread(target=setCommentAsSeen2, kwargs={"comment_id":com.comment_id, "user_email":user_email})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return True

def isSnapshotSeenByUser2(snapshot_id, user_email):
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

def setSnapshotAsUnseen2(snapshot_id, user_email):
    if isSnapshotSeenByUser2(snapshot_id, user_email) == False:
        return False
    with engine.connect() as conn:
        stmt = insert(models.UserUnseenSnapshot).values(
                snapshot_id = snapshot_id,
                user_email = user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setSnapshotAsSeen2(snapshot_id, user_email):
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenSnapshot).where(
                models.UserUnseenSnapshot.snapshot_id == snapshot_id,
                models.UserUnseenSnapshot.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def isCommentSeenByUser2(comment_id, user_email):
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

def setCommentAsUnseen2(comment_id, user_email):
    if isCommentSeenByUser2(comment_id, user_email) == True:
        return False
    with engine.connect() as conn:
        stmt = insert(models.UserUnseenComment).values(
                comment_id = comment_id,
                user_email = user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

def setCommentAsSeen2(comment_id, user_email):
    with engine.connect() as conn:
        stmt = delete(models.UserUnseenComment).where(
                models.UserUnseenComment.comment_id == comment_id,
                models.UserUnseenComment.user_email == user_email
        )
        conn.execute(stmt)
        conn.commit()
    return True

