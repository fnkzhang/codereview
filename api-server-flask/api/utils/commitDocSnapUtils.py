from cloudSql import *

from utils.miscUtils import *
import models


def getCommitDocumentSnapshot(doc_id, commit_id):
    '''
    **Explanation:**
        Gets the snapshot id of a document in a commit
    **Args:**
        -doc_id (int): id of the document
        -commit_id (int): id of the commit
    **Returns:**
        -snapshot_id (int): id of the related snapshot
    '''
    with engine.connect() as conn:
        stmt = select(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.commit_id == commit_id, models.CommitDocumentSnapshotRelation.doc_id == doc_id)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        relation = result.first()
        if relation == None:
            return None
        return relation.snapshot_id

def createCommitDocumentSnapshot(doc_id, commit_id, snapshot_id):
    '''
    **Explanation:**
        Creates a relationship between a snapshot and a document on a given commit
    **Args:**
        -doc_id (int): id of the document
        -commit_id (int): id of the commit
        -snapshot_id (int): id of the snapshot
    **Returns:**
        -True
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
        conn.execute(stmt)
        conn.commit()
    return True

def getAllCommitDocumentSnapshotRelation(commit_id):
    '''
    **Explanation:**
        Gets all document snapshot relationships for a commit
    **Args:**
        -commit_id (int): id of the commit
    **Returns:**
        -relations (dict): A dict with document ids as the keys, which map to their related snapshots' id 
    '''
    with engine.connect() as conn:
        stmt = select(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.commit_id == commit_id)
        foundRelations = conn.execute(stmt)
        relations = {}
        for relation in foundRelations:
            relations[relation.doc_id] = relation.snapshot_id
        return relations
