from flask import Flask, request, jsonify
from flask_cors import CORS

from os import environ

from google.oauth2 import id_token
from google.auth.transport import requests
#import jwt

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
    return {"receivedData": inputBody}

@app.route('/api/user/authenticate', methods=["POST"])
def authenticate():
    print("Hello")
    inputToken = request.get_json()

    # if not inputToken["access_token"]:
    #     print("JSON INVALID")
    #     # Invalid JSON submitted
    #     retData = {
    #         "failed": True,
    #         "reason": "Invalid INPUT JSON"
    #     }

    #     return jsonify(retData) 

    try:

        idInfo = id_token.verify_oauth2_token(inputToken["credential"], requests.Request(), CLIENT_ID)

        retData = {
            "envVar": CLIENT_ID,
            "resultID": idInfo,
            "inputToken": inputToken,
        }

        print("Success?")
        # RETURN User Data back
        return jsonify(retData)
    
    except ValueError:
        print("FAILED INVALID TOKEN")
        retData = {
            "failed": True,
            "code": "FAILED TO AUTHENTICATE TOKEN FROM GOOGLE"
        }
        return jsonify(retData) 
        #Invalid Token
        pass
    # Oauth token 
    # Front end send request to get toen
    # Send back token and when a function is called make sure valid Oauth token is used
    return "FAILED"
    pass