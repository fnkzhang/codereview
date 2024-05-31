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
    headers = request.headers
    if (not isValidRequest(headers, ["Authorization"])):
        print("what")
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
    return datetime.now()

def createID():
    return uuid.uuid4().int >> (128 - 31)

def isValidRequest(parameters, requiredKeys):
    for key in requiredKeys:
        if key not in parameters:
            return False

    return True

def buildStringFromLLMResponse(code, response):
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

