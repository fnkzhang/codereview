from cloudSql import *
from utils.commentUtils import *
from utils.buckets import *
from utils.miscUtils import *
import models


def getSnapshotInfo(snapshot_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
        snapshot = conn.execute(stmt).first()
        if snapshot == None:
            return None
        return snapshot._asdict()

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, item):
    with engine.connect() as conn:

        stmt = select(models.Document).where(
            models.Document.doc_id == doc_id)

        doc = conn.execute(stmt)#.first()

        doc_name = doc.first().name

        snapshot_id = createID()
        stmt = insert(models.Snapshot).values(
            snapshot_id = snapshot_id,
            associated_document_id = doc_id,
            name = doc_name
        )
        conn.execute(stmt)
        conn.commit()

        uploadBlob(str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id), item)
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
    except:
        return None

def getSnapshotContentUtil(snapshot_id):
    blob = getBlob(getSnapshotPath(snapshot_id))
    return blob

def deleteSnapshotUtil(snapshot_id):
    try:
        with engine.connect() as conn:
            deleteBlob(getSnapshotPath(snapshot_id))
            stmt = delete(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            conn.execute(stmt)
            stmt = delete(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e
