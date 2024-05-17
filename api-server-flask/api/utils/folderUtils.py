from cloudSql import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *

from utils.miscUtils import *
import models

def getFolderInfo(folder_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.folder_id == folder_id)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        return foundFolder._asdict()

def getFolderInfoViaLocation(name, parent_folder):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.name == name, models.Folder.parent_folder == parent_folder)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        return foundFolder._asdict()

def getFolderPath(folder_id):
    folder = getFolderInfo(folder_id)
    if folder["parent_folder"] == 0:
        return ""
    else:
        return getFolderPath(folder["parent_folder"]) + folder["name"] + '/'

def createNewFolder(folder_name, parent_folder, proj_id):
    folder_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Folder).values(
            folder_id = folder_id,
            name = folder_name,
            parent_folder = parent_folder,
            associated_proj_id = proj_id
        )
        conn.execute(stmt)
        conn.commit()
    return folder_id

def deleteFolderUtil(folder_id):
    try:
        with engine.connect() as conn:

            stmt = select(models.Document).where(models.Document.parent_folder == folder_id)
            documents = conn.execute(stmt)
            for document in documents:
                deleteDocumentUtil(document.doc_id)

            stmt = select(models.Folder).where(models.Folder.parent_folder ==folder_id)
            folders = conn.execute(stmt)
            for folder in folders:
                deleteFolderUtil(folder.folder_id)
            stmt = delete(models.Folder).where(models.Folder.folder_id == folder_id)
            conn.execute(stmt)

            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def renameFolderUtil(folder_id, folder_name):
    try:
        with engine.connect() as conn:
            stmt = (update(models.Folder)
                .where(models.Folder.folder_id == folder_id)
                .values(name=folder_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def moveFolderUtil(folder_id, parent_folder):
    with engine.connect() as conn:
        stmt = (update(models.Folder)
        .where(models.Folder.folder_id == folder_id)
        .values(parent_folder = parent_folder)
        )
        conn.execute(stmt)
        conn.commit()
    return parent_folder

def getAllFolderContents(folder_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.parent_folder == folder_id)
        foundFolders = conn.execute(stmt)
        folders = []
        for folder in foundFolders:
            folders.append(folder._asdict())
        stmt = select(models.Document).where(models.Document.parent_folder == folder_id)

        results = conn.execute(stmt)

        arrayOfDocuments = []

        for row in results:
            arrayOfDocuments.append(row._asdict())

        return {"folders": folders, "documents":arrayOfDocuments}

def getFolderTree(folder_id):
    root = getFolderInfo(folder_id)
    contents = getAllFolderContents(folder_id)
    folders = []
    documents = []
    for document in contents["documents"]:
        documents.append(document)
    for folder in contents["folders"]:
        foldertree = getFolderTree(folder["folder_id"])
        folders.append(foldertree)
    content = { "folders":folders, "documents":documents}
    root["content"] = content
    return root

#i don't want to have to query the database for every folder, money moment
#terrible optimization but whatevertbh
def getFolderPathsFromList(folder_id, current_path,list_of_folders):
    folderIDToPath = {}
    foldersInFolder = []
    for folder in list_of_folders:
        if folder["parent_folder"] == folder_id:
            list_of_folders.remove(folder)
            foldersInFolder.append(folder)
    for folder in foldersInFolder:
        folderpath = current_path + folder["name"] + '/'
        folderIDToPath[folder["folder_id"]] = folderpath
        folderIDToPath.update(getFolderPathsFromList(folder["folder_id"], folderpath, list_of_folders))
    return folderIDToPath

