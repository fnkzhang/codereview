from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.miscUtils import *
from utils.userAndPermissionsUtils import *
from utils.projectUtils import *

# Return body has array of project Data
# Array can contain -1 value indicating missing references
@app.route('/api/User/Project/', methods = ["GET"])
def getAllUserProjects():
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

    """
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
                "success": False,
                "reason": "Invalid Token Provided"
        }

    idInfo = authenticate()
    if idInfo is None:
        return {
            "success": False,
            "reason": "Failed to Authenticate"
        }
    allPermissions = getAllUserProjPermissionsForUser(idInfo["email"])
    if allPermissions == -1:
        return {"projects": None}
    projects = []

    for permission in allPermissions:
        projects.append(getProjectInfo(permission["proj_id"]))

    return {
        "success": True,
        "reason": "",
        "body": projects
        }

#needs sections in body
    #credentials (of user that already has access to project)
    #email (user to add to project)
    #role (role name)
    #permissions (integer that represents perms)
@app.route('/api/Project/<proj_id>/addUser/', methods=["POST"])
def addUser(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

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
    permissions = getUserProjPermissions(idInfo["email"], proj_id)
    if(permissions < 3 or inputBody["permissions"] > getUserProjPermissions(idInfo["email"], proj_id)):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    if (inputBody["permissions"] == 5):
        return {"success": False, "reason":"Cannot add another Owner", "body":{}}
    if (permissions < 0):
        return {"success": False, "reason":"Invalid Permission Level", "body":{}}
    if inputBody["email"] == idInfo["email"]:
        return {"success": False, "reason":"Can't give yourself perms", "body":{}}
    return {"success": setUserProjPermissions(inputBody["email"], proj_id, inputBody["role"], inputBody["permissions"]), "reason":"N/A", "body": {}}

#needs sections in body
    #credentials (of user that already has access to project)
    #email (user to make owner)
@app.route('/api/Project/<proj_id>/transferOwnership/', methods=["POST"])
def transferProjectOwnership(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    return {"success": changeProjectOwner(inputBody["email"], proj_id), "reason":"N/A", "body": {}}

#copies all permissions from one project to this one
@app.route('/api/Project/<old_proj_id>/<new_proj_id>/importPermissions/', methods = ["POST"])
def importPermissions(old_proj_id, new_proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

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
    permissions = getUserProjPermissions(idInfo["email"], old_proj_id)
    if(permissions < 3):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    projowner = getProjectInfo(new_proj_id)["author_email"]
    projpermissions = getAllUserProjPermissionsForProject(old_proj_id)
    addedUsers = []
    for permission in projpermissions:
        if permission["permissions"] == 5 and permission["user_email"] != projowner:
            setUserProjPermissions(permission["user_email"], new_proj_id, "Editor", 3)
        else:
            setUserProjPermissions(permission["user_email"], new_proj_id, permission["role"], permission["permissions"])
        addedUsers.append(permission["user_email"])
    return {"success": True, "reason":"", "body":addedUsers}

#just addUser but you don't need to be a valid user lol, test function remove later
#still needs:
    #email (user to add to project)
    #role (role name)
    #permissions( integer that represents perms, so far anything greater than 0 is everything)
@app.route('/api/Project/<proj_id>/addUserAdmin/', methods=["POST"])
def addUserAdmin(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

    """
    inputBody = request.get_json()
    return {"success": setUserProjPermissions(inputBody["email"], proj_id, inputBody["role"], inputBody["permissions"]), "reason":"N/A", "body": {}}

#have email in body in "email"
@app.route('/api/Project/<proj_id>/removeUser/', methods=["DELETE"])
def removeUser(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

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
        permissions = getUserProjPermissions(idInfo["email"], proj_id)
        if(permissions < 3 or getUserProjPermissions(inputBody["email"], proj_id) > getUserProjPermissions(idInfo["email"], proj_id)):

            return {"success": False, "reason":"Invalid Permissions", "body":{}}
        if (getUserProjPermissions(inputBody["email"], proj_id) == 5):
            return {"success": False, "reason":"Cannot remove Owner", "body":{}}
        deleteUser(inputBody["email"], proj_id)
        return {"success": True, "reason":"N/A", "body": {}}

    except Exception as e:
            print("Error: ", e)
            return {
                "success": False,
                "reason": str(e)
            }

@app.route('/api/Project/<proj_id>/Users/', methods=["GET"])
def getUsersWithAccessToProject(proj_id):
    """
    TODO: Documentation
    
    ``<POST/GET/UPDATE/DELETE> /api``

    **Explanation:**
        <insert_explanation_here>

    **Args:**
        - route_params (<param_type>): description
        - request.body (dict):
            - body_params (<param_type>): description

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): description
            - reason (str): description
            - body (<body_type>): <body_contents>

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
        # Get All Users Data that Has Relationship to project id
        with engine.connect() as conn:
            emailsWithAccessToProjectStmt = select(models.UserProjectRelation.user_email, models.UserProjectRelation.role, models.UserProjectRelation.permissions).where(
                models.UserProjectRelation.proj_id == proj_id
            )

            userEmailResult = conn.execute(emailsWithAccessToProjectStmt)

            userDataList = []

            for userEmailTuple in userEmailResult:
                userEmail = userEmailTuple[0]
                userRole = userEmailTuple[1]
                userPermissionLevel = userEmailTuple[2]

                getUserDataStmt = select(models.User).where(models.User.user_email == userEmail)
                userSearchResult = conn.execute(getUserDataStmt).first()

                # Add User Role To Return Data
                returnDict = userSearchResult._asdict()
                returnDict["userRole"] = userRole
                returnDict["userPermissionLevel"] = userPermissionLevel
                userDataList.append(returnDict)

            conn.commit()

            return {
                "success": True,
                "reason": "",
                "body": userDataList
            }

    except Exception as e:
            print("Error: ", e)
            return {
                "success": False,
                "reason": str(e)
            }

