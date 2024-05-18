from app import get_app
app = get_app(__name__)

from flask import request
from projectRoutes import *
from folderRoutes import *
from documentRoutes import *
from snapshotRoutes import *
from commentRoutes import *
from llmRoutes import *
from githubRoutes import *
from userAndPermissionsRoutes import *
from authRoutes import *
from utils.commitUtils import *

# PUT TEST/TEMP STUFF HERE
# @app.route
@app.route('/createTable')
def createTable():
    engine = connectCloudSql()
    metaData = MetaData()
    models.Base.metadata.create_all(engine)
    print("Table was created")
    return "Created Table"
# curl -X POST http://127.0.0.1:5000/api/llm/test -H 'Content-Type: application/json' -d '{"input": "hi"}'
@app.route("/api/llm/test", methods=["POST"])
def test_llm():
    data = request.get_json()
    input = data.get("input")

    response = get_chat_response(input)

    if response is None:
        return {
            "success": False,
            "reason": "LLM Error"
        }

    return response
@app.route("/api/llm/test/randomcodefile", methods=["GET"])
def testcommentodcodellm():
    code = open('VaccineRouter.cpp').read()
    highlighted_code="CityInfo citie[], int numCitie"
    start_line = 38
    end_line = 38
    comment = "rename these to something better"
    language = "C++"

    response = get_llm_code_from_suggestion(
        code=code,
        highlighted_code=highlighted_code,
        start_line=start_line,
        end_line=end_line,
        suggestion=comment,
        language=language
    )
    
    if response is None:
        return {
            "success": False,
            "reason": "LLM Error"
        }
    return {
        "success": True,
        "reason": "Success",
        "body": response
    }
@app.route('/api/llm/testexamples', methods = ["GET"])
def testExamples():
    print(buildStringFromLLMResponse(SAY_HELLO_CODE, json.loads(SAY_HELLO_RESPONSE)))
    print("_______________________________")
    print(buildStringFromLLMResponse(CREATE_GETTER_CODE, json.loads(CREATE_GETTER_RESPONSE)))
    print("_______________________________")
    print(buildStringFromLLMResponse(RENAME_VARIABLE_CODE, json.loads(RENAME_VARIABLE_RESPONSE)))
    print("_______________________________")
    print(buildStringFromLLMResponse(RENAME_VARIABLE_CODE_2, json.loads(RENAME_VARIABLE_RESPONSE_2)))
    print("_______________________________")
    return {"treu":True}

@app.route("/api/snapshot/test/<snapshot_id>/", methods=["GET"])
def testsnapshotgetinfo(snapshot_id):
    return {"hi":getSnapshotInfo(snapshot_id)}

def get_app():
    return app
