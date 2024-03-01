
from flask import Flask, request, jsonify
from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from cloudSql import connectCloudSql

import models
engine = connectCloudSql()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"
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

def getDocumentInfo(doc_id):
    with engine.connect() as conn:
        stmt = select(models.Document).where(models.Document.doc_id == doc_id)
        first = conn.execute(stmt).first()
        if first == None:
            return -1
        return first

def createNewFolder(folder_name, parent_folder):
    folder_id = createID()
    with engine.connect() as conn:
        stmt = insert(models.Folders).values(
            folder_id = folder_id,
            name = folder_name,
            parent_folder = parent_folder
        )
        conn.execute(stmt)
        conn.commit()
    return folder_id

#puts documentname as snapshot name until that changes
def createNewSnapshot(proj_id, doc_id, item):
    with engine.connect() as conn:
        
        stmt = select(models.Document).where(
            models.Documet.doc_id == doc_id)
        doc = conn.execute(stmt).first
        doc_name = doc.name
        currentsnapshotlist = doc.snapshots
        
        snapshot_id = createID()
        stmt = insert(models.Snapshot).values(
            snapshot_id = snapshot_id,
            name = doc_name
        )
        conn.execute(stmt)

        stmt = update(models.Document).where(
                    models.Document.doc_id == doc_id
                ).values(
                    snapshots = currentsnapshotlist + [snapshot_id]
                )
        conn.execute(stmt)
        conn.commit()
        uploadBlob(proj_id + '/' + doc_id + '/' + snapshot_id, item)

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
