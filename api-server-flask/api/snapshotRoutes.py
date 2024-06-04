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
    """
    
    ``GET /api/Snapshot/<proj_id>/<doc_id>/<snapshot_id>/``

    **Explanation:**
        Gets the contents of a snapshot. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): id of the project this is in
        - doc_id (int): id of the document the snapshot is for
        - snapshot_id (int): id of the snapshot

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (str): The contents of the snapshot in string format, if unable to be decoded, returns None

    """
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
    """
    
    ``POST /api/Snapshot/<proj_id>/<doc_id>/<commit_id>/``

    **Explanation:**
        Creates a snapshot on a document in a commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): id of the project this is in
        - doc_id (int): id of the document the snapshot is for
        - commit_id (int): id of the commit this is happening on
        - request.body (dict):
            - data (str): contents of the snapshot

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): Id of the newly created snapshot
    """
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
    """
    ``DELETE /api/Snapshot/<snapshot_id>/``

    **Explanation:**
        Deletes a snapshot. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - snapshot_id (int): id of the snapshot

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.

    """
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

@app.route('/api/Snapshot/<snapshot_id>/comments/get', methods=["GET"])
def getCommentsOnSnapshot(snapshot_id):
    """
    
    ``GET /api/Snapshot/<snapshot_id>/comments/get``

    **Explanation:**
        Gets all comments attatched to the snapshot. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - snapshot_id (int): id of the snapshot

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): list of Comment objects as dicts

    """
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

