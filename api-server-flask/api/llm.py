import json
from typing import List, Optional

# pip install "google-cloud-aiplatform>=1.38"
# https://ai.google.dev/docs/prompt_best_practices
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, \
    Content, Part

#------------------------------------------------------------------------------
# Initialize LLM
#-------------------------------------------------------------------------------
model = None
def init_llm(project_id: str="codereview-413200",
             location: str="us-central1"):
    global model
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.0-pro")

#------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------
def get_content(role: str,
                text: str):
    return Content(role=role,
                   parts=[Part.from_text(text)])

def get_json_from_llm_response(response: str):
    start_index = response.find("```")
    end_index = response.rfind("```")

    json_response = response[start_index + 3: end_index]
    if (json_response.lower().startswith("json")):
        json_response = json_response[4:]

    print(json_response)
    
    return json.loads(json_response)

def get_chat_response(prompt: str,
                      history: Optional[List["Content"]] = None,
                      temperature: float=0.15):
    text_response = []
    chat = model.start_chat(history=history)
    
    responses = chat.send_message(prompt,
                                  stream=True,
                                  generation_config=GenerationConfig(
                                      temperature=temperature
                                  ))
    for chunk in responses:
        text_response.append(chunk.text)
    return "".join(text_response)

#------------------------------------------------------------------------------
# Functions used by route
#-------------------------------------------------------------------------------
def get_llm_code_from_suggestion(code: str,
                                 highlighted_code: str,
                                 suggestion: str):
    history = []

    # System prompt with additional context and expected response format
    system_prompt = f"""System Prompt:
    Apply the suggestions to the highlighted code without additional \
    commentary or text. The highlighted code will be a substring located \
    in ```{code}```. Return a JSON object that has the field "code" \
    with the value being the revised code.

    Example
    ```
    {{
        "code": "Your code here"
    }}
    ```
    """
    history.append(get_content("user", system_prompt))
    history.append(get_content("model", "Understood."))

    # User prompt
    user_prompt = f"""Highlighted Code:```
    {highlighted_code}
    ```
    Suggestion: {suggestion}
    """

    try:
        response = get_chat_response(user_prompt, history=history)
    except:
        print("Failed to get response from LLM")
        return None
    
    try:
        new_code = get_json_from_llm_response(response)["code"]
    except:
        print("Failed to get code from response")
        return None

    print("Output:\n\n", new_code, '\n')

    return new_code

def get_llm_suggestion_from_code(code: str):
    history = []

    # System prompt with additional context and expected response format
    system_prompt = f"""System Prompt:
    List some suggestions that would improve the quality of the highlighted \
    code according to best practices. Return a JSON object that has the \
    field "suggestions" with the value being a list of suggestions.

    Example
    ```
    {{
        "suggestions": [
            "Your suggestions here"
        ]
    }}
    ```
    """
    history.append(get_content("user", system_prompt))
    history.append(get_content("model", "Understood."))

    # User prompt
    user_prompt = f"""
    {code}
    ```
    """

    try:
        response = get_chat_response(user_prompt, history=history)
    except:
        print("Failed to get response from LLM")
        return None
    
    try:
        suggestions = get_json_from_llm_response(response)["suggestions"]
    except:
        print("Failed to get suggestions from response")
        return None

    print("Output:\n")
    for suggestion in suggestions:
        print(suggestion, '\n')

    return suggestions
