from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *

from utils.folderUtils import *
from utils.documentUtils import *
from utils.miscUtils import *
from utils.userAndPermissionsUtils import *

import models

#see documentroutes about commit_id, should be pretty obvious tbh
@app.route('/api/Folder/<proj_id>/<folder_id>/<commit_id>/', methods=["GET"])
def getFolder(proj_id, folder_id, commit_id):
    """
    ``GET /api/Folder/<proj_id>/<folder_id>/<commit_id>/``

    **Explanation:**
        Gets folder information from the given commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (str): folder you're moving
        - folder_id (str): project this folder is in
        - commit_id (str): commit this action is taking place on

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (dict): Information about the folder if successful.

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
    info = getFolderInfo(folder_id, commit_id)
    return {
        "success": True,
        "reason": "",
        "body": info
        }

#requires
    #authentication stuff
#needs in body
    #folder name
    #parent_folder
@app.route('/api/Folder/<proj_id>/<commit_id>/', methods=["POST"])
def createFolder(proj_id, commit_id):
    """
    ``POST /api/Folder/<proj_id>/<commit_id>/``

    **Explanation:**
        Creates a folder in a project's commit with the given name and parent folder. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (str): project you're making the folder in
        - commit_id (str): commit this action is taking place on
        - request.body (dict):
            - folder_name (str): name of the folder
            - parent_folder (str): folder you're making it in

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (str): Identifier of the created folder if successful.

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

    folder_id = createNewFolder(inputBody["folder_name"], inputBody["parent_folder"], proj_id, commit_id)
    return {
        "success": True,
        "reason": "",
        "body": folder_id
    }

@app.route('/api/Folder/<folder_id>/<commit_id>/', methods=["DELETE"])
def deleteFolder(folder_id, commit_id):
    """
    ``DELETE /api/Folder/<folder_id>/<commit_id>/``

    **Explanation:**
        Deletes the folder from the commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - folder_id (str): folder you’re deleting
        - commit_id (str): commit this action is taking place on

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
        proj_id = getFolderInfo(folder_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    rv, e = deleteFolderFromCommit(folder_id, commit_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

#body: put new name in "folder_name"
@app.route('/api/Folder/<folder_id>/<commit_id>/rename/', methods=["POST"])
def renameFolder(folder_id, commit_id):
    """
    ``POST /api/Folder/<folder_id>/<commit_id>/rename/``

    **Explanation:**
        Renames the folder from the commit. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - folder_id (str): folder you’re renaming
        - commit_id (str): commit this action is taking place on
        - request.body (dict):
            - folder_name (str): new name for folder

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
        proj_id = getFolderInfo(folder_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    body = request.get_json()
    rv, e = renameItem(folder_id, body["folder_name"], commit_id)
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
@app.route('/api/Folder/<folder_id>/<commit_id>/move/', methods=["POST"])
def moveFolder(folder_id, commit_id):
    """
    ``POST /api/Folder/<folder_id>/<commit_id>/move/``

    **Explanation:**
        This endpoint moves a folder within a project's commit to another folder. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - folder_id (str): folder you're moving
        - commit_id (str): commit this action is taking place on
        - request.body (dict):
            - parent_folder (str): folder you're moving it to

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.

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
        proj_id = getFolderInfo(folder_id, commit_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    parent_folder = inputBody["parent_folder"]
    if not moveItem(folder_id, parent_folder, commit_id):
        return {"success": False,
                "reason":"invalid document"
                }
    return {
        "success": True,
        "reason": "",
        "body": ""
    }

