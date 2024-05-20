from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.projectUtils import *
from utils.documentUtils import *
from utils.snapshotUtils import *
from utils.commentUtils import *
from utils.userAndPermissionsUtils import *
from utils.miscUtils import *

import models

# Get Document with the model data, and parent_folder, and name of the commit in to dict
#commit_id is info about the doc in the commit you're in
@app.route('/api/Document/<proj_id>/<doc_id>/<commit_id>/', methods=["GET"])
def getDocument(proj_id, doc_id, commit_id):
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

    info = getDocumentInfo(doc_id, commit_id)
    return {"success": True, "reason":"", "body": info}

#requires
    #credentials in headers
    #In body:
    #data (text you want in the document)
    #doc_name (name of document)
    #parent_folder (folder you're making it in), if not in request will put in root folder
@app.route('/api/Document/<proj_id>/<commit_id>/', methods=["POST"])
def createDocument(proj_id, commit_id):
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
    if "parent_folder" not in inputBody:
        folder = getProjectInfo(proj_id)["root_folder"]
    else:
        folder = inputBody["parent_folder"]
    doc_id = createNewDocument(inputBody["doc_name"], folder, proj_id, inputBody["data"], commit_id, idInfo["email"])
    return {
        "success": True,
        "reason": "",
        "body": doc_id
    }

#commit_id in the url is just the commit you're deleting the document from
@app.route('/api/Document/<doc_id>/<commit_id>/', methods=["DELETE"])
def deleteDocument(doc_id, commit_id):
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
        proj_id = getDocumentInfo(doc_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    rv, e = deleteDocumentFromCommit(doc_id, commit_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

#body: put new name in "doc_name"
#commit_id in url is commit you're changing the name of
@app.route('/api/Document/<doc_id>/<commit_id>/rename/', methods=["POST"])
def renameDocument(doc_id, commit_id):
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
        proj_id = getDocumentInfo(doc_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    body = request.get_json()
    rv, e  = renameItem(doc_id, body["doc_name"], commit_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Rename"
    }

#requires
    #credentials in headers
    #In body:
    #parent_folder (folder you're moving it to
#commit id in url is commit you're doing action on blah blah you get the idea
@app.route('/api/Document/<doc_id>/<commit_id>/move/', methods=["POST"])
def moveDocument(doc_id, commit_id):
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
    try:
        proj_id = getDocumentInfo(doc_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    folder = inputBody["parent_folder"]
    if not moveItem(doc_id, folder, commit_id):
        return {"success": False,
                "reason":"invalid document"
                }
    return {
        "success": True,
        "reason": "",
        "body": ""
    }

#we have og_commit_ids for snapshtos so probably display those instead of snapshot 1, 2...github also has garbage as snapshot name so it's fine :)
@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotId/', methods=["GET"])
def getAllDocumentCommittedSnapshots(proj_id, doc_id):
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
    foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(doc_id)

    return {"success": True, "reason":"", "body": foundSnapshots}

@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotIdAndWorking/', methods=["GET"])
def getAllDocumentCommittedSnapshotsIncludingWorking(proj_id, doc_id):
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
    working = getUserWorkingCommitInProject(proj_id)
    if working != None:
        foundSnapshots = getAllDocumentCommittedSnapshotsInOrderIncludingWorking(doc_id, working["commit_id"])
    else:
        foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(doc_id)
    return {"success": True, "reason":"", "body": foundSnapshots}

#changes a document's snapshot on a specific commit to the given one
@app.route('/api/Document/<doc_id>/<commit_id>/<snapshot_id>/changeTo/', methods=["POST"])
def changeDocumentSnapshot(doc_id, commit_id, snapshot_id):
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
    try:
        proj_id = getDocumentInfo(doc_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    addSnapshotToCommit(snapshot_id, doc_id, commit_id)
    return {
        "success": True,
        "reason": "",
        "body": ""
    }

@app.route('/api/Document/<document_id>/comments/', methods=["GET"])
def getAllCommentsForDocument(document_id):
    # Authentication
    headers = request.headers

    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided",
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate",
        }

    proj_id = getDocumentProject(document_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    listOfSnapshotIDs = []
    foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(document_id)

    for snapshot in foundSnapshots:
        # Query
        listOfSnapshotIDs.append(snapshot["snapshot_id"])

    listOfComments = filterCommentsByPredicate(models.Comment.snapshot_id.in_(listOfSnapshotIDs))
    if listOfComments is None:
        return {
            "success": False,
            "reason": "Error Grabbing Comments From Database"
        }
    for comment in listOfComments:
        comment["isSeen"]= isCommentSeenByUser(comment["comment_id"], idInfo["body"])
        setCommentAsSeen(comment["comment_id"], idInfo["email"])
    return {
        "success": True,
        "reason": "Found all Comments For All Snapshots for document",
        "body": listOfComments
    }

