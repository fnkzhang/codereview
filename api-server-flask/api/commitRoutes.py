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
    info = getCommitInfo(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": info
    }

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
#will fail if user already has a working non-committed commit
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
    setCommitReviewed(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

#checks if there are commits newer than the user's current working commit
@app.route('/api/Commit/<proj_id>/checkIfNewer/', methods = ["GET"])
def checkIfNewerCommitExists(proj_id):
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
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    workingCommit = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    if workingCommit == None:
        return {"success": False, "reason":"no working commit", "body":{}}
    newestCommit = getProjectLastCommittedCommit(proj_id)
    success = datetime.fromisoformat(workingCommit["date_created"]) > datetime.fromisoformat(newestCommit["date_committed"])
    return {"success": True, "reason":"", "body":success}

@app.route('/api/Commit/<commit_id1>/<commit_id2>/getDiff', methods = ["GET"])
def getCommitDifferences(commit_id1, commit_id2):
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
    proj_id = getCommitInfo(commit_id1)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    commit1Uniques, commit2Uniques = getCommitLocationDifferencesUtil(commit_id1, commit_id2)
    commit1snaps, commit2snaps = getCommitDiffSnapshotsUtil(commit_id1, commit_id2)
    return {"success":True, "reason":"", "body": {"commit1UniqueItems":commit1Uniques, "commit2UniqueItems":commit2Uniques, "snapshotDiffs": {"commit1":commit1snaps, "commit2":commit2snaps}}}


#will also compare commit_id2 snapshots to commit_id1's last commit and remove those
@app.route('/api/Commit/<commit_id1>/<commit_id2>/getDiff', methods = ["GET"])
def getCommitDiffCareAboutLast(commit_id1, commit_id2):
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
    proj_id = getCommitInfo(commit_id1)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    commit1Uniques, commit2Uniques = getCommitLocationDifferencesUtil(commit_id1, commit_id2)
    commit1snaps, commit2snaps = getCommitNewerSnapshotsUtil(commit_id1, commit_id2)
    return {"success":True, "reason":"", "body": {"commit1UniqueItems":commit1Uniques, "commit2UniqueItems":commit2Uniques, "snapshotDiffs": {"commit1":commit1snaps, "commit2":commit2snaps}}}

#mainly to add stuff from other commits during merge
#can also be used to update location/snapshots from them ig
#likely used with getcommitdifferences to get uniques from a commit
#will update dst commit creation time so it doesn't conflict with the same src commit?

#will copy location and names from src commit if new, pending change->will keep name & location if only updating snapshot
#in body requires a list labeled "items"
    #list of item_ids to add to the commit, both folders and documents
    #documents will have the snapshot that is in the src commit
#send empty dict/list if there are no updates/creations/deletions
@app.route('/api/Commit/<dst_commit_id>/<src_commit_id>/bulkAdd/', methods = ["POST"])
def bulkAddToCommit(dst_commit_id, src_commit_id):
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
    proj_id = getCommitInfo(dst_commit_id)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if getUserWorkingCommitInProject(proj_id, idInfo["email"]) != None:
        return {"success": False, "reason":"Working Commit Already Exists For User", "body":{}}
    itemsIds = body["items"]
    for itemId in itemsIds:
        item = getItemCommitLocation(itemId, src_commit_id)
        createItemCommitLocation(itemId, dst_commit_id, item["parent_folder"], item["is_folder"])
        if item["is_folder"] == False:
            commitDocSnap = getCommitDocumentSnapshot(itemId, src_commit_id)
            addSnapshotToCommit(commitDocSnap["snapshot_id"], itemId, dst_commit_id)
    return {"success":True, "reason":""}

#put ids of things to delete in "items"
@app.route('/api/Commit/<commit_id>/bulkDelete/', methods = ["DELETE"])
def bulkDeleteFromCommit(commit_id):
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
    proj_id = getCommitInfo(commit_id)["proj_id"]
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if getUserWorkingCommitInProject(proj_id, idInfo["email"]) != None:
        return {"success": False, "reason":"Working Commit Already Exists For User", "body":{}}
    itemsIds = body["items"]
    for itemId in itemsIds:
        item = getItemCommitLocation(itemId, commit_id)
        if item["is_folder"] == False:
            deleteDocumentFromCommit(itemId, commit_id)
        else:
            deleteFolderFromCommit(itemId, commit_id)
    return {"success":True, "reason":""}

#no checks will just commit
#in body: requires commit name in "name"
@app.route('/api/Commit/<commit_id>/commitCommit/', methods = ["POST"])
def commitCommit(commit_id):
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

    # After User Commits to public, commit should be open
    setCommitOpen(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }

@app.route('/api/Commit/<commit_id>/close/', methods=["GET"])
def closeCommit(commit_id):
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
    
    closeCommit(commit_id)

    return {
        "success": True,
        "reason": "",
        "body": commit_id
    }


#probably used if someone is halfway through a commit and wants to kill it
@app.route('/api/Commit/<proj_id>/workingCommit/', methods=["DELETE"])
def deleteWorkingCommit(proj_id):
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

    foldertree = getCommitTreeWithSeen(commit_id, idInfo["email"])
    return {
            "success":True,
            "reason": "",
            "body":foldertree
            }

@app.route('/api/Commit/<proj_id>/workingCommit', methods = ["GET"])
def getUserWorkingCommitForProject(proj_id):
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

