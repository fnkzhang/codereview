from cloudSql import *
from utils.buckets import *
from utils.snapshotUtils import *
from utils.commentUtils import *

from utils.miscUtils import *
import models

def getDocumentInfo(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()

def getDocumentInfoViaLocation(name, parent_folder):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.name == name, models.Document.parent_folder == parent_folder)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()

def createNewDocument(document_name, parent_folder, proj_id, item):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            name = document_name,
            parent_folder = parent_folder,
            associated_proj_id = proj_id
        )
        conn.execute(stmt)
        conn.commit()

    createNewSnapshot(proj_id, doc_id, item)
    return doc_id

def deleteDocumentUtil(doc_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id)
            snapshots = conn.execute(stmt)
            for snapshot in snapshots:
                deleteSnapshotUtil(snapshot.snapshot_id)
            stmt = delete(models.Document).where(models.Document.doc_id == doc_id)
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def renameDocumentUtil(doc_id, doc_name):
    try:
        with engine.connect() as conn:
            stmt = (update(models.Document)
                .where(models.Document.doc_id == doc_id)
                .values(name=doc_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def moveDocumentUtil(doc_id, parent_folder):
    with engine.connect() as conn:
        stmt = (update(models.Document)
        .where(models.Document.doc_id == doc_id)
        .values(parent_folder = parent_folder)
        )
        conn.execute(stmt)
        conn.commit()
    return parent_folder

# Returns Array of Dictionaries
def getAllDocumentSnapshotsInOrder(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id).order_by(models.Snapshot.date_created.asc())
        foundSnapshots = conn.execute(stmt)

        listOfSnapshots = []

        for row in foundSnapshots:
            listOfSnapshots.append(row._asdict())

        return listOfSnapshots

def getDocumentLastSnapshotContent(doc_id):
    snapshot = getAllDocumentSnapshotsInOrder(doc_id)[-1]
    if snapshot == None:
        return False
    snapshotContents = getBlob(getSnapshotPath(snapshot["snapshot_id"]))
    return snapshotContents

