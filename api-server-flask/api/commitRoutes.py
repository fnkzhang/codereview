from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.documentUtils import *
from utils.folderUtils import *
from utils.miscUtils import *
from utils.userAndPermissionsUtils import *
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *

import models

#gets a dict with the keys of documents mapping to their snapshot in the commit
@app.route('/api/Commit/<commit_id>/', methods = ["GET"])
def getCommitDocumentSnapshotPairs(commit_id):
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
    try:
        proj_id = getCommitInfo(commit_id)["proj_id"]
    except:
        return {"success":False, "reason":"commit doesn't exist"}
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    pairs = getAllCommitDocumentSnapshotRelation(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": pairs
    }

#put last commit_id in "last_commit", if none, don't put any
@app.route('/api/Commit/<proj_id>/createCommit/', methods = ["POST"])
def createCommit(proj_id):
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
    body = request.get_json()
    if(getUserProjPermissions(idInfo["email"], proj_id) < 3):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if "last_commit" in body:
        last_commit = None
    else:
        last_commit = body["last_commit"]
    commit_id = createNewCommit(proj_id, idInfo["email"], last_commit)
    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

#probably used if someone is halfway through a commit and wants to kill it
#will fail if commit is already resolved
@app.route('/api/Commit/<commit_id>/', methods=["DELETE"])
def deleteWWorkingCommit(commit_id):
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
    try:
        commit_info = getCommitInfo(commit_id)
    except:
        return {"success":False, "reason":"commit doesn't exist"}

    if(idInfo["email"] != commit_info["author_email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = deleteCommitUtil(commit_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

@app.route('/api/Commit/<commit_id>/getFolderTree/',methods=["GET"])
def getCommitFolderTree(commit_id):
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
    proj_id = getCommitInfo(commit_id)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    foldertree = getCommitTree(commit_id)
    return {
            "success":True,
            "reason": "",
            "body":foldertree
            }


