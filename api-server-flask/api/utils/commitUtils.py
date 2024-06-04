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
    '''
    **Explanation:**
        Returns a Commit object as a dict

    **Args:**
        -commit_id (int): id of the commit

    **Returns:**
        -commit (dict): Commit as a dict
    '''
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.commit_id == commit_id)
        foundCommit = conn.execute(stmt).first()
        if foundCommit == None:
            return None
        return foundCommit._asdict()

def createNewCommit(proj_id, email, last_commit):
    '''
    **Explanation:**
        Creates a new working commit for the given user
    **Args:**
        -proj_id (int): id of the project this is for
        -email (str): Email of the user
        -last_commit (int or None): id of the commit the new commit will be based off of
    **Returns:**
        -commit_id (int): id of the newly created commit
    '''
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
    '''
    **Explanation:**
        Creates a new working commit for the given user
    **Args:**
        -proj_id (int): id of the project this is for
        -email (str): Email of the user
        -last_commit (int or None): id of the commit the new commit will be based off of
    **Returns:**
        -commit_id (int): id of the newly created commit
    '''
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
    '''
    **Explanation:**
        Commits a working commit
    **Args:**
        -commit_id (int): id of the working commit
        -name (str): New name for the commit
    **Returns:**
        -True
    '''
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
    '''
    **Explanation:**
        Deletes a commit. This should generally be only used for working commits, and using it on committed commits could cause undefined behavior if other commits in the project will still exist after
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
    try:
        with engine.connect() as conn:
            stmt = delete(models.ItemCommitLocation).where(
                    models.ItemCommitLocation.commit_id == commit_id
            )
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
                thread = threading.Thread(target=deleteSnapshotUtil, kwargs={'snapshot_id':snap.snapshot_id})
                thread.start()
                threads.append(thread)
            stmt = select(models.Folder).where(
                    models.Folder.og_commit_id == commit_id)
            folds = conn.execute(stmt)
            for fold in folds:
                purgeFolderUtil(fold.folder_id)
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
    '''
    **Explanation:**
        Sets a commit's state to open
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
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
    '''
    **Explanation:**
        Sets a commit's state to closed
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
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
    '''
    **Explanation:**
        Sets a commit's state to reviewed
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
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
    '''
    **Explanation:**
        Sets a commit's state to approved
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
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
    '''
    **Explanation:**
        Gets all items from the commit that are either documents or folders, determined by the argument "is_folder"
    **Args:**
        -commit_id (int): id of the commit
        -is_folder (int): Whether or not the items returned are folders or documents (True for folder, False for document)
    **Returns:**
        -itemlist (list): list of the items of the commit that match the condition as dicts
    '''
    items = getAllCommitItems(commit_id)
    rv = []
    threads = []
    for item in items:
        if item["is_folder"] == is_folder:
            thread = threading.Thread(target=addItemInfoToList, kwargs={"rv":rv, "item":item, "commit_id":commit_id, "is_folder":is_folder})
            thread.start()
            threads.append(thread)
    for thread in threads:
        thread.join()
    return rv
def addItemInfoToList(rv, item, commit_id, is_folder):
    '''
    **Explanation:**
        Adds an item to list, getting the relevant folder/document information
    **Args:**
        -rv (list): the list to add the item to
        -commit_id (int): id of the commit
        -is_folder (int): Whether or not the item is a folder or document (True for folder, False for document)
    '''
    if is_folder == True:
        rv.append(getFolderInfo(item["item_id"], commit_id))
    else:
        rv.append(getDocumentInfo(item["item_id"], commit_id))
        
def getAllCommitItems(commit_id):
    '''
    **Explanation:**
        Gets all items from a commit
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -itemlist (list): list of the items of the commit
    '''
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
    '''
    **Explanation:**
        Gets all items from the commit in a tree structure
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        - tree (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. The folders also have the "contents" key added, which map to their own contents. 
    '''
    root_folder = getCommitInfo(commit_id)["root_folder"]
    return getFolderTree(root_folder, commit_id)

def getCommitTreeWithAddons(commit_id, email):
    '''
    **Explanation:**
        Gets all items from the commit in a tree structure with along with whether or not there are newly seen snapshots/comments in the folder/document
    **Args:**
        -commit_id (int): id of the commit
        -email (str): email of the user for the seen values
    **Returns:**
        - tree (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. Both item dicts have the "seenSnapshots" and "seenComments" key added, which represent whether or not the user has seen all snapshots/comments for that document. The folders also have the "contents" key added, which map to their own contents. 
    '''
    tree = getCommitTree(commit_id)
    docsnap = getAllCommitDocumentSnapshotRelation(commit_id)
    addToTree(tree, docsnap, email)
    return tree

def addToTree(tree, docsnap, email):
    '''
    **Explanation:**
        Adds the seenSnapshot and seenComment values to a folder and its contents, and recurses for any child folders
    **Args:**
        -tree (dict): A tree like the one returned in getCommitTree
        -docsnap (dict): A dict with document ids as keys, which map to the snapshots related to them in a commit
        -email (str): email of the user for the seen values
    **Returns:**
        - tree (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. Both item dicts have the "seenSnapshots" and "seenComments" key added, which represent whether or not the user has seen all snapshots/comments for that document. The folders also have the "contents" key added, which map to their own contents. 
    '''
    threads = []
    tree["seenSnapshot"] = True
    tree["seenComments"] = True
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
    '''
    **Explanation:**
        Adds the seenSnapshot and seenComment values to an item and its parent folder
    **Args:**
        -item (dict): Dict of the item, located in the tree variable's ["content"]["documents]
        -docsnap (dict): A dict with document ids as keys, which map to the snapshots related to them in a commit
        -email (str): email of the user for the seen values
        -tree (dict): A tree like the one returned in getCommitTree. Top level represents the parent folder of the document

    **Returns:**
        -True
    '''
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
    '''
    **Explanation:**
        Gets all of the folders in the commit as paths; e.g: if folder2 is in folder1, which is in the root folder of the commit, the path would be folder1/folder2/
    **Args:**
        -commit_id (int): id of the commit

    **Returns:**
        -folderIDToPath (dict): dict with folder ids mapping to their paths
    '''
    project = getCommitInfo(commit_id)
    folders = getAllCommitItemsOfType(commit_id, True)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath
