from commentRoutes import *
from llmRoutes import *
from githubRoutes import *
from userAndPermissionsRoutes import *
from authRoutes import *

@app.after_request
def afterRequest(response):
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route("/")
def defaultRoute():
    #print('what', file=sys.stderr)
    return "test"

