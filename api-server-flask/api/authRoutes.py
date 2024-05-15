from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests

from utils.miscUtils import *
from utils.userAndPermissionsUtils import *

@app.route('/api/user/authenticate', methods=["POST"])
def authenticator():
    idInfo = authenticate()
    if idInfo is not None:
        print("Successful authentication")
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

#literally just authenticator but it adds a user to the database.
@app.route('/api/user/signup/', methods = ["POST"])
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
        return {
                "success": False,
                "reason": "Account already exists",
                "body":{}
        }
    createNewUser(idInfo["email"], idInfo["name"])
    return {
            "success":True,
            "reason": "N/A",
            "body": idInfo
    }

# Might need to reformat this function
@app.route('/api/user/isValidUser', methods=["POST"])
def checkIsValidUser():
    headers = request.headers

    if (not isValidRequest(headers, ["Authorization"])):
        return {
                "success": False,
                "reason": "Invalid Token Provided"
        }

    if (not isValidRequest(headers, ["Email"])):
        return {
            "success": False,
            "reason": "Invalid Header Provided"
        }

    user = userExists(headers["Email"])

    if (not user):
        return {
            "success": False,
            "reason": "User Does not exist"
        }

    return {
        "success": True,
        "reason": "",
        "body": {}
    }

