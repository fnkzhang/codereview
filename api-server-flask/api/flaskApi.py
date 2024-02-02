from flask import Flask

app = Flask(__name__)

@app.route("/")
def defaultRoute():
    return "UR MOM" 




@app.route("/sendData", methods=["GET"])
def sendData():
    


    pass
