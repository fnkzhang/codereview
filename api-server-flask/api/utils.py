
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
    
def userExists(user_email):
    with engine.connect() as conn:
        stmt = select(models.User).where(models.User.user_email == user_email)
        result = conn.execute(stmt)
        return result.first() != None

def createID():
    return uuid.uuid4()

# Call Func every api func call to make sure that user is Authenticated before running
def IsValidCredential(credentialToken):
    try:
        print("Valid ID_TOKEN supplied")
        id_token.verify_oauth2_token(credentialToken, requests.Request(), CLIENT_ID)
        return True
    except ValueError:
        print("FAILED INVALID TOKEN")
        return False
      
def isValidRequest(parameters, requiredKeys):
    for key in requiredKeys:
        if key not in parameters:
            return False

    return True
