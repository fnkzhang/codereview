from flask import Flask
from flask_cors import CORS

app = None
def get_app(name):
    global app
    if app is None:
        app = Flask(name)
        CORS(app)

    return app