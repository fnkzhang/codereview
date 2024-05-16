from app import get_app
app = get_app(__name__)

from flask import request

from utils.llmUtils import *

init_llm()

#in body:
    #highlighted_code = code that the comment highlighted
    #code = entire code
    #comment = commented text
# EXAMPLE:
# curl -X POST http://127.0.0.1:5000/api/llm/code-implementation -H 'Content-Type: application/json' -d '{"code": "def aTwo(num):\n    return num+2;\n\nprint(aTwo(2))", "highlighted_code": "def aTwo(num):\n    return num+2;", "startLine": 1, "endLine": 2, "comment": "change the function to snake case, add type hints, remove the unnecessary semicolon, and create a more meaningful function name that accurately describes the behavior of the function.", "language": "Python"}'
@app.route("/api/llm/code-implementation", methods=["POST"])
def implement_code_changes_from_comment():
    data = request.get_json()
    code = data.get("code")
    highlighted_code=data.get("highlightedCode")
    start_line = data.get("startLine")
    end_line = data.get("endLine")
    comment = data.get("comment")
    language = data.get("language")

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
    if response["success"] == False:
        return {
            "success": False,
            "reason":"Off-topic comment"
        }
    body = buildStringFromLLMResponse(code, response)
    if body is None:
        return {
            "success": False,
            "reason": "Unable to build string from response."
        }

    return {
        "success": True,
        "reason": "Success",
        "body": body
    }

# EXAMPLE:
# curl -X POST http://127.0.0.1:5000/api/llm/comment-suggestion -H 'Content-Type: application/json' -d '{"code": "#include <ioteam>\n\nint main() {\n    int num = 4;\n    switch(num) {\n        case 4:\n            std::cout << \"4\" << std::endl;\n            break;\n        default:\n            std::cout << \"not 4\" << std::edl\n            break;\n    }\n    return 0;\n}", "language": "C++"}'
@app.route("/api/llm/comment-suggestion", methods=["POST"])
def suggest_comment_from_code():
    data = request.get_json()
    code = data.get("code")
    language = data.get("language")

    response = get_llm_suggestion_from_code(
        code=code,
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
