from cloudSql import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *
from utils.miscUtils import *
import models

def getFolderInfo(folder_id, commit_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.folder_id == folder_id)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        commit_data = getItemCommitLocation(folder_id, commit_id)
        foundFolder = foundFolder._asdict()
        foundFolder["parent_folder"] = commit_data["parent_folder"]
        foundFolder["name"] = commit_data["name"]
        return foundFolder

def getFolderInfoViaLocation(name, parent_folder, commit_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.name == name, models.Folder.parent_folder == parent_folder)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        foundFolder = foundFolder._asdict()
        commit_data = getItemCommitLocation(foundFolder["folder_id"], commit_id)
        foundFolder["parent_folder"] = commit_data["parent_folder"]
        foundFolder["name"] = commit_data["name"]
        return foundFolder._asdict()

def getFolderPath(folder_id, commit_id):
    folder = getFolderInfo(folder_id, commit_id)
    if folder["parent_folder"] == 0:
        return ""
    else:
        return getFolderPath(folder["parent_folder"]) + folder["name"] + '/'

def createNewFolder(folder_name, parent_folder, proj_id, commit_id):
    folder_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Folder).values(
            folder_id = folder_id,
            associated_proj_id = proj_id
        )
        conn.execute(stmt)
        conn.commit()
    createItemCommitLocation(folder_id, commit_id, folder_name, parent_folder, True)
    return folder_id

def deleteFolderFromCommit(folder_id, commit_id):
    contents = getAllFolderContents(folder_id, commit_id)
    for doc in contents["documents"]:
        deleteDocumentFromCommit(doc["doc_id"], commit_id)
    for folder in contents["folders"]:
        deleteFolderFromCommit(doc["folder_id"], commit_id)

    with engine.connect() as conn:
        stmt = delete(models.ItemCommitLocation).where(models.ItemCommitLocation.item_id == folder_id, models.ItemCommitLocation.commit_id == commit_id)
        conn.execute(stmt)
        conn.commit()
    return True

#only use when deleting project
def purgeFolderUtil(folder_id):
    try:
        with engine.connect() as conn:

            stmt = delete(models.Folder).where(models.Folder.folder_id == folder_id)
            conn.execute(stmt)

            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def getAllFolderContents(folder_id, commit_id):
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(models.ItemCommitLocation.parent_folder == folder_id, models.ItemCommitLocation.commit_id == commit_id)
        foundItems = conn.execute(stmt)
        folders = []
        arrayOfDocuments = []
        for item in foundItems:
            if item.is_folder == True:
                folders.append(getFolderInfo(item.item_id))
            else:
                arrayOfDocuments.append(getDocumentInfo(item.item_id))
        return {"folders": folders, "documents":arrayOfDocuments}

def getFolderTree(folder_id, commit_id):
    root = getFolderInfo(folder_id)
    contents = getAllFolderContents(folder_id, commit_id)
    folders = []
    documents = []
    for document in contents["documents"]:
        documents.append(document)
    for folder in contents["folders"]:
        foldertree = getFolderTree(folder["folder_id"], commit_id)
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

