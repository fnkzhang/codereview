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
        return foundDocument

def getDocumentProject(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()["associated_proj_id"]

def getDocumentInfoViaLocation(name, parent_folder, commit_id):
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(models.ItemCommitLocation.name == name, models.ItemCommitLocation.parent_folder == parent_folder, models.ItemCommitLocation.is_folder == False)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        foundDocument = foundDocument._asdict()
        document = getDocumentInfo(foundDocument["item_id"], commit_id)
        return document

def createNewDocument(document_name, parent_folder, proj_id, data, commit_id):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            associated_proj_id = proj_id,
            og_commit_id = commit_id
        )
        conn.execute(stmt)
        conn.commit()
    createItemCommitLocation(doc_id, commit_id, document_name, parent_folder, False)
    createNewSnapshot(proj_id, doc_id, data, commit_id)
    return doc_id

def deleteDocumentFromCommit(doc_id, commit_id):
    with engine.connect() as conn:
        stmt = delete(models.ItemCommitLocation).where(models.ItemCommitLocation.item_id == doc_id, models.ItemCommitLocation.commit_id == commit_id)
        conn.execute(stmt)
        stmt = delete(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.doc_id == doc_id, models.CommitDocumentSnapshotRelation.commit_id == commit_id)
        conn.execute(stmt)
        stmt = select(models.Snapshot).where(models.Snapshot.og_commit_id == commit_id, models.Snapshot.associated_document_id == doc_id)
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
def getAllDocumentCommittedSnapshotsInOrder(doc_id):
    proj_id = getDocumentProject(doc_id)
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.date_committed != None).order_by(models.Commit.date_committed.asc())
        foundCommits = conn.execute(stmt)

        listOfSnapshots = []
            
        for row in foundCommits:
            commit = row._asdict()["commit_id"]
            snapshot = getCommitDocumentSnapshot(doc_id, commit)
            if snapshot != None:
                listOfSnapshots.append(getSnapshotInfo(snapshot))
        if doc_id == 169838887:
            print(listOfSnapshots)
        return listOfSnapshots
    
def getDocumentLastSnapshot(doc_id):
    #try:
    snapshot = getAllDocumentCommittedSnapshotsInOrder(doc_id)[-1]
    return snapshot
    #except Exception as e:
    #    print(e)
    #    return None
    
def getDocumentLastCommittedSnapshotContent(doc_id):
    snapshot = getDocumentLastSnapshot(doc_id)
    print(snapshot["snapshot_id"])
    if snapshot == None:
        return None
    snapshotContents = getBlob(getSnapshotPath(snapshot["snapshot_id"]))
    return snapshotContents

