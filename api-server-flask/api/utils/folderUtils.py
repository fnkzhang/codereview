from cloudSql import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *
from utils.miscUtils import *
import models

def getFolderInfo(folder_id, commit_id):
    '''
    **Explanation:**
        Gets a folder's information from a specific commit
    **Args:**
        -folder_id (int): id of the folder
        -commit_id (int): id of the commit

    **Returns:**
        -folder (dict): A Folder object as a dict with ItemCommitLocation object "parent_folder" and "name" fields added
    '''
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
    '''
    **Explanation:**
        Gets a folder's information from a specific commit using the name and parent folder instead of id
    **Args:**
        -name (str): name of the folder
        -parent_folder (int): id of the folder's parent folder
        -commit_id (int): id of the commit

    **Returns:**
        -folder (dict): A Folder object as a dict with ItemCommitLocation object "parent_folder" and "name" fields added
    '''
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(models.ItemCommitLocation.name == name, models.ItemCommitLocation.parent_folder == parent_folder, models.ItemCommitLocation.is_folder == True)

        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        foundFolder = foundFolder._asdict()
        folder = getFolderInfo(foundFolder["item_id"], commit_id)
        return folder

def getFolderPath(folder_id, commit_id):
    '''
    **Explanation:**
        Gets the given folder's path in the commit as a string; e.g: Folder2 resides in Folder1, which resides in the roote folder would be Folder1/Folder2/
    **Args:**
        -folder_id (folder): id of the folder
        -commit_id (int): id of the commit

    **Returns:**
        -folderPath (str): The folder's path as a string
    '''
    folder = getFolderInfo(folder_id, commit_id)
    if folder["parent_folder"] == 0:
        return ""
    else:
        return getFolderPath(folder["parent_folder"], commit_id) + folder["name"] + '/'

def createNewFolder(folder_name, parent_folder, proj_id, commit_id):
    '''
    **Explanation:**
        Creates a new folder for a commit in a project
    **Args:**
        -folder_name (int): name of the folder
        -parent_folder (int): id of the folder's parent folder
        -proj_id (int): id of the project this is for
        -commit_id (int): commit this is happening on 
    **Returns:**
        -folder_id (int): id of the newly created folder
    '''
    folder_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Folder).values(
            folder_id = folder_id,
            associated_proj_id = proj_id,
            og_commit_id = commit_id
        )
        conn.execute(stmt)
        conn.commit()
    createItemCommitLocation(folder_id, commit_id, folder_name, parent_folder, True)
    return folder_id

def deleteFolderFromCommit(folder_id, commit_id):
    '''
    **Explanation:**
        Deletes a folder from a commit. The folder will persist in other existing commits. Will also recursively delete all folder contents
    **Args:**
        -folder_id (int): id of the folder to delete
        -commit_id (int): id of the commit to delete from
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
    try:
        contents = getAllFolderContents(folder_id, commit_id)
        for doc in contents["documents"]:
            deleteDocumentFromCommit(doc["doc_id"], commit_id)
        for folder in contents["folders"]:
            deleteFolderFromCommit(folder["folder_id"], commit_id)

        with engine.connect() as conn:
            stmt = delete(models.ItemCommitLocation).where(models.ItemCommitLocation.item_id == folder_id, models.ItemCommitLocation.commit_id == commit_id)
            conn.execute(stmt)
            conn.commit()
        return True, None
    except Exception as e:
        return False, e

#only use when deleting project
def purgeFolderUtil(folder_id):
    '''
    **Explanation:**
        Deletes a folder from the database entirely.
    **Args:**
        -folder_id (int): id of the folder to delete
    **Returns:**
        -success (bool): success
        -error message (str): if there was an error, returns the message, if not, returns None
    '''
    try:
        with engine.connect() as conn:

            stmt = delete(models.Folder).where(models.Folder.folder_id == folder_id)
            conn.execute(stmt)

            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def getAllFolderContents(folder_id, commit_id):
    '''
    **Explanation:**
        Gets all contents of a folder in a commit
    **Args:**
        -folder_id (int): id of the folder
        -commit_id (int): id of the commit
    **Returns:**
        -contents (dict): A dict with 2 keys of "folders" and "documents", which map to lists of the respective items that are in the folder given
    '''
    threads = []
    with engine.connect() as conn:
        stmt = select(models.ItemCommitLocation).where(models.ItemCommitLocation.parent_folder == folder_id, models.ItemCommitLocation.commit_id == commit_id)
        foundItems = conn.execute(stmt)
        folders = []
        arrayOfDocuments = []
        for item in foundItems:
            thread = threading.Thread(target=addItemToCorrectTypeList, kwargs={'item':item, 'folders':folders, "arrayOfDocuments":arrayOfDocuments, "commit_id":commit_id})
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        return {"folders": folders, "documents":arrayOfDocuments}


def addItemToCorrectTypeList(item, folders, arrayOfDocuments, commit_id):
    '''
    **Explanation:**
        Adds the given item to either the folders or arrayOfDocuments lists depending on its type
    **Args:**
        -item (dict): A dict representation of a ItemCommitLocation object
        -folders (list): a list to add folders to
        -arrayOfDocuments (list): a list to add documents to
        -commit_id (int): id of the commit
    **Returns:**
        -True
    '''
    if item.is_folder == True:
        folders.append(getFolderInfo(item.item_id, commit_id))
    else:
        arrayOfDocuments.append(getDocumentInfo(item.item_id, commit_id))
    return True

def getFolderTree(folder_id, commit_id):
    '''
    **Explanation:**
        Gets all contents of a folder in a tree structure
    **Args:**
        -folder_id (int): id of the folder
        -commit_id (int): id of the commit this is happening in
    **Returns:**
        - tree (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. The folders also have the "contents" key added, which map to their own contents. 
    '''
    root = getFolderInfo(folder_id, commit_id)
    contents = getAllFolderContents(folder_id, commit_id)
    folders = []
    documents = []
    threads = []
    for folder in contents["folders"]:
        thread = threading.Thread(target=appendFolderTreeToList, kwargs={"folderlist":folders, "folder_id":folder["folder_id"], "commit_id": commit_id})
        thread.start()
        threads.append(thread)
        #foldertree = getFolderTree(folder["folder_id"], commit_id)
        #folders.append(foldertree)
    for document in contents["documents"]:
        documents.append(document)
    content = { "folders":folders, "documents":documents}
    root["content"] = content
    for thread in threads:
        thread.join()
    return root

def appendFolderTreeToList(folderlist, folder_id, commit_id):
    '''
    **Explanation:**
        Gets the folder tree of the folder given and appends it to the given list
    **Args:**
        -folderlist (list): list to append the tree to
        -folder_id (int): id of the folder to get the tree of
        -commit_id (int): id of the commit this takes place in
    **Returns:**
        - tree (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. The folders also have the "contents" key added, which map to their own contents. 
    '''
    foldertree = getFolderTree(folder_id, commit_id)
    folderlist.append(foldertree)

#i don't want to have to query the database for every folder, money moment
#terrible optimization but whatevertbh
def getFolderPathsFromList(folder_id, current_path, list_of_folders):
    '''
    **Explanation:**
        Gets all of the folders in the list as paths; e.g: if folder2 is in folder1, which is in the root folder of the commit, the path would be folder1/folder2/
    **Args:**
        -folder_id (int): id of the current folder in the list being added
        -current_path (str): current path of the folder
        -list_of_folders: a list of all the folders as a tree in the order of breadth first search

    **Returns:**
        -folderIDToPath (dict): dict with folder ids mapping to their path
    '''
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

