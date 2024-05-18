from cloudSql import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import * 
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *
from utils.miscUtils import *
from sqlalchemy.sql import func
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
        root_folder_id = createNewFolder('root', 0, proj_id, commit_id)
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
        if snap == None:
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
            stmt = select(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.snap_id == snap)
            result = conn.execute(stmt).first()
            if result == None:
                deleteSnapshotUtil(snap)
        conn.execute(stmt)
        conn.commit()
    return True

def commitACommit(commit_id):
    with engine.connect() as conn:
        stmt = (update(models.Commit).where(
            models.Commit.commit_id == commit_id).values(
            date_committed == func.now())
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

        stmt = select(models.Document).where(
                models.Document.og_commit_id == commit_id)
        docs = conn.execute(stmt)
        for doc in docs:
            purgeDocumentUtil(doc.doc_id)

        stmt = select(models.Folder).where(
                models.Folder.og_commit_id == commit_id)
        folds = conn.execute(stmt)
        for fold in folds:
            purgeFolderUtil(fold.folder_id)

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

def getCommitSharedItemIdsUtil(commit_id1, commit_id2):
    commit1Items = getAllCommitItemIds(commit_id1)
    commit2Items = getAllCommitItemIds(commit_id2)
    sharedIds = []
    for itemId in commit1Items:
        if itemId in commit2Items:
            sharedIds.append(itemId)
    return sharedIds

def getCommitDiffSnapshotsUtil(commit_id1, commit_id2):
    shared = getCommitSharedItemIdsUtil(commit_id1, commit_id2)
    commit1snaps = {}
    commit2snaps = {}
    for itemId in shared:
        item = getItemCommitLocation(itemId, commit_id1)
        if item["is_folder"] == False:
            commit1snap = getCommitDocumentSnapshot(itemId, commit_id1)
            commit1snaps[commit1snap["doc_id"]] = commit1snap["snapshot_id"]
            commit2snap = getCommitDocumentSnapshot(itemId, commit_id2)
            commit2snaps[commit2snap["doc_id"]] = commit2snap["snapshot_id"]
    return commit1snaps, commit2snaps

def getCommitLocationDifferencesUtil(commit_id1, commit_id2):
    commit1Items = getAllCommitItemIds(commit_id1)
    commit2Items = getAllCommitItemIds(commit_id2)
    commit1Uniques = []
    commit2Uniques = []
    for itemId in commit1Items:
        if itemId not in commit2Items:
            item = getItemCommitLocation(itemId)
            if item["is_folder"] == True:
                commit1Uniques.append(getFolderInfo(item, commit_id1))
            else: 
                commit1Uniques.append(getDocumentInfo(item, commit_id1))
    for itemId in commit2Items:
        if itemId not in commit1Items:
            item = getItemCommitLocation(itemId)
            if item["is_folder"] == True:
                commit2Uniques.append(getFolderInfo(item, commit_id2))
            else:
                commit2Uniques.append(getDocumentInfo(item, commit_id2))
    return commit1Uniques, commit2Uniques

def getAllCommitItemIdsOfType(commit_id, is_folder):
    items = getAllCommitItems(commit_id)
    rv = []
    for item in items:
        if item["is_folder"] == is_folder:
            rv.append(item["item_id"])
    return rv

def getAllCommitItemsOfType(commit_id, is_folder):
    items = getAllCommitItems(commit_id)
    rv = []
    for item in items:
        if item["is_folder"] == is_folder:
            rv.append(getFolderInfo(item, commit_id))
        else:
            rv.append(getDocumentInfo(item, commit_id))
    return rv

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

def getAllCommitItemIds(commit_id):
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(
                models.ItemCommitLocation.commit_id == commit_id
        )
        results = conn.execute(stmt)
        itemArray = []
        for row in results:
            itemArray.append(row.item_id)
        return itemArray

def getCommitTree(commit_id):
    root_folder = getCommitInfo(commit_id)["root_folder"]
    return getFolderTree(root_folder, commit_id)

def getCommitFoldersAsPaths(commit_id):
    project = getCommitInfo(commit_id)
    folders = getAllCommitItemsOfType(commit_id, True)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath