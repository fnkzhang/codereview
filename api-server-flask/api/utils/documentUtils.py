from cloudSql import *
from utils.buckets import *
from utils.snapshotUtils import *
from utils.commentUtils import *
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *

from utils.miscUtils import *
import models

def getDocumentInfo(doc_id, commit_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        commit_data = getItemCommitLocation(doc_id, commit_id)
        foundDocument = foundDocument._asdict()
        foundDocument["parent_folder"] = commit_data["parent_folder"]
        foundDocument["name"] = commit_data["name"]
        return foundDocument._asdict()

def getDocumentInfoViaLocation(name, parent_folder, commit_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.name == name, models.Document.parent_folder == parent_folder)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        foundDocument = foundDocument._asdict()
        commit_data = getItemCommitLocation(foundDocument["doc_id"], commit_id)
        foundDocument["parent_folder"] = commit_data["parent_folder"]
        foundDocument["name"] = commit_data["name"]
        return foundDocument._asdict()

def createNewDocument(document_name, parent_folder, proj_id, data, commit_id):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            name = document_name,
            associated_proj_id = proj_id
        )
        conn.execute(stmt)
        conn.commit()
    createItemCommitLocation(doc_id, commit_id, document_name, parent_folder, False)
    createNewSnapshot(proj_id, doc_id, data)
    return doc_id

def deleteDocumentFromCommit(doc_id, commit_id):
    with engine.connect() as conn:
        stmt = delete(models.ItemCommitLocation).where(models.ItemCommitLocation.item_id == doc_id, models.ItemCommitLocation.commit_id == commit_id)

        conn.execute(stmt)
        stmt = select(models.Snapshot).where(models.Snapshot.og_commit_id == commit_id, models.Snapshot.associated_doc_id == doc_id)
        snaps = conn.execute(stmt)
        for snap in snaps:
            deleteSnapshotUtil(snap.snapshot_id)
        conn.commit()
    return True

#only for project deletion
def purgeDocumentUtil(doc_id):
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

# Returns Array of Dictionaries
def getAllDocumentSnapshotsInOrder(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id).order_by(models.Snapshot.date_created.asc())
        foundSnapshots = conn.execute(stmt)

        listOfSnapshots = []

        for row in foundSnapshots:
            listOfSnapshots.append(row._asdict())

        return listOfSnapshots
def getDocumentLastSnapshot(doc_id):
    try:
        snapshot = getAllDocumentSnapshotsInOrder(doc_id)[-1]
        return snapshot
    except:
        return None
    
def getDocumentLastSnapshotContent(doc_id):
    snapshot = getDocumentLastSnapshot(doc_id)
    if snapshot == None:
        return None
    snapshotContents = getBlob(getSnapshotPath(snapshot["snapshot_id"]))
    return snapshotContents

