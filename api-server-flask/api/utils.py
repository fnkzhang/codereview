
from flask import Flask, request, jsonify
from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text, delete
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from cloudSql import connectCloudSql

from github import Github
from github import Auth

import models
engine = connectCloudSql()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

def uploadBlob(blobName, item):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
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
def getUser(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        #needs to happen because you can only call result.first() once
        user = result.first()
        if user == None:
            return -1
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
            return -1
        return foundProject._asdict()

def getAllProjectDocuments(proj_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.associated_proj_id == int(proj_id))

        results = conn.execute(stmt)

        arrayOfDocuments = []

        for row in results:
            arrayOfDocuments.append(row._asdict())

        return arrayOfDocuments

def getDocumentInfo(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        foundDocument = conn.execute(stmt).first()
        if foundDocument == None:
            return None
        return foundDocument._asdict()

def getDocumentInfo(name, parent_folder):
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


def getFolderInfo(folder_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.folder_id == folder_id)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return None
        return foundFolder._asdict()

def getFolderInfo(name, parent_folder):
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

def deleteSnapshotUtil(snapshot_id):
    try:
        with engine.connect() as conn:
            stmt = select(models.Snapshot).where(models.Snapshot.snapshot_id == snapshot_id)
            snapshot = conn.execute(stmt)
            doc_id = snapshot.first().associated_document_id
            
            stmt = select(models.Document).where(models.Document.doc_id == doc_id)
            document = conn.execute(stmt)
            proj_id = document.first().associated_proj_id
            
            deleteBlob(str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id))
            
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

# Returns Array of Dictionaries
def getAllDocumentSnapshotsInOrder(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id).order_by(models.Snapshot.date_created.asc())
        foundSnapshots = conn.execute(stmt)
        
        listOfSnapshots = []
        
        for row in foundSnapshots:
            listOfSnapshots.append(row._asdict())
        
        return listOfSnapshots

def getLastSnapshotinDocumentContent(doc_id):
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
        g = Github(auth=auth)
        g.get_user().login
        
        repo = g.get_repo(repository)
        branches = list(repo.get_branches())
        print(branches)
        branchnames = []
        for branch in branches:
            branchnames.append(branch.name)
        return True, branchnames
    except Exception as e:
        return False, e


