
from flask import Flask, request, jsonify
from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, update, delete, DateTime, Text

from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from cloudSql import connectCloudSql

from github import Github, InputGitTreeElement
from github import Auth

import models

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

from cacheUtils import cloudStorageCache, publishTopicUpdate

engine = connectCloudSql()
Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html
with open('github_oath_credentials.json') as creds:
    creds = json.load(creds)
    github_client_id = creds["client-id"]
    github_client_secret = creds["client-secret"]

g = Github()
gapp = g.get_oauth_application(github_client_id, github_client_secret)

with open('github_oath_credentials.json') as creds:
    creds = json.load(creds)
    github_client_id = creds["client-id"]
    github_client_secret = creds["client-secret"]

g = Github()
gapp = g.get_oauth_application(github_client_id, github_client_secret)

def uploadBlob(blobName, item):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    print("Uploading to", blobName)
    blob = bucket.blob(blobName)
    blob.upload_from_string(data = item, content_type='application/json')
    
    return True

def getBlob(blobName):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.get_blob(blobName)
    return blob.download_as_text()

def deleteBlob(blobName):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.get_blob(blobName)
    blob.delete()
    return True

#location = basically the folder the files are located in
def deleteBlobsInDirectory(location):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blobs = bucket.list_blobs(prefix = location)
    for blob in blobs:
        blob.delete()
    return True

def getTime():
    return datetime.now()

def setUserProjPermissions(email, pid, r, perms):
    with engine.connect() as conn:
        stmt = insert(models.UserProjectRelation).values(
                user_email = email,
                proj_id = pid,
                role = r,
                permissions = perms
        )
        conn.execute(stmt)
        conn.commit()
    return True

# Find all project relationship models for user email
def getAllUserProjPermissions(user_email):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email)

        result = conn.execute(stmt)

        returnList = []
        for row in result:
            returnList.append(row._asdict())

        return returnList
def getUserInfo(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        user = result.first()
        if user == None:
            return None
        return user._asdict()

def getUserProjPermissions(user_email, proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email, models.UserProjectRelation.proj_id == proj_id)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        relation = result.first()
        if relation == None:
            return -1
        return relation.permissions

def getProjectInfo(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Project).where(models.Project.proj_id == proj_id)
        foundProject = conn.execute(stmt).first()
        if foundProject == None:
            return None
        return foundProject._asdict()

def getAllProjectDocuments(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.associated_proj_id == int(proj_id))

        results = conn.execute(stmt)

        arrayOfDocuments = []

        for row in results:
            arrayOfDocuments.append(row._asdict())
        
        return arrayOfDocuments

def getGithubProjectDocumentsAsPaths(repo, branch, token):
    g2 = Github(auth = Auth.Token(token))
    repo = g2.get_repo(repo)
    try:
        contents = repo.get_contents("", branch)
    except:
        return []
    githubfiles = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            print(file_content.path)
            githubfiles.append(file_content.path)
    return githubfiles

def getProjectNonexistentGithubDocumentsUtil(repo, branch, token, proj_id):
    allGithubFiles = set(getGithubProjectDocumentsAsPaths(repo, branch, token))
    projectDocuments = getAllProjectDocuments(proj_id)
    projectDocumentPaths = set([getDocumentPath(document['doc_id']) for document in projectDocuments])
    nonexistant = list(allGithubFiles - projectDocumentPaths)
    return nonexistant

def assembleGithubTreeElements(repo, folderIDToPath, deletedDocumentPaths, snapshotIDs):
    tree_elements = []
    for deletedDocumentPath in deletedDocumentPaths:
        tree_elements.append(InputGitTreeElement(path = deletedDocumentPath,
                mode = "100644",
                type = "blob",
                sha = None
            ))
    for snapshotID in snapshotIDs:
        snapshot = getSnapshotInfo(snapshotID)
        document = getDocumentInfo(snapshot["associated_document_id"])
        blob = repo.create_git_blob(
                content = getSnapshotContentUtil(snapshotID),
                encoding = 'utf-8',
                )
        tree_elements.append(InputGitTreeElement(path = folderIDToPath[document["parent_folder"]] + document["name"],
                mode = "100644",
                type = "blob",
                sha = blob.sha
            ))
    return tree_elements

def assembleGithubComments(snapshotIDs):
    githubComments = []
    for snapshotID in snapshotIDs:
        doc_id = getSnapshotInfo(snapshotID)["associated_document_id"]
        documentPath = getDocumentPath(doc_id)
        commentList = filterCommentsByPredicate(models.Comment.snapshot_id == snapshotID )
        for comment in commentList:
            if comment["is_resolved"] == False:
                githubComments.append("Comment From CodeReview\nComment Author:" + comment["author_email"] + "\nDocument:"+documentPath + '\nLine ' + comment.highlight_start_y + ' to Line ' + comment.highlight_end_y + '\n'+ comment.content)
    return githubComments   


def getDocumentInfo(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()


def getDocumentInfoViaLocation(name, parent_folder):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.name == name, models.Document.parent_folder == parent_folder)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()

def createNewDocument(document_name, parent_folder, proj_id, item):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            name = document_name,
            parent_folder = parent_folder,
            associated_proj_id = proj_id
        )
        conn.execute(stmt)
        conn.commit()

    createNewSnapshot(proj_id, doc_id, item)
    return doc_id

def moveDocumentUtil(doc_id, parent_folder):
    with engine.connect() as conn:
        stmt = (update(models.Document)
        .where(models.Document.doc_id == doc_id)
        .values(parent_folder = parent_folder)
        )
        conn.execute(stmt)
        conn.commit()
    return parent_folder

def moveFolderUtil(folder_id, parent_folder):
    with engine.connect() as conn:
        stmt = (update(models.Folder)
        .where(models.Folder.folder_id == folder_id)
        .values(parent_folder = parent_folder)
        )
        conn.execute(stmt)
        conn.commit()
    return parent_folder

def getDocumentPath(doc_id):
    document = getDocumentInfo(doc_id)
    paths = getProjectFoldersAsPaths(document["associated_proj_id"])
    return paths[document["parent_folder"]] + document["name"]

def getFolderPath(folder_id):
    folder = getFolderInfo(folder_id)
    paths = getProjectFoldersAsPaths(folder["associated_proj_id"])
    return paths[folder["parent_folder"]] + folder["name"]

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
  
def getAllProjectFolders(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.associated_proj_id == proj_id)
        foundFolders = conn.execute(stmt)
        folders = []
        for folder in foundFolders:
            folders.append(folder._asdict())
        return folders

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, item):
    with engine.connect() as conn:
        
        stmt = select(models.Document).where(
            models.Document.doc_id == doc_id)

        doc = conn.execute(stmt)#.first()

        doc_name = doc.first().name
            
        snapshot_id = createID()
        stmt = insert(models.Snapshot).values(
            snapshot_id = snapshot_id,
            associated_document_id = doc_id,
            name = doc_name
        )
        conn.execute(stmt)
        conn.commit()

        uploadBlob(str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id), item)
        return snapshot_id




def getSnapshotProject(snapshot_id):
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

def getSnapshotPath(snapshot_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            snapshot = conn.execute(stmt)
            doc_id = snapshot.first().associated_document_id

            stmt = select(models.Document).where(models.Document.doc_id == doc_id)
            document = conn.execute(stmt)
            proj_id = document.first().associated_proj_id
            return str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id)
    except:
        return None

def getSnapshotInfo(snapshot_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
        snapshot = conn.execute(stmt).first()
        if snapshot == None:
            return None
        return snapshot._asdict()

def getCommentInfo(comment_id):
    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.comment_id == comment_id)
        comment = conn.execute(stmt).first()
        return comment._asdict()

def getCommentProject(comment_id):
    return getSnapshotProject(getCommentInfo(comment_id)["snapshot_id"])

def getSnapshotContentUtil(snapshot_id):
    blob = getBlob(getSnapshotPath(snapshot_id))
    return blob

def deleteSnapshotUtil(snapshot_id):
    try:
        with engine.connect() as conn:
            deleteBlob(getSnapshotPath(snapshot_id))
            stmt = delete(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            conn.execute(stmt)
            stmt = delete(models.Comment).where(models.Comment.snapshot_id == snapshot_id)
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def deleteDocumentUtil(doc_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id)
            snapshots = conn.execute(stmt)
            for snapshot in snapshots:
                deleteSnapshotUtil(snapshot.snapshot_id)
            stmt = delete(models.Document).where(models.Document.doc_id == doc_id)
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

def renameDocumentUtil(doc_id, doc_name):
    try:
        with engine.connect() as conn:
            stmt = (update(models.Document)
                .where(models.Document.doc_id == doc_id)
                .values(name=doc_name)
                )
            conn.execute(stmt)
            conn.commit()
        return True, "No Error"
    except Exception as e:
        return False, e

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
    #permissions is a placeholder value for owner because we only have 1 perm rn but hey it's 1111
        relationstmt = insert(models.UserProjectRelation).values(
                user_email = owner,
                proj_id = pid,
                role = "Owner",
                permissions = 15
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

# Returns Array of Dictionaries
def getAllDocumentSnapshotsInOrder(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id).order_by(models.Snapshot.date_created.asc())
        foundSnapshots = conn.execute(stmt)
        
        listOfSnapshots = []
        
        for row in foundSnapshots:
            listOfSnapshots.append(row._asdict())
        
        return listOfSnapshots

def getDocumentLastSnapshotContent(doc_id):
    snapshot = getAllDocumentSnapshotsInOrder(doc_id)[-1]
    if snapshot == None:
        return False
    doc_id = snapshot["associated_document_id"]
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        document = conn.execute(stmt)
        proj_id = document.first().associated_proj_id

    snapshotContents = getBlob(str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot["snapshot_id"]))
    return snapshotContents

def userExists(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        return result.first() != None

def createID():
    return uuid.uuid4().int >> (128 - 31)
      
def isValidRequest(parameters, requiredKeys):
    for key in requiredKeys:
        if key not in parameters:
            return False

    return True


#repository = "user/reponame", aka just github style
def getBranches(token, repository):
    try:
        auth = Auth.Token(token)
        g2 = Github(auth=auth)
        
        repo = g2.get_repo(repository)
        branches = list(repo.get_branches())
        branchnames = []
        for branch in branches:
            branchnames.append(branch.name)
        return True, branchnames
    except Exception as e:
        return False, e

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

def getProjectFoldersAsPaths(proj_id):
    project = getProjectInfo(proj_id)
    folders = getAllProjectFolders(proj_id)
    folderIDToPath = {}
    folders = [folder for folder in folders if folder["parent_folder"] > 0]
    folderIDToPath = getFolderPathsFromList(project["root_folder"], "", folders)
    folderIDToPath[project["root_folder"]] = ""
    return folderIDToPath
    
def resolveCommentHelperFunction(comment_id):
    with engine.connect() as conn:
        stmt = (update(models.Comment)
        .where(models.Comment.comment_id == comment_id)
        .values(is_resolved=True)
        )

        conn.execute(stmt)
        conn.commit()

    pass
  
def fetchFromCloudStorage(blobName:str):
    '''
    If cached, returns the blob in cache.
    If uncached, makes a request for the blob in Google Buckets
    and returns the blob.

    Args
      blobName:
        Name of the blob to retrieve.
    '''
    try:
        from cacheUtils import getCloudStorageCache
        blobContents = getCloudStorageCache().get(blobName)
        if blobContents is None:
            blobContents = getBlob(blobName)
            print('uncached\n\n\n')
        else:
            print('cached\n\n\n')
        
        if blobContents is not None:
            getCloudStorageCache().set(blobName, blobContents)
        
        return blobContents
    except Exception as e:
        print(e)
        return None

def publishCloudStorageUpdate(blobName: str):
    '''
    Publishes a message with the blobName as the key to indicate that the
    specified blob has been updated. The key is used to delete the blob
    from cache.

    Args
      blobName:
        Name of the blob that was updated (created, edited, deleted)
    '''
    publishTopicUpdate("cloud-storage-updates", blobName)
    return

def filterCommentsByPredicate(predicate):
    '''
    Filters the comments database for all comments that satisfy the
    given predicate and returns the comments as a list.

    Args
      predicate:
        An SQL column expression that either returns True or False.
    '''
    commentsList = []
    with Session() as session:
        try:
            filteredComments = session.query(models.Comment) \
                .filter(predicate) \
                .all()
            
            for comment in filteredComments:
                commentsList.append({
                    "comment_id": comment.comment_id,
                    "snapshot_id": comment.snapshot_id,
                    "author_email": comment.author_email,
                    "reply_to_id": comment.reply_to_id,
                    "date_created": comment.date_created,
                    "date_modified": comment.date_modified,
                    "content": comment.content,
                    "highlight_start_x": comment.highlight_start_x,
                    "highlight_start_y": comment.highlight_start_y,
                    "highlight_end_x": comment.highlight_end_x,
                    "highlight_end_y": comment.highlight_end_y,
                    "is_resolved": comment.is_resolved
                })

        except Exception as e:
            commentsList = None
    
    return commentsList

def buildStringFromLLMResponse(code, response):
    success = response["success"]
    if success == False:
        return "waow, this failed!"
    insertions = convertKeysToInt(response["insertions"])
    deletions = response["deletions"]
    codeList = code.split('\n')
    builtString = ""
    for i in range(len(codeList)+1):
        if i not in deletions:
            if i > 0:
                builtString = builtString + codeList[i-1]
                if i < len(codeList) or insertions.get(i) != None:
                    builtString = builtString + '\n'
        if insertions.get(i) != None:
            builtString = builtString + insertions.get(i)
            if i < len(codeList) or insertions.get(i) != None:
                builtString = builtString + '\n'
    return builtString

def convertKeysToInt(somedict):
    rv = {}
    for key in somedict.keys():
        rv[int(key)] = somedict[key]
    return rv
