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
    """
    ``POST /api/Snapshot/<snapshot_id>/comment/create``

    **Explanation:**
        Creates a top-level comment on the given snapshot

    **Args:**
        - snapshot_id (str): The ID of the snapshot.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the comment creation was successful.
            - reason (str): Description of the result of the comment creation.
            - body (dict): Information about the created comment, including its ID, snapshot ID, author email, reply-to ID, content, highlight start and end coordinates, and resolution status.

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
    """
    ``PUT /api/comment/<comment_id>/resolve``

    **Explanation:**
        Resolves a given comment

    **Args:**
        - comment_id (str): The ID of the comment to resolve.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the resolution operation was successful.
            - reason (str): Description of the result of the resolution operation.

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
    proj_id = getCommentProject(comment_id)
    print(comment_id)
    if(getUserProjPermissions(idInfo["email"], proj_id) < 1):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}
    resolveCommentHelperFunction(comment_id)

    return {
        "success": True,
        "reason": "Ran The Call"
    }

@app.route('/api/comments/<comment_id>/edit', methods=["PUT"])
def editComment(comment_id):
    """
    ``PUT /api/comments/<comment_id>/edit``

    **Explanation:**
        Edits a comment

    **Args:**
        - comment_id (str): The ID of the comment to edit.
        - request.body (dict):
            - content (str): new contents of comment

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the edit operation was successful.
            - reason (str): Description of the result of the edit operation.

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
    """
    ``DELETE /api/comments/<comment_id>/delete``

    **Explanation:**
        Deletes a comment

    **Args:**
        - comment_id (str): The ID of the comment to delete.

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the delete operation was successful.
            - reason (str): Description of the result of the delete operation.

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


