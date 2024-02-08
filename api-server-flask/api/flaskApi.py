from flask import Flask, request
from flask_cors import CORS
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
