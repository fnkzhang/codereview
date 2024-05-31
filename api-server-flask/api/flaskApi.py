from app import get_app
app = get_app(__name__)

from flask import request, jsonify
try:
    from testRoutes import *
except Exception as e:
    print(e)
    pass
from projectRoutes import *
from folderRoutes import *
from documentRoutes import *
from snapshotRoutes import *
from commentRoutes import *
from llmRoutes import *
from githubRoutes import *
from userAndPermissionsRoutes import *
from authRoutes import *
from commitRoutes import *

@app.after_request
def afterRequest(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test"
