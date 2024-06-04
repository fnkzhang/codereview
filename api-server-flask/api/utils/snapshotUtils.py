from cloudSql import *
from utils.commentUtils import *
from utils.buckets import *
from utils.miscUtils import *
from utils.commitDocSnapUtils import *
from utils.seenUtils import *
import models


def getSnapshotInfo(snapshot_id):
    '''
    **Explanation:**
        Gets a snapshot's information
    **Args:**
        -snapshot_id (int): id of the snapshot

    **Returns:**
        -snapshot (dict): A Snapshot object as a dict
    '''
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
        snapshot = conn.execute(stmt).first()
        if snapshot == None:
            return None
        return snapshot._asdict()

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, data, commit_id, user_email):
    '''
    **Explanation:**
        Creates a new snapshot attatched to a document on a commit
    **Args:**
        -proj_id (int): id of the project this is for
        -doc_id (int): id of the document the snapshot is for
        -data (int): content of the snapshot
        -commit_id (int): commit this is happening on 
        -user_email (str): Email of the user
    **Returns:**
        -snapshot_id (int): id of the newly created document
    '''
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
        createCommitDocumentSnapshot(doc_id, commit_id, snapshot_id)
        stmt = select(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.snapshot_id == snap)
        result = conn.execute(stmt).first()

        setSnapAsUnseenForAllProjUsersOtherThanMaker(snapshot_id, user_email, proj_id)
        if result == None and snap != None:
            deleteSnapshotUtil(snap)
        return snapshot_id

def getSnapshotProject(snapshot_id):
    '''
    **Explanation:**
        Gets a snapshot's project's id
    **Args:**
        -snapshot_id (int): id of the snapshot

    **Returns:**
        -proj_id (int): The id of the project the snapshot belongs to
    '''
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

def getSnapshotContentUtil(snapshot_id):
    '''
    **Explanation:**
        Gets a snapshot's contents
    **Args:**
        -snapshot_id (int): id of the snapshot

    **Returns:**
        -blob (bytes): The contents of the snapshot
    '''
    blob = fetchFromCloudStorage(str(snapshot_id))
    return blob

def deleteSnapshotUtil(snapshot_id):
    '''
    **Explanation:**
        Deletes a snapshot from the database and buckets entirely. This also deletes associated comments.
    **Args:**
        -snapshot_id (int): id of the snapshot to delete
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
    try:
        with engine.connect() as conn:
            deleteBlob(str(snapshot_id))
            stmt = delete(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            conn.execute(stmt)
            stmt = select(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
            comms = conn.execute(stmt)
            threads = []
            for comm in comms:
                thread = threading.Thread(target=purgeComment, kwargs={"comment_id":comm.comment_id})
                thread.start()
                threads.append(thread)
            stmt = delete(models.CommitDocumentSnapshotRelation).where(
                models.CommitDocumentSnapshotRelation.snapshot_id == snapshot_id
            )
            conn.execute(stmt)
            conn.commit()
            setSnapAsSeenForAllUsers(snapshot_id)
        for thread in threads:
            thread.join()
        return True, "No Error"
    except Exception as e:
        print(e)
        return False, e
