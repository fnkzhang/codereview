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

def getAllCommitDocumentSnapshotRelation(commit_id):
    with engine.connect() as conn:
        stmt = select(models.CommitDocumentSnapshotRelation).where(models.CommitDocumentSnapshotRelation.commit_id == commit_id)
        foundRelations = conn.execute(stmt)
        relations = {}
        for relation in foundRelations:
            relations[relation.doc_id] = relation.snapshot_id
        return relations

