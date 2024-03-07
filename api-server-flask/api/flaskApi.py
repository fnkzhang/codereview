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
from diff_match_patch import diff_match_patch
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import sessionmaker
import models

from utils import engine

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

engine = connectCloudSql()
Session = sessionmaker(engine)

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

    if not userExists(idInfo["email"]):
        retData = {
                "success": False,
                "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
                "body":{}
        }
        return jsonify(retData)
    with engine.connect() as conn:
        pid = createID()
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = idInfo["email"]
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
    return True

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

    if not userExists(idInfo["email"]):
        retData = {
                "success": False,
                "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
                "body":{}
        }
        return jsonify(retData)

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
                proj_id == proj_id
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

    if not userExists(idInfo["email"]):
        retData = {
                "success": False,
                "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
                "body":{}
        }
        return jsonify(retData)
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

@app.route('/api/Document/<proj_id>/<doc_id>/create', methods=["POST"])
def createDocument(proj_id, doc_id):
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
    if not userExists(idInfo["email"]):
        retData = {
                "success": False,
                "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
                "body":{}
        }
        return jsonify(retData)

    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    ##########################
    uploadBlob(proj_id + '/' + doc_id,  inputBody["data"])

    return {"posted": inputBody}

@app.route('/api/Document/<proj_id>/<doc_id>/get', methods=["GET"])
def getDocument(proj_id, doc_id):
    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }
    
    #if not userExists(idInfo["email"]):
    #    retData = {
    #            "success": False,
    #            "reason": "Account does not exist, stop trying to game the system by connecting to backend not through the frontend",
    #            "body":{}
    #    }
    #    return jsonify(retData)
    
    #if(getUserProjPermissions(idInfo["email"], proj_id) < 0):
    #    return {"success": False, "reason":"Invalid Permissions", "body":{}}
    
    document = fetchFromCloudStorage(f"{proj_id}/{doc_id}")

    return {"blobContents": document}

#not gonna mess with diff stuff for now because again, i'm only going to focus on document permissions
@app.route('/api/Document/<proj_id>/<doc_id>/<diff_id>/create', methods=["POST"])
def createDiff(proj_id, doc_id, diff_id):
    inputBody = request.get_json()
    dmp = diff_match_patch()
    diffText = dmp.patch_toText(dmp.patch_make(dmp.diff_main(inputBody["original"], inputBody["updated"])))
    uploadBlob(proj_id + '/' + doc_id + '/' + diff_id, diffText)
    return {"diffText": diffText}

@app.route('/api/Document/<proj_id>/<doc_id>/<diff_id>/get', methods=["GET"])
def getDiff(proj_id, doc_id, diff_id):
    idInfo = authenticate()
    if idInfo is None:
        return {
            "success":False,
            "reason": "Failed to Authenticate"
        }

    diff = fetchFromCloudStorage(f"{proj_id}/{doc_id}/{diff_id}")
    document = fetchFromCloudStorage(f"{proj_id}/{doc_id}")
    
    dmp = diff_match_patch()
    output, _ = dmp.patch_apply(dmp.patch_fromText(diff), document)
    return {"diffResult": output}

@app.route('/api/Document/<proj_id>/<doc_id>/test', methods=["GET"])
def testDocument(proj_id, doc_id):
    return uploadBlob(proj_id + '/'+ doc_id, {'ok':'hey'})

# Comment POST, GET, PUT, DELETE
@app.route('/api/diffs/<diff_id>/comment/create', methods=["POST"])
def createComment(diff_id):
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
    if not isValidRequest(body, ["diff_id", "author_id", "reply_to_id", "content"]):
        return {
            "success": False,
            "reason": "Invalid Request"
        }

    # Query
    with Session() as session:
        try:
            session.add(models.Comment(
                diff_id=int(body["diff_id"]),
                author_id=int(body["author_id"]),
                reply_to_id=int(body["reply_to_id"]),
                content=body["content"]
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

@app.route('/api/diffs/<diff_id>/comments/get', methods=["GET"])
def getCommentsOnDiff(diff_id):
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
                .filter_by(diff_id=diff_id) \
                .all()

            for comment in filteredComments:
                commentsList.append({
                    "comment_id": comment.comment_id,
                    "diff_id": comment.diff_id,
                    "author_id": comment.author_id,
                    "reply_to_id": comment.reply_to_id,
                    "date_created": comment.date_created,
                    "date_modified": comment.date_modified,
                    "content": comment.content
                })
        except Exception as e:
            print("Error: ", e)
            return []

    print("Successful Read")
    return commentsList

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
        "reason": "Successful Delete"
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
