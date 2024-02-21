from cloudSql import connectCloudSql
from flask import Flask, request
from flask_cors import CORS
from google.cloud import storage
from utils import *
from diff_match_patch import diff_match_patch
app = Flask(__name__)

CORS(app)

@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test" 



# Takes in json with "code" section
@app.route('/api/sendData', methods=["POST"])
def sendData():
    inputBody = request.get_json()
    return {"receivedData": inputBody}

@app.route('/api/Document/<proj_id>/<doc_id>/create', methods=["POST"])
def createDocument(proj_id, doc_id):
    inputBody = request.get_json()
    uploadBlob(proj_id + '/' + doc_id,  inputBody["data"])
    return {"posted": inputBody}

@app.route('/api/Document/<proj_id>/<doc_id>/get', methods=["GET"])
def getDocument(proj_id, doc_id):
    blob = getBlob(proj_id + '/' + doc_id)
    return {"blobContents": blob}

@app.route('/api/Document/<proj_id>/<doc_id>/<diff_id>/create', methods=["POST"])
def createDiff(proj_id, doc_id, diff_id):
    inputBody = request.get_json()
    dmp = diff_match_patch()
    diffText = dmp.patch_toText(dmp.patch_make(dmp.diff_main(inputBody["original"], inputBody["updated"])))
    uploadBlob(proj_id + '/' + doc_id + '/' + diff_id, diffText)
    return {"diffText": diffText}

@app.route('/api/Document/<proj_id>/<doc_id>/<diff_id>/get', methods=["GET"])
def getDiff(proj_id, doc_id, diff_id):
    document = getBlob(proj_id + '/' + doc_id)
    diffText = getBlob(proj_id + '/' + doc_id + '/' + diff_id)
    dmp = diff_match_patch()
    output, _ = dmp.patch_apply(dmp.patch_fromText(diffText), document)
    return {"diffResult": output}

@app.route('/api/Document/<proj_id>/<doc_id>/test', methods=["GET"])
def testDocument(proj_id, doc_id):
    return uploadBlob(proj_id + '/'+ doc_id, {'ok':'hey'})

@app.route('/api/diffs/<diff_id>/comment/create', methods=["POST"])
def postComment(diff_id):
    # authenticate
    # query cloud sql
    
    # temporary
    return {"success": True}

@app.route('/api/diffs/<diff_id>/comments/get', methods=["GET"])
def getCommentsOnDiff(diff_id):
    # authenticate
    # query cloud sql
    
    # temporary
    retArray = []
    for i in range(10):
        d = {
            "comment_id": i + 1,
            "diff_id": diff_id,
            "author_id": 1000 + i,
            "reply_to_id": 0,
            "date_created": "2024-02-20 12:00:00",
            "date_modified": "2024-02-20 12:00:00",
            "content": f"Fake comment {i+1}"
        }
        retArray.append(d)
    
    return retArray

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
    # authenticate
    # query cloud sql
    
    # temporary
    return {"success": True}

@app.route('/api/comments/<comment_id>/delete', methods=["DELETE"])
def deleteComment(comment_id):
    # authenticate
    # query cloud sql
    
    # temporary
    return {"success": True}