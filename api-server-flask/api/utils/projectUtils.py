from cloudSql import *
from utils.folderUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import * 
from utils.miscUtils import *
import models

def getProjectInfo(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Project).where(models.Project.proj_id == proj_id)
        foundProject = conn.execute(stmt).first()
        if foundProject == None:
            return None
        return foundProject._asdict()

def createNewProject(proj_name, owner):
    pid = createID()
    root_folder_id = createNewFolder('root', 0, pid)
    with engine.connect() as conn:
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = owner,
                root_folder = root_folder_id
        )
        relationstmt = insert(models.UserProjectRelation).values(
                user_email = owner,
                proj_id = pid,
                role = "Owner",
                permissions = 5
        )
        conn.execute(projstmt)
        conn.execute(relationstmt)
        conn.commit()
    return pid

def deleteProjectUtil(proj_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Project).where(models.Project.proj_id == proj_id)
            project = conn.execute(stmt).first()
            deleteFolderUtil(project.root_folder)
            stmt = delete(models.Project).where(models.Project.proj_id == proj_id)
            conn.execute(stmt)
            stmt = delete(models.UserProjectRelation).where(models.UserProjectRelation.proj_id == proj_id)
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def renameProjectUtil(proj_id, proj_name):
    try:
        with engine.connect() as conn:
            stmt = (update(models.Project)
                .where(models.Project.proj_id == proj_id)
                .values(name=proj_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def getAllProjectDocuments(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.associated_proj_id == int(proj_id))

        results = conn.execute(stmt)

        arrayOfDocuments = []

        for row in results:
            arrayOfDocuments.append(row._asdict())

        return arrayOfDocuments


def getAllProjectFolders(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.associated_proj_id == proj_id)
        foundFolders = conn.execute(stmt)
        folders = []
        for folder in foundFolders:
            folders.append(folder._asdict())
        return folders

def getProjectFoldersAsPaths(proj_id):
    project = getProjectInfo(proj_id)
    folders = getAllProjectFolders(proj_id)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath


