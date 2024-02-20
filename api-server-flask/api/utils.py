from google.cloud import storage
import google.auth
from datetime import datetime
import json
import uuid
import os

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase
from cloudSql import connectCloudSql
from flaskAPI import engine

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "googlecreds.json"

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
        stmt = select(models.UserProjectRelation).where(models.UserProjectRelation.user_email = user_email, models.UserProjectRelation.proj_id = proj_id)
        #idk if this works :) change later
        result = conn.execute(stmt)
        if result.first() == None || result.first().permissions == 0:
            return False
        return True

def isValidRequest(requestedData):
    if "credential" not in requestedData:
        return {"success": False, "reason": "Invalid JSON Provided",
                "body":{}
                }
    credential = requestedData["credential"]
    if not IsValidCredential(credential):
        retData = {
            "success": False,
            "reason": "Invalid Token Provided",
            "body": {}
        }
        return jsonify(retData)
    return None

def createID():
    return uuid.uuid4()
