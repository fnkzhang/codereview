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

@app.route('/api/Document/<proj_id>/<doc_id>/', methods=["GET"])
def getDocument(proj_id, doc_id):
    print(request)
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

    info = getDocumentInfo(doc_id)
    return {"success": True, "reason":"", "body": info}

#requires
    #credentials in headers
    #In body:
    #data (text you want in the document)
    #doc_name (name of document)
    #parent_folder (folder you're making it in), if not in request will put in root folder
@app.route('/api/Document/<proj_id>/', methods=["POST"])
def createDocument(proj_id):
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
    doc_id = createNewDocument(inputBody["doc_name"], folder, proj_id, inputBody["data"])
    return {
        "success": True,
        "reason": "",
        "body": doc_id
    }

@app.route('/api/Document/<doc_id>/', methods=["DELETE"])
def deleteDocument(doc_id):
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
        proj_id = getDocumentInfo(doc_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    rv, e = deleteDocumentUtil(doc_id)
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
@app.route('/api/Document/<doc_id>/rename/', methods=["POST"])
def renameDocument(doc_id):
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
        proj_id = getDocumentInfo(doc_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    body = request.get_json()
    rv, e = renameDocumentUtil(doc_id, body["doc_name"])
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
@app.route('/api/Document/<doc_id>/move/', methods=["POST"])
def moveDocument(doc_id):
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
        proj_id = getDocumentInfo(doc_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "document doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    folder = inputBody["parent_folder"]
    if not moveDocumentUtil(doc_id, folder):
        return {"success": False,
                "reason":"invalid document"
                }
    return {
        "success": True,
        "reason": "",
        "body": ""
    }

@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotId/', methods=["GET"])
def getAllDocumentSnapshots(proj_id, doc_id):
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

    foundSnapshots = getAllDocumentSnapshotsInOrder(doc_id)

    return {"success": True, "reason":"", "body": foundSnapshots}

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

    proj_id = getDocumentInfo(document_id)["associated_proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    listOfSnapshotIDs = []
    foundSnapshots = getAllDocumentSnapshotsInOrder(document_id)

    for snapshot in foundSnapshots:
        # Query
        listOfSnapshotIDs.append(snapshot["snapshot_id"])

    listOfComments = filterCommentsByPredicate(models.Comment.snapshot_id.in_(listOfSnapshotIDs))
    if listOfComments is None:
        return {
            "success": False,
            "reason": "Error Grabbing Comments From Database"
        }

    return {
        "success": True,
        "reason": "Found all Comments For All Snapshots for document",
        "body": listOfComments
    }

