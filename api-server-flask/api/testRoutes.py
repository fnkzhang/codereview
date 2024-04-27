from app import get_app
app = get_app()

from flask import request

# PUT TEST/TEMP STUFF HERE
# @app.route

from llm import get_chat_response
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

def get_app():
    return app