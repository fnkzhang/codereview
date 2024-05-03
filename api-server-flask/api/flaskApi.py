from flask import Flask, request, jsonify
app = Flask(__name__)

from flask_cors import CORS
CORS(app)

try:
    from testRoutes import createTable, dropUserProjectRelationTable, \
        testInsert, grabData, sendData
except:
    pass

from cloudSql import connectCloudSql
from utils import *
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import sessionmaker
import models

from utils import engine
from llm import init_llm, get_llm_code_from_suggestion, get_llm_suggestion_from_code

Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html

init_llm()
# Remove Later for testing
@app.route('/createTable')
def createTable():
    engine = connectCloudSql()
    
    models.Comment.metadata = models.Base.metadata

    models.Comment.metadata.create_all(engine)
    models.User.metadata = models.Base.metadata
    models.User.metadata.create_all(engine)
    models.UserProjectRelation.metadata = models.Base.metadata
    models.UserProjectRelation.metadata.create_all(engine)
    #metaData.create_all(engine)
    print("Table was created")
    return "Created Table"

@app.after_request
def afterRequest(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/user/authenticate', methods=["POST"])
def authenticator():
    idInfo = authenticate()
    if idInfo is not None:
        print("Success?")
        # RETURN User Data back
        return jsonify({
            "success": True,
            "reason": "N/A",
            "body": idInfo
        })
    
    return jsonify({
        "success": False,
        "reason": "FAILED TO AUTHENTICATE LOGIN FROM GOOGLE",
        "body": {}
    })

def authenticate():
    headers = request.headers
    if (not isValidRequest(headers, ["Authorization"])):
        return None
    try:
        idInfo = id_token.verify_oauth2_token(
            headers["Authorization"],
            requests.Request(),
            CLIENT_ID
        )
        return idInfo

    except ValueError:
        return None

@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test"

# Might need to reformat this function
@app.route('/api/user/isValidUser', methods=["POST"])
def checkIsValidUser():
    headers = request.headers

    if (not isValidRequest(headers, ["Authorization"])):
        return {
                "success": False,
                "reason": "Invalid Token Provided"
        }
    
    if (not isValidRequest(headers, ["Email"])):
        return {
            "success": False,
            "reason": "Invalid Header Provided"
        }
    
    user = userExists(headers["Email"])

    if (not user):
        return {
            "success": False,
            "reason": "User Does not exist"
        }
    
    return {
        "success": True,
        "reason": "",
        "body": {}
    }

    pass
#literally just authenticate but it adds a user to the database.
#needs sections:
    #credentials
@app.route('/api/user/signup/', methods = ["POST"])
def signUp():
    headers = request.headers
    if (not isValidRequest(headers, ["Authorization"])):
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

    if userExists(idInfo["email"]):
        retData = {
                "success": False,
                "reason": "Account already exists",
                "body":{}
        }
        return jsonify(retData)

    with engine.connect() as conn:
        stmt = insert(models.User).values(
            user_email = idInfo["email"],
            name = idInfo["name"]
        )
        conn.execute(stmt)
        conn.commit()
    retData = {
            "success":True,
            "reason": "N/A",
            "body": idInfo
    }
    return jsonify(retData)

# Return body has array of project Data
# Array can contain -1 value indicating missing references
@app.route('/api/User/<user_email>/Project/', methods = ["GET"])
def getAllUserProjects(user_email):
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
    if idInfo["email"] != user_email:
        return {
            "success": False,
            "reason": "User does not match email"
            }
    allPermissions = getAllUserProjPermissions(user_email)
    if allPermissions == -1:
        return {"projects": "None"}
    projects = []

    for permission in allPermissions:
        projects.append(getProjectInfo(permission["proj_id"]))

    return {
        "success": True,
        "reason": "",
        "body": projects
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
    return {
        "success": True,
        "reason": "",
        "body": pid
    }

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

    if authenticate() is None:
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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
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


@app.route('/api/Document/<proj_id>/GetDocuments/', methods = ["GET"])
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
#requires
    #authentication stuff
#needs in body
    #folder name
    #parent_folder
@app.route('/api/Folder/<proj_id>/', methods=["POST"])
def createFolder(proj_id):
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
    
    folder_id = createNewFolder(inputBody["folder_name"], inputBody["parent_folder"], proj_id)
    return {
        "success": True,
        "reason": "",
        "body": folder_id
    }

@app.route('/api/Folder/<proj_id>/<folder_id>/', methods=["GET"])
def getFolder(proj_id, folder_id):
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
    info = getFolderInfo(folder_id)
    return {
        "success": True,
        "reason": "",
        "body": info
        }

#needs sections in body
    #credentials (of user that already has access to project)
    #email (user to add to project)
    #role (role name)
    #permissions (integer that represents perms)
@app.route('/api/Project/<proj_id>/addUser/', methods=["POST"])
def addUser(proj_id):
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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 3 or body["permissions"] > getUserProjPermissions(idInfo["email"], proj_id)):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    with engine.connect() as conn:
        if(getUserProjPermissions(inputBody["email"], proj_id)) < 0:
            relationstmt = insert(models.UserProjectRelation).values(
                    user_email = inputBody["email"],
                    proj_id = proj_id,
                    role = inputBody["role"],
                    permissions = inputBody["permissions"]
            )
        else:
            relationstmt = update(models.UserProjectRelation).where(
                models.UserProjectRelation.user_email == inputBody["email"],
                models.UserProjectRelation.proj_id == proj_id
            ).values(
                role = inputBody["role"],
                permissions = inputBody["permissions"]
            )
        conn.execute(relationstmt)
        conn.commit()
    return {"success": True, "reason":"N/A", "body": {}}

#just addUser but you don't need to be a valid user lol, test function remove later
#still needs:
    #email (user to add to project)
    #role (role name)
    #permissions( integer that represents perms, so far anything greater than 0 is everything)
@app.route('/api/Project/<proj_id>/addUserAdmin/', methods=["POST"])
def addUserAdmin(proj_id):
    inputBody = request.get_json()
    with engine.connect() as conn:
        if(getUserProjPermissions(inputBody["email"], proj_id)) < 0:
            relationstmt = insert(models.UserProjectRelation).values(
                    user_email = inputBody["email"],
                    proj_id = proj_id,
                    role = inputBody["role"],
                    permissions = inputBody["permissions"]
            )
        else:
            relationstmt = update(models.UserProjectRelation).where(
                models.UserProjectRelation.user_email == inputBody["email"],
                proj_id == proj_id
            ).values(
                role = inputBody["role"],
                permissions = inputBody["permissions"]
            )

        conn.execute(relationstmt)
        conn.commit()
    return {"success": True, "reason":"N/A", "body": {}}

@app.route('/api/Project/<proj_id>/removeUser/', methods=["POST"])
def removeUser(proj_id):
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

    #3 is placeholder value since we only have read permission
    if(getUserProjPermissions(idInfo["email"], proj_id) < 3):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    with engine.connect() as conn:
        relationstmt = delete(models.UserProjectRelation).where(
            models.UserProjectRelation.user_email == inputBody["email"],
            proj_id == proj_id
        )
        conn.execute(relationstmt)
        conn.commit()
    return {"success": True, "reason":"N/A", "body": {}}

@app.route('/api/Snapshot/<proj_id>/<doc_id>/', methods=["POST"])
def createSnapshot(proj_id, doc_id):
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
    snapshot_id = createNewSnapshot(proj_id, doc_id, inputBody["data"])
    return {
        "success": True,
        "reason": "",
        "body": snapshot_id
    }

@app.route('/api/Snapshot/<proj_id>/<doc_id>/<snapshot_id>/', methods=["GET"])
def getSnapshot(proj_id, doc_id, snapshot_id):
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
    blob = fetchFromCloudStorage(f"{proj_id}/{doc_id}/{snapshot_id}")
    return {
        "success": True,
        "reason": "",
        "body": blob
    }


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

    #requires
    #credentials in headers
    #In body:
    #parent_folder (folder you're moving it to
@app.route('/api/Folder/<folder_id>/move/', methods=["POST"])
def moveFolder(folder_id):
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
        proj_id = getFolderInfo(folder_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    parent_folder = inputBody["parent_folder"]
    if not moveFolderUtil(folder_id, parent_folder):
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

@app.route('/api/Snapshot/<snapshot_id>/', methods=["DELETE"])
def deleteSnapshot(snapshot_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = deleteSnapshotUtil(snapshot_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
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

    if authenticate() is None:
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

    if authenticate() is None:
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

@app.route('/api/Folder/<folder_id>/', methods=["DELETE"])
def deleteFolder(folder_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    try:
        proj_id = getFolderInfo(folder_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    rv, e = deleteFolderUtil(folder_id)
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
@app.route('/api/Folder/<folder_id>/rename/', methods=["POST"])
def renameFolder(folder_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    try:
        proj_id = getFolderInfo(folder_id)["associated_proj_id"]
    except:
        return {
            "success": False,
            "reason": "folder doesn't exist"
        }

    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    rv, e = renameFolderUtil(folder_id, body["folder_name"])
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Rename"
    }

@app.route('/api/Project/<proj_id>/', methods=["DELETE"])
def deleteProject(proj_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    if(getUserProjPermissions(idInfo["email"], proj_id) < 5):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    # Query
    rv, e = deleteProjectUtil(proj_id)
    if(not rv):
        return {
            "success": False,
            "reason": str(e)
        }

    return {
        "success": True,
        "reason": "Successful Delete"
    }

@app.route('/api/Snapshot/<snapshot_id>/comment/create', methods=["POST"])
def createComment(snapshot_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }

    body = request.get_json()
    if not isValidRequest(body, ["author_email", "reply_to_id", "content"]):
        return {
            "success": False,
            "reason": "Invalid Request"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    with Session() as session:
        try:
            session.add(models.Comment(
                snapshot_id = snapshot_id,
                author_email = body["author_email"],
                reply_to_id = int(body["reply_to_id"]),
                content = body["content"],
                highlight_start_x = int(body["highlight_start_x"]),
                highlight_start_y = int(body["highlight_start_y"]),
                highlight_end_x = int(body["highlight_end_x"]),
                highlight_end_y = int(body["highlight_end_y"]),
                is_resolved = body["is_resolved"]

            ))
            session.commit()
        except Exception as e:
            print("Error: ", e)
            return {
                "success": False,
                "reason": str(e)
            }

    print("Successful Write Comment")
    return {
        "success": True,
        "reason": "Successful Write",
        "body": {
            "snapshot_id": snapshot_id,
            "author_email": body["author_email"],
            "reply_to_id": int(body["reply_to_id"]),
            "content": body["content"],
            "highlight_start_x": int(body["highlight_start_x"]),
            "highlight_start_y": int(body["highlight_start_y"]),
            "highlight_end_x":int(body["highlight_end_x"]),
            "highlight_end_y": int(body["highlight_end_y"]),
            "is_resolved": body["is_resolved"]
        }
    }

# Set comment is_resolved to true
@app.route('/api/comment/<comment_id>/resolve', methods=["PUT"])
def resolveComment(comment_id):
    # Authentication
    print("TEST")
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getCommentProject(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1 or getProjectInfo(proj_id)["author_email"] != idInfo["email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    resolveCommentHelperFunction(comment_id)

    return {
        "success": True,
        "reason": "Ran The Call"
    }
    # Set Comment is_resolved to true
    
    pass
# look into pagination
# https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/api/#flask_sqlalchemy.SQLAlchemy.paginate
@app.route('/api/Snapshot/<snapshot_id>/comments/get', methods=["GET"])
def getCommentsOnSnapshot(snapshot_id):

    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    commentsList = filterCommentsByPredicate(models.Comment.snapshot_id == snapshot_id)
    if commentsList is None:
        return {
            "success": False,
            "reason": "Error Grabbing Comments From Database"
        }
    
    print("Successful Read")
    return {
        "success": True,
        "reason": "",
        "body": commentsList
    }

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

# Comment POST, GET, PUT, DELETE
@app.route('/api/comments/<comment_id>/subcomments/get', methods=["GET"])
def getSubcommentsOnComment(comment_id):
    # authenticate
    # query cloud sql
    proj_id = getCommentProject(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # temporary
    retArray = []
    for i in range(5):
        d = {
            "subcomment_id": i + 1,
            "comment_id": comment_id,
            "author_id": 2000 + i,
            "date_created": "2024-02-20 12:00:00",
            "date_modified": "2024-02-20 12:00:00",
            "content": f"Fake subcomment {i+1} on comment {comment_id}"
        }
        retArray.append(d)
    
    return retArray

@app.route('/api/comments/<comment_id>/edit', methods=["PUT"])
def editComment(comment_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }

    body = request.get_json()
    if not isValidRequest(body, ["content"]):
        return {
            "success": False,
            "reason": "Invalid Request"
        }
    proj_id = getCommentProject(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1 or getCommentInfo(comment_id)["author_email"] != idInfo["email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    # Query
    try:
        with Session() as session:
            session.query(models.Comment) \
                .filter_by(comment_id=comment_id) \
                .update({
                    "date_modified": getTime(),
                    "content": body["content"]
                })

            session.commit()
    except Exception as e:
        print("Error: ", e)
        return {
            "success": False,
            "reason": str(e)
        }
    
    print("Successful Edit")
    return {
        "success": True,
        "reason": "Successful Edit"
    }

@app.route('/api/comments/<comment_id>/delete', methods=["DELETE"])
def deleteComment(comment_id):
    # Authentication
    headers = request.headers
    if not isValidRequest(headers, ["Authorization"]):
        return {
            "success": False,
            "reason": "Invalid Token Provided"
        }

    if authenticate() is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    proj_id = getCommentProject(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1 or getCommentInfo(comment_id)["author_email"] != idInfo["email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
 
    # Query
    try:
        with Session() as session:
            session.query(models.Comment) \
                .filter_by(comment_id=comment_id) \
                .delete()

            session.commit()
    except Exception as e:
        print("Error: ", e)
        return {
            "success": False,
            "reason": str(e)
        }
    
    print("Successful Delete")
    return {
        "success": True,
        "reason": "Successful Delete"
    }
#checks whether authenticated user has github connected
@app.route('/api/Github/userHasGithub/', methods = ["GET"])
def getUserGithubStatus():
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
    user = getUserInfo(idInfo["email"])
    if user == None:
        return {"success":False, "reason":"User does not exist"}
    return {"success:":True, "reason":"", "body": user["github_token"] != None}
#needs auth because everything does lmao
#put code in the body in "github_code"
@app.route('/api/Github/addToken', methods=["POST"])
def addGithubToken():
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
    code = body["github_code"]
    token = gapp.get_access_token(code)
    with engine.connect() as conn:
        stmt = update(models.User).where(models.User.user_email == idInfo["email"]).values(github_token = token.token)
        conn.execute(stmt)
        conn.commit()
    return {"success":True,
            "reason": "",
        }

#needs auth because everything does lmao
#needs parameter, ex ..../getRepositoryBranches/?repository=fnkzhang/codereview
@app.route('/api/Github/getRepositoryBranches/', methods=["GET"])
def getGithubRepositoryBranches():
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
    repository = request.args.get("repository")
    token = getUserInfo(idInfo["email"])["github_token"]
    success, rv = getBranches(token, repository)#body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)
                }
    return {"success":True,
            "reason": "",
            "body": rv
        }

#needs auth
#body: put repository path in "repository" and branch in "branch"
#body: put project_name in "project_name"
#format -> repository = "fnkzhang/codereview", branch = "main"
@app.route('/api/Github/PullToNewProject/', methods=["POST"])
def pullToNewProject():
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
        #
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    proj_id = createNewProject(body["project_name"], idInfo["email"])
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    project = getProjectInfo(proj_id)
    pathToFolderID = {}
    pathToFolderID[""] = project["root_folder"]
    contents = repo.get_contents("", body["branch"])
    updated_files = []
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content.decode())
    return {"success":True, "reason":"", "body":proj_id}


#needs auth
#put repository path in "repository" and branch in "branch"
#format -> repository = "fnkzhang/codereview", branch = "main"
@app.route('/api/Github/<proj_id>/PullToExistingProject/', methods=["POST"])
def pullToExistingProject(proj_id):
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
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 2):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    g2 = Github(auth = Auth.Token(user["github_token"]))
    repo = g2.get_repo(body["repository"])
    project = getProjectInfo(proj_id)
    folders = getAllProjectFolders(proj_id)
    pathToFolderID = {}
    pathToFolderID[""] = project["root_folder"]
    contents = repo.get_contents("", body["branch"])
    updated_files = []
    documents = getAllProjectDocuments(proj_id)
    folders = getAllProjectFolders(proj_id)
    docs_to_delete = [document['doc_id'] for document in documents]
    folders_to_delete = [folder['folder_id'] for folder in folders]
    folders_to_delete.remove(project["root_folder"])
    while contents:
        file_content = contents.pop(0)
        index = file_content.path.rfind('/')
        if index < 0:
            path = ""
        else:
            path = file_content.path[:index]
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
            folder = getFolderInfoViaLocation(file_content.name, pathToFolderID[path])
            if folder != None:
                folder_id = folder["folder_id"]
                folders_to_delete.remove(folder_id)
            else:
                folder_id = createNewFolder(file_content.name, pathToFolderID[path], proj_id)
            pathToFolderID[file_content.path] = folder_id
        else:
            document = getDocumentInfoViaLocation(file_content.name, pathToFolderID[path])
            if document != None:
                doc_id = document["doc_id"]
                if file_content.decoded_content.decode() != getDocumentLastSnapshotContent(doc_id):
                    createNewSnapshot(proj_id, doc_id, file_content.decoded_content.decode())
                    updated_files.append(doc_id)
                docs_to_delete.remove(doc_id)
            else:
                doc_id = createNewDocument(file_content.name, pathToFolderID[path], proj_id, file_content.decoded_content.decode())
                updated_files.append(doc_id)
        print(pathToFolderID)
    for doc_to_delete in docs_to_delete:
        deleteDocumentUtil(doc_to_delete)
    for folder_to_delete in folders_to_delete:
        deleteFolderUtil(folder_to_delete)
    deleteProjectDeletedDocuments(proj_id)
    return {"success":True, "reason":"", "body":updated_files}

#needs "branch" in arguments, for example /api/Github/12345/getNonexistent/?owner_name=fnkzhang&repo_name=coderaview&branch=main
@app.route('/api/Github/<proj_id>/getNonexistent/', methods=["GET"])
def getProjectNonexistentGithubDocuments(proj_id):
    headers = request.headers
    repository = request.args.get("repository")
    branch = request.args.get("branch")
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
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    documents = getProjectNonexistentGithubDocumentsUtil(repository, branch, token, proj_id)
    return {"success":True, "reason":"", "body":documents}


#testfunctionifthatwasn'tobviousbyitsname, is currently emulating push
#put list of snapshots ID's to push in "snapshots"
#put list of paths in deletedDocuments, should just be the samae paths as received in 
#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/PushToExisting/', methods=["POST"])
def pushToExistingBranch(proj_id):
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
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    g2 = Github(auth = Auth.Token(token))
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["branch"] not in rv:
        return {"success":False,
                "reason": "branch does not exist"}
    repo = g2.get_repo(body["repository"])
    updated_files = []
    folderIDToPath = getProjectFoldersAsPaths(proj_id)
    body = request.get_json()
    snapshotIDs = body["snapshots"]
    deletedDocumentPaths = body["deletedDocuments"]
    tree_elements = assembleGithubTreeElements(deletedDocumentPaths, snapshotIDs)
    branch_sha = repo.get_branch(body["branch"]).commit.sha
    try:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            base_tree = repo.get_git_tree(sha=branch_sha)
            )
    except Exception as e:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            )
    commit = repo.create_git_commit(
        message=body["message"],
        tree = repo.get_git_tree(sha=new_tree.sha),
        parents=[repo.get_git_commit(branch_sha)],
        )
    ref = repo.get_git_ref(ref='heads/' + body["branch"])
    ref.edit(sha=commit.sha, force=True)
    commit = repo.get_branch(body["branch"]).commit
    allcomments = assembleGithubComments(snapshotIDs)
    for comment in allcomments:
        com.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}


#testfunctionifthatwasn'tobviousbyitsname, is currently emulating push
#put list of snapshots ID's to push in "snapshots"
#put list of paths in deletedDocuments, should just be the samae paths as received in 
#put repository including owner name in "repository", ex: billingtonbill12/testrepo
#put branchname in "branch"
#put branch you're building off of into "oldbranch"
#put commit message in "message", or if we eventually put a generic message that's fine
@app.route('/api/Github/<proj_id>/PushToNewBranch/', methods=["POST"])
def pushToNewBranch(proj_id):
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
        #
    if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    body = request.get_json()
    user = getUserInfo(idInfo["email"])
    token = user["github_token"]
    g2 = Github(auth = Auth.Token(token))
    success, rv = getBranches(token, body["repository"])
    if (not success):
        return {"success":False,
                "reason": str(rv)}
    if body["oldbranch"] not in rv:
        return {"success":False,
                "reason": "branch getting built off of does not exist"}
    if body["branch"] in rv:
        return {"success":False,
                "reason": "branch already exists"}
    repo = g2.get_repo(body["repository"])
    updated_files = []
    folderIDToPath = getProjectFoldersAsPaths(proj_id)
    body = request.get_json()
    snapshotIDs = body["snapshots"]
    deletedDocumentPaths = body["deletedDocuments"]
    tree_elements = assembleGithubTreeElements(deletedDocumentPaths, snapshotIDs)
    try:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            base_tree = repo.get_git_tree(sha=branch_sha)
            )
    except Exception as e:
        new_tree = repo.create_git_tree(
            tree = tree_elements,
            )
    commit = repo.create_git_commit(
        message=body["message"],
        tree = repo.get_git_tree(sha=new_tree.sha),
        parents=[repo.get_git_commit(branch_sha)],
        )
    ref = repo.create_git_ref(ref='refs/heads/' + body["branch"], sha = branch_sha)
    ref.edit(sha=commit.sha, force=True)
    commit = repo.get_branch(body["branch"]).commit
    allcomments = assembleGithubComments(snapshotIDs)
    for comment in allcomments:
        com.create_comment(body=comment)
    return {"success":True, "reason":"", "body":updated_files}

@app.route('/api/testo/', methods=["POST"])
def testo():
    '''
    user = getUserInfo("billingtonbill12@gmail.com")
    token = user["github_token"]
    g2 = Github(auth = Auth.Token(token))
    repo = g2.get_repo("billingtonbill12/testrepo")
    com = repo.get_branch("main").commit
    print(com.get_comments())
    for i in com.get_comments():
        print(i.body)
        print(i.line)
    com.create_comment(body="what was the point", path="weee/foldername123/testfile")
    com.create_comment(body="what was the point2", path="README.md")
    '''
    a = filterCommentsByPredicate(models.Comment.author_email == "sichuan@ucdavis.edu" and models.Comment.content == "Remove this")
    a = [b for b in a if b["content"] == "Remove this"]
    return {"erm":a}

@app.route('/api/Project/<proj_id>/getFolderTree/',methods=["GET"])
def getProjectFolderTree(proj_id):
    
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
    
    project = getProjectInfo(proj_id)
    foldertree = getFolderTree(project["root_folder"])
    return {
            "success":True,
            "reason": "",
            "body":foldertree
            }

# EXAMPLE:
# curl -X GET http://127.0.0.1:5000/api/llm/code-implementation -H 'Content-Type: application/json' -d '{"code": "def aTwo(num):\n    return num+2;\n\nprint(aTwo(2))", "highlighted_code": "def aTwo(num):\n    return num+2;", "comment": "change the function to snake case, add type hints, remove the unnecessary semicolon, and create a more meaningful function name that accurately describes the behavior of the function."}'

#in body:
    #highlighted_code = code that the comment highlighted
    #code = entire code
    #comment = commented text
@app.route("/api/llm/code-implementation", methods=["GET"])
def implement_code_changes_from_comment():
    data = request.get_json()
    code = data.get("code")
    highlighted_code=data.get("highlighted_code")
    comment = data.get("comment")

    response = get_llm_code_from_suggestion(
        code=code,
        highlighted_code=highlighted_code,
        suggestion=comment
    )

    if response is None:
        return {
            "success": False,
            "reason": "LLM Error"
        }

    return {
        "success": True,
        "reason": "Success",
        "body": response
    }

# EXAMPLE:
# curl -X GET http://127.0.0.1:5000/api/llm/comment-suggestion -H 'Content-Type: application/json' -d '{"code": "def calc_avg(n):\n    tot=0\n    cnt=0\n    for number in n:\n      tot = tot+ number\n      cnt= cnt+1\n    average=tot/cnt"}'
@app.route("/api/llm/comment-suggestion", methods=["GET"])
def suggest_comment_from_code():
    data = request.get_json()
    code = data.get("code")

    response = get_llm_suggestion_from_code(
        code=code
    )

    if response is None:
        return {
            "success": False,
            "reason": "LLM Error"
        }

    return {
        "success": True,
        "reason": "Success",
        "body": response
    }
