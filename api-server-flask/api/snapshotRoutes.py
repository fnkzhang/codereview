from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.projectUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *
from utils.miscUtils import *
from utils.buckets import *
from utils.userAndPermissionsUtils import *
import models

@app.route('/api/Snapshot/<proj_id>/<doc_id>/<snapshot_id>/', methods=["GET"])
def getSnapshot(proj_id, doc_id, snapshot_id):
    print("GETTING SNAPSHOT", proj_id, doc_id, snapshot_id)
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    blob = fetchFromCloudStorage(str(snapshot_id))
    print(blob)
    setSnapshotAsSeen(snapshot_id, idInfo["email"])
    try:
        blob = blob.decode()
    except:
        blob = None
    return {
        "success": True,
        "reason": "",
        "body": blob
    }

# Data Passed in body while project and document id passed in url
@app.route('/api/Snapshot/<proj_id>/<doc_id>/<commit_id>/', methods=["POST"])
def createSnapshot(proj_id, doc_id, commit_id):
    print("Creating Snapshot", proj_id, doc_id)
    inputBody = request.get_json()
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success":False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if inputBody.get("data") == None:
        return {"success": False, "reason":"no data", "body":{}}
    working = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    if working == None:
        work_id = createNewCommit(proj_id, idInfo["email"], commit_id)
    else:
        work_id = working["commit_id"]
        rebuildPathToPrevCommit(doc_id, work_id, commit_id)
        
    snapshot_id = createNewSnapshot(proj_id, doc_id, inputBody["data"], work_id, idInfo["email"])
    return {
        "success": True,
        "reason": "",
        "body": snapshot_id
    }

@app.route('/api/Snapshot/<snapshot_id>/', methods=["DELETE"])
def deleteSnapshot(snapshot_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }
    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = deleteSnapshotUtil(snapshot_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

# look into pagination
# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/api/#flask_sqlalchemy.SQLAlchemy.paginate
@app.route('/api/Snapshot/<snapshot_id>/comments/get', methods=["GET"])
def getCommentsOnSnapshot(snapshot_id):

    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }
    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    commentsList = filterCommentsByPredicate(models.Comment.snapshot_id == snapshot_id)
    if commentsList is None:
        return {
            "success": False,
            "reason": "Error Grabbing Comments From Database"
        }

    print("Successful Read")
    return {
        "success": True,
        "reason": "",
        "body": commentsList
    }

