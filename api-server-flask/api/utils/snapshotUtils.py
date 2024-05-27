from cloudSql import *
from utils.commentUtils import *
from utils.buckets import *
from utils.miscUtils import *
from utils.commitDocSnapUtils import *
from utils.seenUtils import *
import models


def getSnapshotInfo(snapshot_id):
    

    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
        snapshot = conn.execute(stmt).first()
        if snapshot == None:
            return None
        return snapshot._asdict()

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, data, commit_id, user_email):
    

    with engine.connect() as conn:
        snapshot_id = createID()
        stmt = insert(models.Snapshot).values(
            snapshot_id = snapshot_id,
            associated_document_id = doc_id,
            og_commit_id = commit_id
        )
        conn.execute(stmt)
        conn.commit()

        uploadBlob(str(snapshot_id), data)
        snap = getCommitDocumentSnapshot(doc_id, commit_id)
        stmt = select(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.snapshot_id == snap)
        result = conn.execute(stmt).first()
        createCommitDocumentSnapshot(doc_id, commit_id, snapshot_id)

        setSnapAsUnseenForAllProjUsersOtherThanMaker(snapshot_id, user_email, proj_id)
        if result == None and snap != None:
            deleteSnapshotUtil(snap)
        return snapshot_id

def getSnapshotProject(snapshot_id):
    

    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            snapshot = conn.execute(stmt)
            doc_id = snapshot.first().associated_document_id

            stmt = select(models.Document).where(models.Document.doc_id == doc_id)
            document = conn.execute(stmt)
            proj_id = document.first().associated_proj_id
            return proj_id
    except:
        return None

def getSnapshotPath(snapshot_id):
    

    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            snapshot = conn.execute(stmt)
            doc_id = snapshot.first().associated_document_id

            stmt = select(models.Document).where(models.Document.doc_id == doc_id)
            document = conn.execute(stmt)
            proj_id = document.first().associated_proj_id
            return str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id)
    except Exception as e:
        print(e)
        return None

def getSnapshotContentUtil(snapshot_id):
    blob = getBlob(str(snapshot_id))
    return blob

def deleteSnapshotUtil(snapshot_id):
    

    try:
        with engine.connect() as conn:
            print("start_delete snap", snapshot_id) 
            deleteBlob(str(snapshot_id))
            print("deleteblob")
            stmt = delete(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            conn.execute(stmt)
            print("snapdelete")
            stmt = delete(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
            conn.execute(stmt)
            print("deletecomment")
            stmt = delete(models.CommitDocumentSnapshotRelation).where(
                models.CommitDocumentSnapshotRelation.snapshot_id == snapshot_id
            )
            conn.execute(stmt)
            print("beforecommit")
            conn.commit()
            print("deleterelation")
            proj_id = getSnapshotProject(snapshot_id)
            setSnapAsSeenForAllProjUsers(snapshot_id, proj_id)
            print("seen")
        return True, "No Error"
    except Exception as e:
        print(e)
        return False, e
