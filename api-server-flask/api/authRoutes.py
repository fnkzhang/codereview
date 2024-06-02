from app import get_app
app = get_app(__name__)

from flask import request, jsonify

from google.oauth2 import id_token
from google.auth.transport import requests

from utils.miscUtils import *
from utils.userAndPermissionsUtils import *

@app.route('/api/user/authenticate', methods=["POST"])
def authenticator():
    """
    ``POST /api/user/authenticate``

    **Explanation:**
        Authenticates a user and sees if their credentials from google are correct

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the authentication was successful.
            - reason (str): Description of the authentication result.
            - body (dict): User information if authentication was successful, empty dictionary otherwise.

    """
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

@app.route('/api/user/signup', methods = ["POST"])
def signUp():
    """
    ``POST /api/user/signup``

    **Explanation:**
        Checks a user's credentials from google, and if they do not exist in our database, gets added

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the signup was successful.
            - reason (str): Description of the signup result.
            - body (dict): User information if signup was successful, empty dictionary otherwise.

    """
    idInfo = authenticate()
    if idInfo is None:
        return {
            "success": False,
            "reason": "Failed to Authenticate"
        }

    if userExists(idInfo["email"]) == False:
        createNewUser(idInfo["email"], idInfo["name"])

    return {
            "success": True,
            "reason": "N/A",
            "body": idInfo
    }

@app.route('/api/user/isValidUser', methods=["POST"])
def checkIsValidUser():
    """
    ``POST /api/user/isValidUser``

    **Explanation:**
        Checks if user exists from authentication given in headers

    **Returns:**
        A dictionary containing the following keys:
            - success (bool): Indicates whether the user is valid.
            - reason (str): Description of the validation result.
            - body (dict): Empty dictionary.

    """
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

