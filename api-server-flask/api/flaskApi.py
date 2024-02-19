from flask import Flask, request, jsonify
from flask_cors import CORS


from google.oauth2 import id_token
from google.auth.transport import requests


from google.cloud.sql.connector import Connector, IPTypes

# from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy import Table, Column, String, Integer, Float, Boolean, MetaData, insert
import pymysql

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

app = Flask(__name__)


CORS(app)

class User():
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(50))

def connectCloudSql() -> sqlalchemy.engine.base.Engine:
    instance_connection_name = "codereview-413200:us-central1:cr-cloudsql-db"
    db_user = "root"
    db_pass = "Q$mXxb?_io-#<-_0"
    db_name = "test"

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        
        return conn;

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        echo = True
    )
    print("Finished")
    return pool

metaData = MetaData()
data = Table('testTable', metaData,
            Column('id', Integer(), primary_key=True),
            Column('name', String(50), nullable=False),
            Column('email', String(50), nullable=False),
            )

# Remove Later for testing
@app.route('/createTable')
def createTable():
    engine = connectCloudSql()
    
    metaData.create_all(engine)
    print("Table was created")
    return "Created Table"


@app.route('/insert')
def testInsert():
    engine = connectCloudSql()
    with engine.connect() as conn:
        stmt = insert(data).values(name="PungeBob", email="testEmail@gmail.com")

        conn.execute(stmt)
        conn.commit()
        
    return "tested"

# Comment Post, Delete, GET,
@app.route('/api/comment', methods=["POST"])
def createComment():
    
    pass

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