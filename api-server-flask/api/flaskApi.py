from cloudSql import connectCloudSql
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import storage
from utils import *
from diff_match_patch import diff_match_patch
from google.oauth2 import id_token
from google.auth.transport import requests
import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select
import pymysql
import models

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

app = Flask(__name__)


CORS(app)
engine = connectCloudSql()


# Remove Later
class User():
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))


metaData = MetaData()
table = Table('testTable', metaData,
            Column('id', Integer(), primary_key=True),
            Column('name', String(50), nullable=False),
            Column('email', String(50), nullable=False),
            )

# Remove Later for testing
@app.route('/createTable')
def createTable():
    engine = connectCloudSql()
    
    models.Comment.metadata = models.Base.metadata

    models.Comment.metadata.create_all(engine)

    #metaData.create_all(engine)
    print("Table was created")
    return "Created Table"


@app.route('/insert')
def testInsert():
    #engine = connectCloudSql()
    with engine.connect() as conn:
        stmt = insert(table).values(name="PungeBob", email="testEmail@gmail.com")

        conn.execute(stmt)
        conn.commit()

    return "tested"

@app.route('/testGrabData')
def grabData():
    #engine = connectCloudSql()

    with engine.connect() as conn:
        stmt = select(table).where(table.c.email == "testEmail@gmail.com")

        result = conn.execute(stmt)
        result = result.mappings().all()

        retArray = []
        # Recreate Dict from SQLAlchemy Row and return
        # Can't Find any alternatives that worked rn maybe in future
        for row in result:
            d = {}
            d["id"] = row.id
            d["name"] = row.name
            d["email"] = row.email

            retArray.append(d)

    returnArray = {
        "success": True,
        "reason": "",
        "body": retArray,
    }
    
    return returnArray
# End Remove later

# Comment Post, Delete, GET,
@app.route('/api/comment', methods=["POST"])
def createComment():
    requestedData = request.get_json()

    # Error Check
    if "credential" not in requestedData:
        return { "success": False,
                "reason": "Invalid JSON Provided",
                "body": {}
            }
    
    # Authentication
    credential = requestedData["credential"]
    if not IsValidCredential(credential):
        retData = {
            "success": False,
            "reason": "Invalid Token Provided",
            "body": {}
        }
        return jsonify(retData) 
    
    # Query
    engine = connectCloudSql()

    with engine.connect() as conn:
        stmt = insert(models.Comment).values(
           # comment_id=requestedData["comment_id"],
            diff_id=requestedData["diff_id"],
            author_id=requestedData["author_id"],
            reply_to_id=requestedData["reply_to_id"],
            content=requestedData["content"],
        )

        conn.execute(stmt)
        conn.commit()

    retData = {
        "success": True,
        "reason": "",
        "body": {}
    }

    return jsonify(retData) 

# Return All Comments for a dig
@app.route('/api/comment', methods=["GET"])
def getComment():
    requestedData = request.get_json()

    # Error Check

    if "credential" not in requestedData:
        return { "success": False,
                "reason": "Invalid JSON Provided",
                "body": {}
            }
    
    # Authentication
    credential = requestedData["credential"]
    if not IsValidCredential(credential):
        retData = {
            "success": False,
            "reason": "Invalid Token Provided",
            "body": {}
        }
        return jsonify(retData) 
    
     # Query
    engine = connectCloudSql()

    diff_id = requestedData["diff_id"]

    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.diff_id == diff_id)

        retArray = []
        for row in conn.execute(stmt):
            d ={}

            d["comment_id"] = row.comment_id
            d["diff_id"] = row.diff_id
            d["author_id"] = row.author_id
            d["reply_to_id"] = row.reply_to_id
            d["date_created"] = row.date_created
            d["date_modified"] = row.date_modified
            d["content"] = row.content
            print(row)
            retArray.append(d)        

    returnArray = {
        "success": True,
        "reason": "",
        "body": retArray,
    }
    
    return returnArray   

    


@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test" 

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
    
    if not IsValidCredential(inputBody["credential"]):
        return { "success": False,
                "reason": "Invalid Token Provided",
                "body": {}
                    }
    
    return { "success": True,
            "reason": "N/A",
            "body": inputBody
            }

@app.route('/api/user/authenticate', methods=["POST"])
def authenticate():
    print("Hello")
    inputToken = request.get_json()

    try:
        idInfo = id_token.verify_oauth2_token(inputToken["credential"], requests.Request(), CLIENT_ID)

        retData = {
            "success": True,
            "reason": "N/A",
            "body": idInfo
        }

        print("Success?")
        # RETURN User Data back
        return jsonify(retData)
    
    except ValueError:
        print("FAILED INVALID TOKEN")
        retData = {
            "success": False,
            "reason": "FAILED TO AUTHENTICATE SIGNIN FROM GOOGLE",
            "body": {}
        }
        return jsonify(retData) 

# Call Func every api func call to make sure that user is Authenticated before running
def IsValidCredential(credentialToken):
    try:
        print("Valid ID_TOKEN supplied")
        id_token.verify_oauth2_token(credentialToken, requests.Request(), CLIENT_ID)
        return True
    except ValueError:
        print("FAILED INVALID TOKEN")
        return False
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