from cloudSql import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import * 
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *
from utils.miscUtils import *
from utils.seenUtils import *
from sqlalchemy.sql import func
import models
from reviewStateEnums import reviewStateEnum

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
        print(last_commit)
        last_commit_items = getAllCommitItems(last_commit)
        for item in last_commit_items:
            createItemCommitLocation(item["item_id"], commit_id, item["name"], item["parent_folder"], item["is_folder"])
        last_commit_docsnap = getAllCommitDocumentSnapshotRelation(last_commit)
        for docsnap in last_commit_docsnap:
            createCommitDocumentSnapshot(docsnap, commit_id, last_commit_docsnap[docsnap])
        root_folder_id = getCommitInfo(last_commit)["root_folder"]
    else:
        root_folder_id = createNewFolder('root', 0, proj_id, commit_id)
    with engine.connect() as conn:
        stmt = insert(models.Commit).values(
                proj_id = proj_id,
                commit_id = commit_id,
                author_email = email,
                root_folder = root_folder_id,
                last_commit = last_commit,
                name = "User Working Commit",
                state = reviewStateEnum.open, # Set opened because first commit
                is_approved = False,
                approved_count = 0,
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
                    models.CommitDocumentSnapshotRelation.snapshot_id == snap)
            result = conn.execute(stmt).first()
            if result == None:
                deleteSnapshotUtil(snap)
        conn.execute(stmt)
        conn.commit()
    return True

def commitACommit(commit_id, name):

    with engine.connect() as conn:
        getCommit = select(models.Commit).where(
            models.Commit.commit_id == commit_id
        )
        commitData = conn.execute(getCommit).first()._asdict()

        print(commitData["last_commit"])

        stmt = update(models.Commit).where(
                models.Commit.commit_id == commit_id).values(
                date_committed = func.now(),
                name = name,
        )


        # Close Old Commit
        closeCommitStmt = update(models.Commit).where(
            models.Commit.commit_id == commitData["last_commit"]
        ).values (
            state = reviewStateEnum.closed
        )

        conn.execute(stmt)
        conn.execute(closeCommitStmt)
        conn.commit()
    return True

def deleteCommit(commit_id):

    try:
        with engine.connect() as conn:
            print("start commit deletion", commit_id)
            stmt = delete(models.ItemCommitLocation).where(
                    models.ItemCommitLocation.commit_id == commit_id
            )
            print("delete location")
            conn.execute(stmt)
            threads = []
            stmt = select(models.Document).where(
                    models.Document.og_commit_id == commit_id)
            docs = conn.execute(stmt)
            for doc in docs:
                thread = threading.Thread(target=purgeDocumentUtil, kwargs={'doc_id':doc.doc_id})
                thread.start()
                threads.append(thread)
            stmt = select(models.Snapshot).where(
                    models.Snapshot.og_commit_id == commit_id)
            snaps = conn.execute(stmt)
            for snap in snaps:
                print("start snapdelete in commit", snap.snapshot_id)
                thread = threading.Thread(target=deleteSnapshotUtil, kwargs={'snapshot_id':snap.snapshot_id})
                thread.start()
                threads.append(thread)
            stmt = select(models.Folder).where(
                    models.Folder.og_commit_id == commit_id)
            folds = conn.execute(stmt)
            for fold in folds:
                purgeFolderUtil(fold.folder_id)
            print("folderdead")
            stmt = delete(models.Commit).where(
                    models.Commit.commit_id == commit_id
            )
            snaps = conn.execute(stmt)
            for thread in threads:
                thread.join()
            conn.commit()
        with engine.connect() as conn:
            stmt = delete(models.CommitDocumentSnapshotRelation).where(
                models.CommitDocumentSnapshotRelation.commit_id == commit_id)
            conn.execute(stmt)
            conn.commit()
        return True, None
    except Exception as e:
        print("commit", e)
        return False, e

def setCommitOpen(commit_id):

    try:

        with engine.connect() as conn:
            stmt = update(models.Commit).where(
                models.Commit.commit_id == commit_id).values(
                state = reviewStateEnum.open
            )

            conn.execute(stmt)
            conn.commit()
            return True
    except Exception as e:
        print("Error: ", e)
        return False

def setCommitClosed(commit_id):

    try:

        with engine.connect() as conn:
            stmt = update(models.Commit).where(
                models.Commit.commit_id == commit_id).values(
                state = reviewStateEnum.closed
            )

            conn.execute(stmt)
            conn.commit()
            return True
    except Exception as e:
        print("Error: ", e)
        return False

def setCommitReviewed(commit_id):

    try:

        with engine.connect() as conn:
            stmt = update(models.Commit).where(
                models.Commit.commit_id == commit_id).values(
                state = reviewStateEnum.reviewed
            )

            conn.execute(stmt)
            conn.commit()
            return True
    except Exception as e:
        print("Error: ", e)
        return False

def setCommitApproved(commit_id):

    try:
        with engine.connect() as conn:
            stmt = update(models.Commit).where(
                models.Commit.commit_id == commit_id).values(
                is_approved = True,
                state = reviewStateEnum.approved,
                approved_count = models.Commit.approved_count + 1,
            )

            conn.execute(stmt)
            conn.commit()
            return True
    except Exception as e:
        print("Error: ", e)
        return False


def getAllCommitItemsOfType(commit_id, is_folder):
    items = getAllCommitItems(commit_id)
    rv = []
    threads = []
    for item in items:
        if item["is_folder"] == is_folder:
            thread = threading.Thread(target=appendInfo, kwargs={"rv":rv, "item":item, "commit_id":commit_id, "is_folder":is_folder})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return rv
def appendInfo(rv, item, commit_id, is_folder):
    if is_folder == True:
        rv.append(getFolderInfo(item["item_id"], commit_id))
    else:
        rv.append(getDocumentInfo(item["item_id"], commit_id))
        
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
import time

def getCommitTreeWithAddons(commit_id, email):
    start = time.time()
    tree = getCommitTree(commit_id)
    treetime = time.time()
    docsnap = getAllCommitDocumentSnapshotRelation(commit_id)
    dstime = time.time()
    addToTree(tree, docsnap, email)
    combine = time.time()
    print("tree:", treetime-start, " dstime:", dstime-treetime, " combine:", combine-dstime)
    return tree

def addToTree(tree, docsnap, email):
    threads = []
    tree["seenSnapshot"] = True
    tree["seenComments"] = True
    with engine.connect() as conn:
        for item in tree["content"]["folders"]:
            thread = threading.Thread(target=addToTree, kwargs={'tree':item, 'docsnap':docsnap, 'email':email})
            thread.start()
            threads.append(thread)
            #addToTree(item, docsnap, email)
        for item in tree["content"]["documents"]:
            thread = threading.Thread(target=addSeenAndUnresolved, kwargs={'item':item, 'docsnap':docsnap, 'email':email, 'tree':tree})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return True

def addSeenAndUnresolved(item, docsnap, email, tree):
    with engine.connect() as conn:
        item["seenSnapshot"] = isSnapshotSeenByUser(docsnap[item["doc_id"]], email)
        item["seenComments"] = isSnapshotAllCommentSeenByUser(docsnap[item["doc_id"]], email)
        if item["seenSnapshot"] == False:
            tree["seenSnapshot"] = False
        if item["seenComments"] == False:
            tree["seenComments"] = False
        stmt = select(models.Comment).where(
                models.Comment.snapshot_id == docsnap[item["doc_id"]],
                models.Comment.is_resolved == False
                )
        count = conn.execute(stmt).rowcount
        item["unresolvedCommentCount"] = count
    return True

def getCommitFoldersAsPaths(commit_id):
    project = getCommitInfo(commit_id)
    folders = getAllCommitItemsOfType(commit_id, True)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath
