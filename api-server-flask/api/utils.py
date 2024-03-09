
from flask import Flask, request, jsonify
from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import ColumnExpressionArgument, Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from cloudSql import connectCloudSql
from cacheUtils import cloudStorageCache, commentsCache, publishTopicUpdate

import models
engine = connectCloudSql()

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(engine)


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

#for eventual use when i decide to actually put in the time
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

def getUserProjPermissions(user_email, proj_id):
    with engine.connect() as conn:
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email == user_email, models.UserProjectRelation.proj_id == proj_id)
        #idk if this works :) change later
        result = conn.execute(stmt)
        #can probably remove/change the 2nd part of the or statement when we finalize what permissions are represented by what
        
        #needs to happen because you can only call result.first() once
        first = result.first()
        if first == None:
            return -1
        return first.permissions
    
def userExists(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        return result.first() != None

def createID():
    return uuid.uuid4()
      
def isValidRequest(parameters, requiredKeys):
    for key in requiredKeys:
        if key not in parameters:
            return False

    return True

def fetchFromCloudStorage(blobName:str):
    '''
    If cached, returns the blob in cache.
    If uncached, makes a request for the blob in Google Buckets
    and returns the blob.

    Args
      blobName:
        Name of the blob to retrieve.
    '''
    blobContents = cloudStorageCache.get(blobName)
    if blobContents is None:
        blobContents = getBlob(blobName)
    
    if blobContents is not None:
        cloudStorageCache.set(blobName, blobContents)
    
    return blobContents

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

def fetchCommentsOnDiff(diff_id: int):
    '''
    If cached, returns all comments associated with the diff in cache.
    If uncached, makes a request to query the comments database
    in Cloud SQL and returns all comments associated with the diff.

    Args
      diff_id:
        Unique identifier of the diff to retrieve comments from.
    '''
    commentsList = commentsCache.get(diff_id)
    if commentsList is None:
        commentsList = filterCommentsByPredicate(
            models.Comment.diff_id == diff_id)
    
    if commentsList is not None:
        commentsCache.set(diff_id, commentsList)

    return commentsList

def filterCommentsByPredicate(predicate: ColumnExpressionArgument[bool]):
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
                    "diff_id": comment.diff_id,
                    "author_id": comment.author_id,
                    "reply_to_id": comment.reply_to_id,
                    "date_created": comment.date_created,
                    "date_modified": comment.date_modified,
                    "content": comment.content
                })

        except Exception as e:
            commentsList = None
    
    return commentsList
