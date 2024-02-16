from flask import Flask, request, jsonify
from flask_cors import CORS

from google.oauth2 import id_token
from google.auth.transport import requests
#import jwt

#Todo hide later
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"

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
        "body": inputBody}

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
        id_token.verify_oauth2_token(credentialToken, requests.Request(), CLIENT_ID)
        return True
    except ValueError:
        print("FAILED INVALID TOKEN")
        return False