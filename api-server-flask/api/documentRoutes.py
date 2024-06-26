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
    """
    ``GET /api/Document/<proj_id>/<doc_id>/<commit_id>/``

    **Explanation:**
        Gets the document information in the commit given. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): The project ID.
        - doc_id (int): The document ID.
        - commit_id (int): The commit ID.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the retrieval was successful.
            - reason (str): Description of the result of the retrieval.
            - body (dict): Document information.

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
    """
    ``POST /api/Document/<proj_id>/<commit_id>/``

    **Explanation:**
        Creates a document in the given commit. This will also automatically generate a snapshot for the document with the given data. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): The project ID.
        - commit_id (int): The commit ID.
        - request.body (dict):
            - doc_name (str): name of document
            - data (str): text you want in the document
            - parent_folder(int): Optional; if not in request will put in root folder

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the creation was successful.
            - reason (str): Description of the result of the creation.
            - body (str): ID of the created document.

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
    """
    ``DELETE /api/Document/<doc_id>/<commit_id>/``

    **Explanation:**
        Deletes a document from the given commit. This will also purge any snapshots that originated from that document in that commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        doc_id (int): The document ID.
        commit_id (int): The commit ID.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the deletion was successful.
            - reason (str): Description of the result of the deletion.

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
    """
    ``POST /api/Document/<doc_id>/<commit_id>/rename/``

    **Explanation:**
        Renames a document. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - doc_id (int): The document ID
        - commit_id (int): the commit you're changing the name of
        - request.body(dict):
            - doc_name (str): new name

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

@app.route('/api/Document/<doc_id>/<commit_id>/move/', methods=["POST"])
def moveDocument(doc_id, commit_id):
    """
    ``POST /api/Document/<doc_id>/<commit_id>/move/``

    **Explanation:**
        Moves a document. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - doc_id (int): The document ID
        - commit_id (int): The commit you're doing action on
        - request.body (dict):
            - parent_folder (int): folder you're moving it to

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (str): An empty string representing the body of the response.

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

@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotId/', methods=["GET"])
def getAllDocumentCommittedSnapshots(proj_id, doc_id):
    """
    ``GET /api/Document/<proj_id>/<doc_id>/getSnapshotId/``

    **Explanation:**
        Returns every snapshot associated with this document and committed commits. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): The project id the document is in
        - doc_id (int): The id of the document

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Whether or not the request succeeded
            - reason (str): The reason
            - body (list): A list of dicts of the format 
                {"snapshot": A Snapshot object in the form of a dict
                  "commit": A Commit object in the form of a dict, this is the commit that the snapshot above was originally associated with
                }
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
    foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(doc_id)
    snapCommits = []
    for snap in foundSnapshots:
        commit = getCommitInfo(snap["og_commit_id"])
        snapCommits.append({"snapshot":snap, "commit":commit})
    
    print(snapCommits)
    return {"success": True, "reason":"", "body": snapCommits}

import time

@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotIdAndWorking/', methods=["GET"])
def getAllDocumentCommittedSnapshotsIncludingWorking(proj_id, doc_id):
    """
    ``GET /api/Document/<proj_id>/<doc_id>/getSnapshotIdAndWorking/``

    **Explanation:**
        Returns every snapshot associated with this document and committed commits. Also return the snapshots associated with any working commits of the user sending the request based off the authentication headers. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): The project id the document is in
        - doc_id (int): The id of the document


    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Whether or not the request succeeded
            - reason (str): The reason
            - body (list): A list of dicts of the format {"snapshot":'information about a snapshot', "commit":'information about the commit the snapshot is originally from'}

    """
    start = time.time()
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
    permstime = time.time()
    working = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    workingtime = time.time()
    if working != None:
        foundSnapshots = getAllDocumentCommittedSnapshotsInOrderIncludingWorking(doc_id, working["commit_id"])
    else:
        foundSnapshots = getAllDocumentCommittedSnapshotsInOrder(doc_id)
    snapshotfind = time.time()
    snapCommits = []
    for snap in foundSnapshots:
        commit = getCommitInfo(snap["og_commit_id"])
        snapCommits.append({"snapshot":snap, "commit":commit})
    getcommits = time.time()
    print("perms:", permstime-start, " getworking:", workingtime-permstime, " snapshotfindtime:", snapshotfind-workingtime, " commitfindtime:", getcommits - snapshotfind)
    return {"success": True, "reason":"", "body": snapCommits}

#changes a document's snapshot on a specific commit to the given one
@app.route('/api/Document/<doc_id>/<commit_id>/<snapshot_id>/changeTo/', methods=["POST"])
def changeDocumentSnapshot(doc_id, commit_id, snapshot_id):
    """
    ``POST /api/Document/<doc_id>/<commit_id>/<snapshot_id>/changeTo/``

    **Explanation:**
        This endpoint changes the document identified by 'doc_id' and 'commit_id' to the snapshot identified by 'snapshot_id'.
        It requires authentication via an Authorization token header.
        Only users with sufficient permissions can change document snapshots.

    **Args:**
        - doc_id (int): The identifier of the document.
        - commit_id (int): The identifier of the commit.
        - snapshot_id (int): The identifier of the snapshot to change to.

    Returns:
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (str): An empty string representing the body of the response.

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
    """
    ``GET /api/Document/<document_id>/comments/``

    **Explanation:**
        Gets all comments on a document across all committed snapshots. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - document_id (int): The identifier of the document.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): A list of dictionaries representing comments associated with the document.
                Each dictionary contains information about a single comment.

    """
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
    working = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    if working != None:
        foundSnapshots = getAllDocumentCommittedSnapshotsInOrderIncludingWorking(document_id, working["commit_id"])
    else:
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
        comment["isSeen"]= isCommentSeenByUser(comment["comment_id"], idInfo["email"])
        setCommentAsSeen(comment["comment_id"], idInfo["email"])
    
    return {
        "success": True,
        "reason": "Found all Comments For All Snapshots for document",
        "body": listOfComments
    }

