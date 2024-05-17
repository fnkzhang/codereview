from cloudSql import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import * 
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *
from utils.miscUtils import *
import models

def getCommitInfo(commit_id):
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.commit_id == commit_id)
        foundCommit = conn.execute(stmt).first()
        if foundCommit == None:
            return None
        return foundCommit._asdict()

def createNewCommit(proj_id, email, last_commit):
    commit_id = createID()
    if last_commit != None:
        last_commit_items = getAllCommitItems(last_commit)
        for item in last_commit_items:
            createItemCommitLocation(item["item_id"], commit_id, item["name"], item["parent_folder"], item["is_folder"])
        root_folder_id = getCommitInfo(commit_id)["root_folder"]
    else:
        root_folder_id = createNewFolder('root', 0, pid, commit_id)
    with engine.connect() as conn:
        stmt = insert(models.Commit).values(
                proj_id = proj_id,
                commit_id = commit_id,
                author_email = email,
                root_folder = root_folder_id
        )
        conn.execute(stmt)
        conn.commit()
    return commit_id

def addSnapshotToCommit(snapshot_id, doc_id, commit_id):
    with engine.connect() as conn:
        snap = getCommitDocumentSnapshot(doc_id, commit_id)
        if snap == -1:
            stmt = insert(models.CommitDocumentSnapshotRelation).values(
                    snapshot_id = snapshot_id,
                    commit_id = commit_id,
                    doc_id = doc_id
            )
        else:
            stmt = update(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.doc_id == doc_id,
                    models.CommitDocumentSnapshotRelation.commit_id == commit_id).values(
                    snapshot_id = snapshot_id
            )
        conn.execute(stmt)
        conn.commit()
    return True

def commitACommit(commit_id):
    with engine.connect() as conn:
        stmt = (update(models.Commit)
        .where(models.Commit.commit_id == commit_id)
        .values(is_resolved=True)
        )
        conn.execute(stmt)
        conn.commit()
    return True

def deleteCommit(commit_id):
    with engine.connect() as conn:
        stmt = delete(models.ItemCommitLocation).where(
                models.ItemCommitLocation.commit_id == commit_id
        )
        conn.execute(stmt)
        stmt = select(models.Snapshot).where(
                models.Snapshot.og_commit_id == commit_id)
        snaps = conn.execute(stmt)
        for snap in snaps:
            deleteSnapshotUtil(snap.snapshot_id)
        conn.commit()

def removeItemFromCommit(item_id, commit_id):
    with engine.connect() as conn:
        stmt = delete(models.ItemCommitLocation).where(
                models.ItemCommitLocation.item_id == item_id).where(
                models.ItemCommitLocation.commit_id == commit_id
        )
        conn.execute(stmt)
        conn.commit()
    return True

def getAllCommitItems(commit_id):
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(
                models.ItemCommitLocation.commit_id == commit_id
        )
        results = conn.execute(stmt)
        itemArray = []
        for row in results:
            itemArray.append(row._asdict())
        return itemArray

def getCommitTree(commit_id):
    root_folder = getCommitInfo(commit_id)["root_folder"]
    return getFolderTree(root_folder, commit_id)
    
