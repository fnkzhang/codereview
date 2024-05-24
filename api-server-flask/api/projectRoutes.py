from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.projectUtils import *
from utils.documentUtils import *
from utils.folderUtils import *
from utils.miscUtils import *
from utils.userAndPermissionsUtils import *

import models

@app.route('/api/Project/<proj_id>/', methods = ["GET"])
def getProject(proj_id):
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
    projectData = getProjectInfo(proj_id)

    if projectData == None:
        return {
            "success": False,
            "reason": "Could Not Get project"
        }

    return {
        "success": True,
        "reason": "",
        "body": projectData
    }

#put project name in body in "project_name"
@app.route('/api/Project/createProject/', methods = ["POST"])
def createProject():
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
    pid = createNewProject(body["project_name"], idInfo["email"])
    commit_id = createNewCommit(pid, idInfo["email"], None)
    commitACommit(commit_id, "Base Commit")
    return {
        "success": True,
        "reason": "",
        "body": pid
    }

@app.route('/api/Project/<proj_id>/', methods=["DELETE"])
def deleteProject(proj_id):
    # Authentication
    headers = request.headers
    '''
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
    '''
    #if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
    #    return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = purgeProjectUtil(proj_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

#body: put new name in "proj_name"
@app.route('/api/Project/<proj_id>/rename/', methods=["POST"])
def renameProject(proj_id):
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
        proj_id = getProjectInfo(proj_id)
    except:
        return {
            "success": False,
            "reason": "project doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    body = request.get_json()
    rv, e = renameProjectUtil(proj_id, body["proj_name"])
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Rename"
    }

@app.route('/api/Project/<proj_id>/GetCommits/', methods = ["GET"])
def getProjectCommittedCommits(proj_id):
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

    arrayOfCommits = getAllCommittedProjectCommitsInOrder(proj_id)
    workingCommit = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    if workingCommit != None:
        arrayOfCommits.append(workingCommit)
    for commit in arrayOfCommits:
        docsnap = getAllCommitDocumentSnapshotRelation(commit["commit_id"])
        for doc in docsnap.keys():
            commit["seenSnapshot"] = isSnaphotSeenByUser(docsnap[doc], idInfo["email"])
            commit["seenComments"] = isSnapshotAllCommentSeenByUser(docsnap[doc], idInfo["email"])
    return {
        "success": True,
        "reason": "",
        "body": arrayOfCommits
    }

@app.route('/api/Project/<proj_id>/GetLatestCommit/', methods = ["GET"])
def getProjectLatestCommit(proj_id):
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

    latestCommit = getProjectLastCommittedCommit(proj_id)

    if latestCommit == None:
        return {
            "success": False,
            "reason": "No Latest Commit"
        }
    
    return {
        "success": True,
        "reason": "",
        "body": latestCommit
    }
#discontinued for now
@app.route('/api/Project/<proj_id>/GetDocuments/', methods = ["GET"])
def getProjectDocuments(proj_id):
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


    arrayOfDocuments = getAllProjectDocuments(proj_id)
    return {
        "success": True,
        "reason": "",
        "body": arrayOfDocuments
    }

