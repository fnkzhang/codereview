
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

import models

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

from cacheUtils import cloudStorageCache, publishTopicUpdate

engine = connectCloudSql()
Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html

def uploadBlob(blobName, item):
    storage_client = storage.Client()
    bucket = storage_client.bucket('cr_storage')
    print("Uploading to", blobName)
    blob = bucket.blob(blobName)
    blob.upload_from_string(data = item, content_type='application/json')
    
    return True

def getBlob(blobName):
    print("GETTING BLOB", blobName)
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

def deleteProjectWithProjectID(proj_id):
    with engine.connect() as conn:
        grabProjectStatement = select(models.Project.author_email).where(models.Project.proj_id == proj_id)

        result = conn.execute(grabProjectStatement)
        projectOwnerEmail = result.first()
        print(result)



        # GET PROJECT AUTHOR EMAIL AND DELETE THE COMMENT
        deleteProjectRelation = delete(models.UserProjectRelation).where(models.UserProjectRelation.user_email == projectOwnerEmail)
        deleteProjectStatement = delete(models.Project).where(models.Project.proj_id == proj_id)
        deleteDocumentStatement  = delete(models.Document).where(models.Document.associated_proj_id == proj_id)
        #deleteDocumentCommentsStatement = delete(models.Comment).where()

        conn.execute(deleteProjectRelation)
        conn.execute(deleteProjectStatement)
        conn.execute(deleteDocumentStatement)

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
            return -1
        return foundFolder

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

        blobContents = cloudStorageCache.get(blobName)
        if blobContents is None:
            blobContents = getBlob(blobName)
            print('uncached\n\n\n')
        else:
            print('cached\n\n\n')
        
        if blobContents is not None:
            cloudStorageCache.set(blobName, blobContents)
        
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