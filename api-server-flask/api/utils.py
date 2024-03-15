
from flask import Flask, request, jsonify
from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, update, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from cloudSql import connectCloudSql

import models

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

engine = connectCloudSql()

def uploadBlob(blobName, item):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.blob(blobName)
    blob.upload_from_string(data = item, content_type='application/json')
    return True

def getBlob(blobName):
    print(blobName)
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    blob = bucket.get_blob(blobName)
    return blob.download_as_text()

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

def getUserProjPermissions(user_email, proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email, models.UserProjectRelation.proj_id == proj_id)
        #idk if this works :) change later
        result = conn.execute(stmt)
        #can probably remove/change the 2nd part of the or statement when we finalize what permissions are represented by what
        
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
    
def getAllDocumentsForProject(proj_id):
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
            return -1
        return foundDocument
  
def createNewDocument(document_name, parent_folder):
    doc_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Document).values(
            doc_id = doc_id,
            name = document_name,
            parent_folder = parent_folder
        )
        conn.execute(stmt)
        foldercontentstmt = select(models.Folder).where(
                models.Folder.folder_id == parent_folder
                )
        contents = conn.execute(stmt).first().contents
        contents.append([doc_id, 0])
        stmt = update(models.Folder).where(
                models.Folder.folder_id == parent_folder
                ).values(
                contents = contents
                )
        conn.commit()
    return doc_id


def getFolderInfo(folder_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.folder_id == folder_id)
        foundFolder = conn.execute(stmt).first()
        if foundFolder == None:
            return -1
        return foundFolder

def createNewFolder(folder_name, parent_folder):
    folder_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Folder).values(
            folder_id = folder_id,
            name = folder_name,
            parent_folder = parent_folder
        )
        conn.execute(stmt)
        foldercontentstmt = select(models.Folder).where(
                models.Folder.folder_id == parent_folder
                )
        contents = conn.execute(stmt).first().contents
        contents.append([folder_id, 1])
        stmt = update(models.Folder).where(
                models.Folder.folder_id == parent_folder
                ).values(
                contents = contents
                )
        conn.commit()
    return folder_id

def getAllChildDocuments(folder_id):
    with engine.connect() as conn:
        stmt = select(models.Folder).where(models.Folder.folder_id == folder_id)
        folder = conn.execute(stmt).first()
        if folder == None:
            return -1
        else:
            documents = []
            for content in folder.content:
                if content[2] == 0:
                    documents.append(content[0])
                else:
                    documents = documents + getAllChildDocuments(content[0])
            return documents

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, item):
    with engine.connect() as conn:
        
        stmt = select(models.Document).where(
            models.Document.doc_id == doc_id)

        doc = conn.execute(stmt).first()

        doc_name = doc.name
            
        snapshot_id = createID()
        stmt = insert(models.Snapshot).values(
            snapshot_id = snapshot_id,
            associated_document_id = doc_id,
            name = doc_name
        )
        conn.execute(stmt)
        conn.commit()

        uploadBlob(str(proj_id) + '/' + str(doc_id) + '/' + str(snapshot_id), item)

# Returns Array of Dictionaries
def getAllDocumentSnapshotsInOrder(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Snapshot).where(models.Snapshot.associated_document_id == doc_id).order_by(models.Snapshot.date_created.asc())
        foundDocuments = conn.execute(stmt)
        
        listOfDocuments = []
        
        for row in foundDocuments:
            listOfDocuments.append(row._asdict())
        
        return listOfDocuments

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