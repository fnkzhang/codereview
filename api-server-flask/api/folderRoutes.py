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

