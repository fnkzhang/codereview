from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from cloudSql import *
from utils.commentUtils import *
from utils.miscUtils import *
from utils.snapshotUtils import *
from utils.projectUtils import *
from utils.userAndPermissionsUtils import *

import models 

@app.route('/api/Snapshot/<snapshot_id>/comment/create', methods=["POST"])
def createComment(snapshot_id):
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

    body = request.get_json()
    if not isValidRequest(body, ["author_email", "reply_to_id", "content"]):
        return {
            "success": False,
            "reason": "Invalid Request"
        }
    proj_id = getSnapshotProject(snapshot_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

    comment_id = createNewComment(snapshot_id, body["author_email"], int(body["reply_to_id"]), body["content"], int(body["highlight_start_x"]), int(body["highlight_start_y"]), int(body["highlight_end_x"]), int(body["highlight_end_y"]), is_resolved = body["is_resolved"])
    print("Successful Write Comment")
    return {
        "success": True,
        "reason": "Successful Write",
        "body": {
            "comment_id":comment_id,
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
    proj_id = getCommentProject(comment_id)
    print(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1 or getProjectInfo(proj_id)["author_email"] != idInfo["email"]):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    resolveCommentHelperFunction(comment_id)

    return {
        "success": True,
        "reason": "Ran The Call"
    }

# Comment POST, GET, PUT, DELETE
@app.route('/api/comments/<comment_id>/subcomments/get', methods=["GET"])
def getSubcommentsOnComment(comment_id):
    # authenticate
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

def editComment(comment_id):
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
    idInfo = authenticate()
    if idInfo is None:
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


