from cloudSql import *

from utils.miscUtils import *
import models


def getCommitDocumentSnapshot(doc_id, commit_id):
    with engine.connect() as conn:
        stmt = select(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.commit_id == commit_id, models.CommitDocumentSnapshotRelation.doc_id == doc_id)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        relation = result.first()
        if relation == None:
            return None
        return relation.snapshot_id

def createCommitDocumentSnapshot(doc_id, commit_id, snapshot_id):
    with engine.connect() as conn:
        print("SNAPSHOT_ID!!!", snapshot_id, doc_id)
        snap = getCommitDocumentSnapshot(doc_id, commit_id)
        print("OLDSNAPSHOT_ID!!!", snap)
        if snap == None:
            print("doesn't?")
            stmt = insert(models.CommitDocumentSnapshotRelation).values(
                    snapshot_id = snapshot_id,
                    commit_id = commit_id,
                    doc_id = doc_id
            )
        else:
            print("existss")
            stmt = update(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.doc_id == doc_id,
                    models.CommitDocumentSnapshotRelation.commit_id == commit_id).values(
                    snapshot_id = snapshot_id
            )
            stmt = conn.execute(stmt)
            stmt = select(models.CommitDocumentSnapshotRelation).where(
                    models.CommitDocumentSnapshotRelation.snapshot_id == snap)
            result = conn.execute(stmt).first()
            if result == None:
                deleteSnapshotUtil(snap)
        conn.execute(stmt)
        conn.commit()
    return True
def getAllCommitDocumentSnapshotRelation(commit_id):
    with engine.connect() as conn:
        stmt = select(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.commit_id == commit_id)
        foundRelations = conn.execute(stmt)
        relations = {}
        for relation in foundRelations:
            relations[relation.doc_id] = relation.snapshot_id
        return relations
