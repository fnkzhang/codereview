from cloudSql import connectCloudSql
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS

from utils import *
from diff_match_patch import diff_match_patch
from google.oauth2 import id_token
from google.auth.transport import requests

from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select, update, delete
from sqlalchemy.orm import sessionmaker

import pymysql

import models
from cloudSql import connectCloudSql

from utils import engine
from llm import init_llm, get_llm_code_from_suggestion, get_llm_suggestion_from_code

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

app = Flask(__name__)

CORS(app, headers=["Content-Type", "Authorization"])
engine = connectCloudSql()
Session = sessionmaker(engine) # https://docs.sqlalchemy.org/en/20/orm/session_basics.html

init_llm()

@app.after_request
def afterRequest(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

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

# Takes in json with "code" section
@app.route('/api/sendData', methods=["POST"])
def sendData():
    inputBody = request.get_json()

    # Check valid request json
    if "credential" not in inputBody or "code" not in inputBody:
        return { "success": False,
                "reason": "Invalid JSON Provided",
                "body": {}
        }
    
    return { "success": True,
            "reason": "N/A",
            "body": inputBody
            }

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
@app.route('/api/user/signup', methods = ["POST"])
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
            "body": {idInfo}
    }
    return jsonify(retData)

@app.route('/api/User/<user_email>/Project/', methods = ["GET"])
def getUserProjects(user_email):
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

    allPermissions = getUserProjPermissions(user_email)
    if allPermissions == -1:
        return {"projects": "None"}
    projects = []
    for permission in allPermissions:
        projects.append(getProjectInfo(permission.proj_id))
    info = json.dumps(projects)
    return {"proj_info": info}

@app.route('/api/Project/<proj_name>/', methods = ["POST"])
def createProject(proj_name):
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
    root_folder_id = createNewFolder('root', 0)
    with engine.connect() as conn:
        pid = createID()
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = idInfo["email"],
                root_folder = root_folder_id
        )
    #permissions is a placeholder value for owner because we only have 1 perm rn but hey it's 1111
        relationstmt = insert(models.UserProjectRelation).values(
                user_email = idInfo["email"],
                proj_id = pid,
                role = "Owner",
                permissions = 15
        )
        conn.execute(projstmt)
        conn.execute(relationstmt)
        conn.commit()
    return {
        "success": True,
        "reason": "",
        "body": {}
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
    info = json.dumps(getProjectInfo(proj_id))
    return {"proj_info": info}

@app.route('/api/Project/<proj_id>/Documents', methods = ["GET"])
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
    proj_info = getProjectInfo(proj_id)
    documents = json.dumps(getAllChildDocuments(proj_info.root_folder))
    return {"documents": documents}


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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    folder_id = createNewFolder(inputBody["folder_name"], inputBody["parent_folder"])
    return {"posted": folder_id}

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
    info = json.dumps(getFolderInfo(folder_id))
    return {"folder_info": info}

#needs sections in body
    #credentials (of user that already has access to project)
    #email (user to add to project)
    #role (role name)
    #permissions (integer that represents perms, so far anything greater than 0 is everything)
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

    if(getUserProjPermissions(idInfo["email"], proj_id) < 3):
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

    #todo:make this a function
    #if not userExists(idInfo["email"]):
    #    retData = {
    #            "success": False,
    #            "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
    #            "body":{}
    #    }
    #    return jsonify(retData)

    # if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
    #     return {"success": False, "reason":"Invalid Permissions", "body":{}}
    ##########################
    createNewSnapshot(proj_id, doc_id, inputBody["data"])
    return {"posted": inputBody}

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
    blob = getBlob(proj_id + '/' + doc_id + '/' + snapshot_id)
    return {"blobContents": blob}

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
    if not isValidRequest(body, ["snapshot_id", "author_id", "reply_to_id", "content"]):
        return {
            "success": False,
            "reason": "Invalid Request"
        }

    # Query
    with Session() as session:
        try:
            session.add(models.Comment(
                snapshot_id=int(body["snapshot_id"]),
                author_id=int(body["author_id"]),
                reply_to_id=int(body["reply_to_id"]),
                content=body["content"],
                highlight_start_x = int(body["highlight_start_x"]),
                highlight_start_y = int(body["highlight_start_y"]),
                highlight_end_x = int(body["highlight_end_x"]),
                highlight_end_y = int(body["highlight_end_y"]),

            ))
            session.commit()
        except Exception as e:
            print("Error: ", e)
            return {
                "success": False,
                "reason": str(e)
            }

    print("Successful Write")
    return {
        "success": True,
        "reason": "Successful Write"
    }

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

    # Query
    commentsList = []
    with Session() as session:
        try:
            filteredComments = session.query(models.Comment) \
                .filter_by(snapshot_id=snapshot_id) \
                .all()

            for comment in filteredComments:
                commentsList.append({
                    "comment_id": comment.comment_id,
                    "snapshot_id": comment.snapshot_id,
                    "author_id": comment.author_id,
                    "reply_to_id": comment.reply_to_id,
                    "date_created": comment.date_created,
                    "date_modified": comment.date_modified,
                    "content": comment.content,
                    "highlight_start_x": comment.highlight_start_x,
                    "highlight_start_y": comment.highlight_start_y,
                    "highlight_end_x": comment.highlight_end_x,
                    "highlight_end_y": comment.highlight_end_y
                })
        except Exception as e:
            print("Error: ", e)
            return []
    
    print("Successful Read")
    return commentsList

#requires
    #credentials in headers

    #In body:
    #data (text you want in the document)
    #doc_name (name of document)
    #parent_folder (folder you're making it in)
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
    
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    doc_id = createNewDocument(inputBody["doc_name"], inputBody["parent_folder"])

    createNewSnapshot(proj_id, doc_id, inputBody["data"])

    return {"posted": inputBody}

@app.route('/api/Document/<proj_id>/<doc_id>/getSnapshotId/', methods=["GET"])
def getAllDocumentSnapshots(proj_id, doc_id):
    print("Request:", request.headers)
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

    if not userExists(idInfo["email"]):
        return {
                "success": False,
                "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
                "body":{}
        }
    
    foundSnapshots = getAllDocumentSnapshotsInOrder(doc_id)
    
    return {"success": True, "reason":"", "body": foundSnapshots}

@app.route('/api/Document/<proj_id>/<doc_id>/', methods=["GET"])
def getDocument(proj_id, doc_id):
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

    #if not userExists(idInfo["email"]):
    #    return {
    #            "success": False,
    #            "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
    #            "body":{}
    #    }

    # if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
    #     return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    info = json.dumps(getDocumentInfo(doc_id))
    return {"success": True, "reason":"", "body": info}

# Comment POST, GET, PUT, DELETE

@app.route('/api/comments/<comment_id>/subcomments/get', methods=["GET"])
def getSubcommentsOnComment(comment_id):
    # authenticate
    # query cloud sql
    
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

# EXAMPLE:
# curl -X GET http://127.0.0.1:5000/api/llm/code-implementation -H 'Content-Type: application/json' -d '{"code": "def aTwo(num):\n    return num+2;", "coding_language": "python", "comment": "change the function to snake case, add type hints, remove the unnecessary semicolon, and create a more meaningful function name that accurately describes the behavior of the function."}'
@app.route("/api/llm/code-implementation", methods=["GET"])
def implement_code_changes_from_comment():
    data = request.get_json()
    code = data.get("code")
    comment = data.get("comment")
    coding_language = data.get("coding_language")

    response = get_llm_code_from_suggestion(
        old_code=code,
        coding_language=coding_language,
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
# curl -X GET http://127.0.0.1:5000/api/llm/comment-suggestion -H 'Content-Type: application/json' -d '{"code": "def calc_avg(n):\n    total=0\n    count=0\n    for number in n:\n        total = total + number\n        count = count+1\n    average=total/count", "coding_language": "python"}'
@app.route("/api/llm/comment-suggestion", methods=["GET"])
def suggest_comment_from_code():
    data = request.get_json()
    code = data.get("code")
    coding_language = data.get("coding_language")

    response = get_llm_suggestion_from_code(
        code=code,
        coding_language=coding_language
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
