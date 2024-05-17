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
    with engine.connect() as conn:
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = owner,
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
    createNewCommit(pid, email)
    return pid

def purgeProjectUtil(proj_id):
    try:
        with engine.connect() as conn:
            commits = getAllProjectCommits(proj_id)
            for commit in commit:
                deleteCommit(commit["commit_id"])
            docs = getAllProjectDocuments(proj_id)
            for doc in docs:
                purgeDocumentUtil(doc["doc_id"])
            folders = getAllProjectFolders(proj_id)
            for folder in folders:
                purgeFolderUtil(folder["folder_id"])
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
##work on this later for github
def getProjectFoldersAsPaths(proj_id):
    project = getProjectInfo(proj_id)
    folders = getAllProjectFolders(proj_id)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath

# Returns Array of Dictionaries
def getAllProjectCommits(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id).order_by(models.Commit.date_created.asc())
        foundCommits = conn.execute(stmt)

        listOfCommits = []

        for row in foundCommits:
            listOfCommits.append(row._asdict())

        return listOfCommits

# Returns Array of Dictionaries
def getAllCommittedProjectCommitsInOrder(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.date_committed != None).order_by(models.Commit.date_committed.asc())
        foundCommits = conn.execute(stmt)

        listOfCommits = []

        for row in foundCommits:
            listOfCommits.append(row._asdict())

        return listOfCommits

def getProjectLastCommittedCommit(proj_id):
    try:
        return getAllCommittedProjectCommitsInOrder(proj_id)[-1]
    except:
        return None

def getUserWorkingCommitInProject(proj_id, email):
    with engine.connect() as conn:
        stmt = select(models.Commit).where(models.Commit.proj_id == proj_id, models.Commit.date_committed == None)
        commit = conn.execute(stmt).first()
        if commit == None:
            return None
        return commit._asdict()

