from flask import request, jsonify

import json
import uuid
from datetime import datetime
import os
import google.auth
from google.oauth2 import id_token
from google.auth.transport import requests
import threading

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/googlecreds.json"
os.environ["GCLOUD_PROJECT"] = "codereview-413200"
CLIENT_ID = "474055387624-orr54rn978klbpdpi967r92cssourj08.apps.googleusercontent.com"


def authenticate():
    """
    **Explanation:**
        Verifies a user's credentials

    **Args:**
        - headers (dict): Not really an argument, but this function can only be called in routes which will have headers

    **Returns:**
        idInfo (json): A json object that describes the verified user's information. Includes "email" and "name" keys, which map to the user's email and name respectively. If user cannot be verified, returns None
    """
    headers = request.headers
    if (not isValidRequest(headers, ["Authorization"])):
        return None
    try:
        idInfo = id_token.verify_oauth2_token(
            headers["Authorization"],
            requests.Request(),
            CLIENT_ID
        )
        return idInfo

    except ValueError:
        return None

def getTime():
    """
    **Explanation:**
        Gets the current time

    **Returns:**
        time (datetime): the current time
    """
    return datetime.now()

def createID():
    """
    **Explanation:**
        Creates a uuid in int format

    **Returns:**
        id (int): generated uuid
    """
    return uuid.uuid4().int >> (128 - 31)

def isValidRequest(parameters, requiredKeys):
    """
    **Explanation:**
        Checks whether or not the request's parameters includes the required keys

    **Args:**
        - parameters (dict): The parameters that will be checked for the keys
        - keys (list): list of required keys

    **Returns:**
        - success (bool): Whether or not the request is valid
    """
    for key in requiredKeys:
        if key not in parameters:
            return False

    return True

def buildStringFromLLMResponse(code, response):
    """
    **Explanation:**
        Checks whether or not the request's parameters includes the required keys

    **Args:**
        - code (str): original code to edit 
        - response (dict): A dict with the keys "success", "insertions", and "deletions". The "insertions" key maps to a dictionary of line insertions that follow the format of (line number (int)) : "(lines to insert (str))". The lines are inserted on the line number directly after the line number provided. The "deletions" key maps to a list of line numbers (int) that should be deleted. The "success" key maps to whether or not the response was succesfull

    **Returns:**
        - builtString (str): Rebuilt code based off of the response dict
    """
    success = response["success"]
    if success == False:
        return False
    insertions = convertKeysToInt(response["insertions"])
    deletions = response["deletions"]
    codeList = code.split('\n')
    builtString = ""
    for i in range(len(codeList)+1):
        if i not in deletions:
            if i > 0:
                builtString = builtString + codeList[i-1]
                if i < len(codeList) or insertions.get(i) != None:
                    builtString = builtString + '\n'
        if insertions.get(i) != None:
            builtString = builtString + insertions.get(i)
            if i < len(codeList) or insertions.get(i) != None:
                builtString = builtString + '\n'
    return builtString

def convertKeysToInt(somedict):
    rv = {}
    for key in somedict.keys():
        rv[int(key)] = somedict[key]
    return rv

