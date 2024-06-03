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
    """
    ``GET /api/Project/<proj_id>/``

    **Explanation:**
        Gets information about the project of the id.

    **Args:**
        - proj_id (int): Id of the project you're getting

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): A Project object in the form of a dict

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
    """
    ``POST /api/Project/createProject/``

    **Explanation:**
        Creates a project.

    **Args:**
        - request.body (dict):
            - project_name (str): The name of the project

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (int): the id of the newly created project

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
    """
    ``DELETE /api/Project/<proj_id>/``

    **Explanation:**
        Deletes a project

    **Args:**
        - proj_id (int): id of the project you're deleting

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Whether or not the request succeeded
            - reason (str): If the request failed, the error

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
    
    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
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
    """
    ``POST /api/Project/<proj_id>/rename/``

    **Explanation:**
        Renames a project

    **Args:**
        - proj_id (int): id of the project you're renaming
        - request.body (dict):
            - proj_name (str): new name for the project

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
    """
    ``GET /api/Project/<proj_id>/GetCommits/``

    **Explanation:**
        Get all of the project's committed commits

    **Args:**
        - proj_id (int): id of the project

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): A list of Commit objects as dicts

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

    arrayOfCommits = getAllCommittedProjectCommitsInOrder(proj_id)
    workingCommit = getUserWorkingCommitInProject(proj_id, idInfo["email"])
    if workingCommit != None:
        arrayOfCommits.append(workingCommit)
    return {
        "success": True,
        "reason": "",
        "body": arrayOfCommits
    }

@app.route('/api/Project/<proj_id>/GetLatestCommit/', methods = ["GET"])
def getProjectLatestCommit(proj_id):
    """
    TODO: Documentation
    
    ``GET /api/Project/<proj_id>/GetLatestCommit/``

    **Explanation:**
        Get the latest committed commit of the project

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
