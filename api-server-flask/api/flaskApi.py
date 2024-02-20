from flask import Flask, request, jsonify
from flask_cors import CORS

from google.oauth2 import id_token
from google.auth.transport import requests

import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select
import pymysql

import models
from cloudSql import connectCloudSql
from utils import *

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

app = Flask(__name__)


CORS(app)
engine = connectCloudSql()


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
    with engine.connect() as conn:
        stmt = insert(table).values(name="PungeBob", email="testEmail@gmail.com")

        conn.execute(stmt)
        conn.commit()

    return "tested"

@app.route('/testGrabData')
def grabData():
    engine = connectCloudSql()

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
    #print("Hello")
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


@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test"



# Takes in json with "code" section
@app.route('/api/sendData', methods=["POST"])
def sendData():
    inputBody = request.get_json()
    return {"receivedData": inputBody}

@app.route('api/Document/<proj_name>/', methods = ["POST"])
def createProject(proj_name):
    with engine.connect() as conn:
        inputBody = request.get_json()
        validity = isValidRequest(inputBody)
        if validity != None:
            return validity
        pid = createID()
        projstmt = insert(models.Project).values(
                proj_id = pid,
                name = proj_name,
                author_email = inputBody["credential"]["email"]
        )
        #permissions is a placeholder value for owner because we only have 1 perm rn
        relationstmt = insert(models.UserProjectRelation).values(
                user_email = inputBody["credential"]["email"],
                proj_id = pid,
                role = "Owner",
                permissions = 15
        )
        conn.execute(projstmt)
        conn.execute(relationstmt)
        conn.commit()
    return True

@app.route('/api/Document/<proj_id>/<doc_id>/', methods=["POST"])
def createDocument(proj_id, doc_id):
    inputBody = request.get_json()
    validity = isValidRequest(inputBody)
    if validity != None:
        return validity

    uploadBlob(proj_id + '/' + doc_id,  inputBody["data"])
    return {"posted": inputBody}


@app.route('/api/Document/<proj_id>/<doc_id>/', methods=["GET"])
def getDocument(proj_id, doc_id):
    inputBody = request.get_json()
    validity = isValidRequest(inputBody)
    if(getUserProjPermissions(inputBody["credential"]["email"], proj_id) == False):
        return {"success": False, "reason":"Invalid Permissions", "body":{}}

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
                                                                 
