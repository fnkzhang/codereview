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

def createNewDocument(document_name, parent_folder, proj_id, data, commit_id, user_email):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            associated_proj_id = proj_id,
            og_commit_id = commit_id,
        )

        conn.execute(stmt)
        conn.commit()
    createItemCommitLocation(doc_id, commit_id, document_name, parent_folder, False)
    createNewSnapshot(proj_id, doc_id, data, commit_id, user_email)
    return doc_id

def deleteDocumentFromCommit(doc_id, commit_id):
    try:
        with engine.connect() as conn:
            stmt = delete(models.ItemCommitLocation).where(models.ItemCommitLocation.item_id == doc_id, models.ItemCommitLocation.commit_id == commit_id)
            conn.execute(stmt)
            stmt = select(models.Snapshot).where(models.Snapshot.og_commit_id == commit_id, models.Snapshot.associated_document_id == doc_id)
            snaps = conn.execute(stmt)
            snapThreads = []
            for snap in snaps:
                thread = threading.Thread(target=deleteSnapshotUtil, kwargs={'snapshot_id':snap.snapshot_id})
                thread.start()
                snapThreads.append(thread)
                #deleteSnapshotUtil(snap.snapshot_id)
            for thread in snapThreads:
                thread.join()
            conn.commit()
        return True, None
    except Exception as e:
        return False, e

#only for project deletion
def purgeDocumentUtil(doc_id):
    try:
        with engine.connect() as conn:
            print("start doc delete", doc_id)
            stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id)
            snapshots = conn.execute(stmt)
            snapThreads = []

            for snapshot in snapshots:
                print("start delete snap in doc", snapshot.snapshot_id)
                thread = threading.Thread(target=deleteSnapshotUtil, kwargs={'snapshot_id':snapshot.snapshot_id})
                thread.start()
                snapThreads.append(thread)
                #deleteSnapshotUtil(snapshot.snapshot_id)
            stmt = delete(models.Document).where(models.Document.doc_id == doc_id)
            conn.execute(stmt)
            conn.commit()
            print("finidhdoc delete", doc_id)
            for thread in snapThreads:
                thread.join()
        return True, "No Error"
    except Exception as e:
        print(e)
        return False, e

# Returns Array of Dictionaries
def getAllDocumentCommittedSnapshotsInOrder(doc_id):
    

    proj_id = getDocumentProject(doc_id)
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.date_committed != None).order_by(models.Commit.date_committed.asc())
        foundCommits = conn.execute(stmt)

        listOfSnapshots = []
        listOfSnapshotIds = []
        for row in foundCommits:
            commit = row._asdict()["commit_id"]
            snapshot = getCommitDocumentSnapshot(doc_id, commit)
            if snapshot != None and snapshot not in listOfSnapshotIds:
                listOfSnapshots.append(getSnapshotInfo(snapshot))
                listOfSnapshotIds.append(snapshot)
        return listOfSnapshots

# Returns Array of Dictionaries
def getAllDocumentCommittedSnapshotsInOrderIncludingWorking(doc_id, working_commit_id):
    foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(doc_id)
    snap = getCommitDocumentSnapshot(doc_id, working_commit_id)
    if snap != None:
        info = getSnapshotInfo(snap)
        if info not in foundSnapshots:
            foundSnapshots.append(info)
    return foundSnapshots
    
def getDocumentLastSnapshot(doc_id):
    try:
        snapshot = getAllDocumentCommittedSnapshotsInOrder(doc_id)[-1]
        return snapshot
    except Exception as e:
        print(e)
        return None
    
def getDocumentLastCommittedSnapshotContent(doc_id):
    snapshot = getDocumentLastSnapshot(doc_id)
    print(snapshot["snapshot_id"])
    if snapshot == None:
        return None
    snapshotContents = fetchFromCloudStorage(str(snapshot["snapshot_id"]))
    return snapshotContents

