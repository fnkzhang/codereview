from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.projectUtils import *
from utils.documentUtils import *
from utils.folderUtils import *
from utils.miscUtils import *
from utils.userAndPermissionsUtils import *
from utils.commitUtils import *
from utils.commitDocSnapUtils import *
from utils.commitLocationUtils import *

import models

@app.route('/api/Commit/<commit_id>/info/', methods = ["GET"])
def getCommitInformation(commit_id):
    """
    ``GET /api/Commit/<commit_id>/info/``

    **Explanation:**
        Gets information about a commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): A Commit object in the form of a dict

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
        proj_id = getCommitInfo(commit_id)["proj_id"]
    except:
        return {"success": False, "reason":"commit doesn't exist"}
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    info = getCommitInfo(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": info
    }

#gets a dict with the keys of documents mapping to their snapshot in the commit
@app.route('/api/Commit/<commit_id>/', methods = ["GET"])
def getCommitDocumentSnapshotPairs(commit_id):
    """
    ``GET /api/Commit/<commit_id>/``

    **Explanation:**
        Gets all the snapshots associated with the documents in a commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): A dict with the keys of documents ids mapping to their snapshot ids

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
#will fail if user already has a working non-committed commit
@app.route('/api/Commit/<proj_id>/createCommit/', methods = ["POST"])
def createCommit(proj_id):
    """
    ``POST /api/Commit/<proj_id>/createCommit/``

    **Explanation:**
        Creates a working commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int)): the id of the project the commit is for
        - request.body (dict):
            - last_commit (int): Optional; the committed this new commit will be based off of, if not provided will be empty

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): The id of the newly created commit

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
        body = request.get_json()
    except:
        body = {}
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if getUserWorkingCommitInProject(proj_id, idInfo["email"]) != None:
        return {"success": False, "reason":"Working Commit Already Exists For User", "body":{}}
    if body.get("last_commit") == None:
        last_commit = None
    else:
        last_commit = body["last_commit"]

    commit_id = createNewCommit(proj_id, idInfo["email"], last_commit)
    # Redundant but just in case since creating new commit already sets it reviewed
    setCommitOpen(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

#no checks will just commit
#in body: requires commit name in "name"
@app.route('/api/Commit/<commit_id>/commitCommit/', methods = ["POST"])
def commitCommit(commit_id):
    """
    ``POST /api/Commit/<commit_id>/commitCommit/``

    **Explanation:**
        Commits a commit. Also sets the commit as open. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit
        - request.body (dict):
            - name (str): what the user is naming the newly committed commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): the id of the commit

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
    body = request.get_json()
    name = body["name"]
    commit = getCommitInfo(commit_id)
    proj_id = commit["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    commit_id = commitACommit(commit_id, name)
    
    print(commit_id)
    # After User Commits to public, commit should be open
    setCommitOpen(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

@app.route('/api/Commit/<commit_id>/setReviewed/', methods=["GET"])
def setReviewedCommit(commit_id):
    """
    
    ``GET /api/Commit/<commit_id>/setReviewed/``

    **Explanation:**
        Sets a commit as reviewed. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): the id of the commit

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
    
    # Using comments to get project_id
    commit = getCommitInfo(commit_id)
    proj_id = commit["proj_id"]

    # Reviewer can make commit reviewed
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    setCommitReviewed(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

@app.route('/api/Commit/<commit_id>/close/', methods=["GET"])
def closeCommit(commit_id):
    """
    
    ``GET /api/Commit/<commit_id>/close/``

    **Explanation:**
        Sets the commit as closed. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): the id of the commit

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
    
    # Using comments to get project_id
    commit = getCommitInfo(commit_id)
    proj_id = commit["proj_id"]
    # ONLY OWNER CAN CLOSE COMMIT
    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    setCommitClosed(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

@app.route('/api/Commit/<commit_id>/approve/', methods=["GET"])
def approveCommit(commit_id):
    """
    
    ``GET /api/Commit/<commit_id>/approve/``

    **Explanation:**
        Sets the commit as approved. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): the id of the commit

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
    
    # Using comments to get project_id
    commit = getCommitInfo(commit_id)
    proj_id = commit["proj_id"]

    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    couldApproveCommit = setCommitApproved(commit_id)
    print(couldApproveCommit)

    if(not couldApproveCommit):
        return {
            "success": False,
            "reason": "Failed To Set Approved",
            "body": commit_id
        }
           
    return {
        "success": True,
        "reason": "",
        "body": commit_id

    }
    
#probably used if someone is halfway through a commit and wants to kill it
@app.route('/api/Commit/<proj_id>/workingCommit/', methods=["DELETE"])
def deleteWorkingCommit(proj_id):
    """
    
    ``DELETE /api/Commit/<proj_id>/workingCommit/``

    **Explanation:**
        Deletes the working commit of the user (derived from credentials in authorization). Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (proj_id): id of the project the commit is getting deleted

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
        commit_info = getUserWorkingCommitInProject(proj_id, idInfo["email"])
        if commit_info == None:
            return {"success":False, "reason":"working commit doesn't exist"}
    except:
        return {"success":False, "reason":"working commit doesn't exist"}

    if(idInfo["email"] != commit_info["author_email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = deleteCommit(commit_info["commit_id"])
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
    """
    ``GET /api/Commit/<commit_id>/getFolderTree/``

    **Explanation:**
        Gets all the items in a commit in a tree structure. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - commit_id (int): id of the commit

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): The top level of the dict is a Folder object represented as a dict. It has the added key of "contents", which maps to another dict, which has 2 keys of "folders" and "documents". These keys map to lists of dicts of their respective items within the folder. Both item dicts have the "seenSnapshots" and "seenComments" key added, which represent whether or not the user has seen all snapshots/comments for that document. The folders also have the "contents" key added, which map to their own contents. 

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
    proj_id = getCommitInfo(commit_id)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    foldertree = getCommitTreeWithAddons(commit_id, idInfo["email"])
    return {
            "success":True,
            "reason": "",
            "body":foldertree
            }

@app.route('/api/Commit/<proj_id>/workingCommit', methods = ["GET"])
def getUserWorkingCommitForProject(proj_id):
    """
    
    ``GET /api/Commit/<proj_id>/workingCommit``

    **Explanation:**
        Gets information about the user's (derived from credentials in Authorization headers) working commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): id of the project

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): A Commit object in the form of a dict

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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    commit = getUserWorkingCommitInProject(proj_id, idInfo["email"])

    if commit == None:
        return {
            "success": False,
            "reason": "no working commit"
        }

    return {
        "success": True,
        "reason": "",
        "body": commit
    }


@app.route('/api/Commit/<proj_id>/getLatestComments/', methods=["GET"])
def getAllLatestCommitComments(proj_id):
    """
    
    ``GET /api/Commit/<proj_id>/getLatestComments/``

    **Explanation:**
        Gets all comments associated with snapshots that are associated with the latest committed commit of the project. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): id of the project

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): A list of unresolved Comment objects in the form of dicts

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
    last_commit = getProjectLastCommittedCommit(proj_id)
    if last_commit == None:
        return {"success":False, "reason":"no commit?"}
    docsnap = getAllCommitDocumentSnapshotRelation(last_commit["commit_id"])
    allcomments = []
    with engine.connect() as conn:
        for doc in docsnap.keys():
            stmt = select(models.Comment).where(
                    models.Comment.snapshot_id == docsnap[doc],
                    models.Comment.is_resolved == False
                    )
            comments = conn.execute(stmt)
            for comment in comments:
                allcomments.append(comment._asdict())         
        
    return {"success": True, "reason":"", "body": allcomments}
