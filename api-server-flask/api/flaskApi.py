from flask import Flask, request, jsonify
from flask_cors import CORS

from google.oauth2 import id_token
from google.auth.transport import requests

import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert, select
import pymysql

import models
from cloudSql import connectCloudSql

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

app = Flask(__name__)


CORS(app)

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
    engine = connectCloudSql()
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

        for row in result:
            print(row, type(row))

    list_of_dicts = [row._asdict() for row in result]
    print(list_of_dicts)
    return list_of_dicts


# Comment Post, Delete, GET,
@app.route('/api/comment', methods=["POST"])
def createComment():
    requestedData = request.get_json()

    # Error Check

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
            comment_id=requestedData["comment_id"],
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
    pass

# Return All Comments for a dig
@app.route('/api/comment', methods=["GET"])
def getComment():
    requestedData = request.get_json()

    # Error Check

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

    returnObj = {}

    with engine.connect() as conn:
        stmt = select(models.Comment).where(models.Comment.c.diff_id == diff_id)
    
        for row in conn.execute(stmt):
            print(row)
            
    

    


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