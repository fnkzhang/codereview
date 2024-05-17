from cloudSql import *

from utils.miscUtils import *
import models

def getItemCommitLocation(item_id, commit_id):
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(models.ItemCommitFolder.commit_id == commit_id, models.ItemCommitFolder.item_id == item_id)
        result = conn.execute(stmt)
        relation = result.first()
        if relation == None:
            return None
        return relation._asdict()

def createItemCommitLocation(item_id, commit_id, name, parent_folder, is_folder):
    with engine.connect() as conn:
        if getItemCommitLocation(item_id, commit_id) == None:
            stmt = insert(models.ItemCommitLocation).values(
                    item_id = item_id,
                    commit_id = commit_id,
                    parent_folder = parent_folder,
                    name = name,
                    is_folder = is_folder
            )
        else:
            stmt = update(models.ItemCommitLocation).where(
                    models.ItemCommitLocation.item_id == item_id,
                    models.ItemCommitLocation.commit_id == commit_id).values(
                    parent_folder = parent_folder,
                    name = name
            )
        conn.execute(stmt)
        conn.commit()
    return True

def renameItem(item_id, item_name, commit_id):
    try:
        with engine.connect() as conn:
            stmt = (update(models.ItemCommitLocation)
                .where(models.ItemCommitLocation.item_id == item_id)
                .where(models.ItemCommitLocation.commit_id == commit_id)
                .values(name=item_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def moveItem(item_id, parent_folder, commit_id):
    try:
        with engine.connect() as conn:
            stmt = (update(models.ItemCommitLocation)
                .where(models.ItemCommitLocation.item_id == item_id)
                .where(models.ItemCommitLocation.commit_id == commit_id)
                .values(parent_folder=parent_folder)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e


