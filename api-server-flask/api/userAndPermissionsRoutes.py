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
    
    ``GET /api/User/Project/``

    **Explanation:**
        Gets all projects the user has access to

    **Args:**
        Requires credentials of the user in the Authorization header

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): List of the projects as dicts
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
    #email (user to add to project)
    #role (role name)
    #permissions (integer that represents perms)
@app.route('/api/Project/<proj_id>/addUser/', methods=["POST"])
def addUser(proj_id):
    """
    ``POST /api/Project/<proj_id>/addUser/``

    **Explanation:**
        Adds a user to a project with the given permission level. Will update the permission level if they are already on the project. Enforces permissions through credentials given in Authorization header. User's permissions must be higher than or equal the level they are giving

    **Args:**
        - proj_id (int): the id of the project
        - request.body (dict):
            - email (str): email of the user being added
            - role (str): name of the role they're being given
            - permissions (int): level of permissions they're being given

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
    if getUserInfo(inputBody["email"] == None):
        return {
            "success":False,
            "reason": "Not a valid user"
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
    return {"success": setUserProjPermissions(inputBody["email"], proj_id, inputBody["role"], inputBody["permissions"]), "reason":"N/A"}

#needs sections in body
    #email (user to make owner)
@app.route('/api/Project/<proj_id>/transferOwnership/', methods=["POST"])
def transferProjectOwnership(proj_id):
    """
    ``POST /api/Project/<proj_id>/transferOwnership/``

    **Explanation:**
        Transfers ownership to the given user. Enforces permissions through credentials given in Authorization header. User must be owner already
    
    **Args:**
        - proj_id (int): the id of the project
        - request.body (dict):
            - email (str): email of the user being added

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
    if getUserInfo(inputBody["email"]) == None:
        return {
            "success":False,
            "reason": "Invalid User"
        }
    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    return {"success": changeProjectOwner(inputBody["email"], proj_id), "reason":"N/A"}

#have email in body in "email"
@app.route('/api/Project/<proj_id>/removeUser/', methods=["DELETE"])
def removeUser(proj_id):
    """
    ``DELETE /api/Project/<proj_id>/removeUser/``

    **Explanation:**
        Removes a user from the project. Enforces permissions through credentials given in Authorization header.

    **Args:**
        - proj_id (int): the id of the project
        - request.body (dict):
            - email (str): email of the user being added

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
    ``GET /api/Project/<proj_id>/Users/``

    **Explanation:**
        Gets all users that have access to the project

    **Args:**
        - proj_id (int): the id of the project

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the operation was successful.
            - reason (str): Description of the success or failure reason.
            - body (list): List of the users as dicts
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
                if userSearchResult == None:
                    returnDict = {}
                    returnDict["user_email"] = userEmail
                    returnDict["name"] = "Unknown Name"
                    returnDict["date_joined"] = None
                    returnDict["github_token"] = None
                else:
                    returnDict = userSearchResult._asdict()
                    returnDict.pop("github_token")
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

