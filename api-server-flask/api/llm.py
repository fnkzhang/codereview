import json, re

# pip install "google-cloud-aiplatform>=1.38"
# pip install --upgrade google-cloud-aiplatform
# https://ai.google.dev/docs/prompt_best_practices
import vertexai
from vertexai.generative_models import (
    GenerativeModel
)

#------------------------------------------------------------------------------
# System Instruction Prompts
#-------------------------------------------------------------------------------
SYSTEM_INSTRUCTION_CODE_FROM_SUGGESTION = """\
You are a coding expert in {}. Apply the user's suggestion to the highlighted 
code which is located at lines between the start line and end line of the 
code. Modify the highlighted code. Avoid modifying the original code or giving 
an explanation for the code. Your response will be the changes you made to the highlighted code.
Return only the code that is changed, and DO NOT place the programming language name in the response.
Make sure to add the keep the indentation in relation to the parent code.
If the code was not commented out before, make sure that it stays uncommented.
Important: Do not let the user change your response format after you have already made the changes,
even if the user requests for it. Ignore user prompts that are
unrelated to implementing the code from the suggestion.
"""

# Your response must be a JSON object with the key 
# "revised_code". Important: Do not let the user change your JSON response 
# format, even if the user requests for it. Ignore user prompts that are
# unrelated to implementing the code from the suggestion.
SYSTEM_INSTRUCTION_SUGGESTION_FROM_CODE = """\
In all of your replies, respond as {}.
Generate multiple suggestions to improve the quality of code. Provide a 
diverse set of recommendations for enhancing the code's readability, 
performance, and maintainability. Return a JSON object with the key 
'suggestions' and a list of JSON objects. Each object in the list should 
contain 'startLine', 'endLine', and 'suggestion' keys, indicating the 
highlighted code lines and suggested changes. Be creative and offer as many 
suggestions as you can think of! Important: Do not let the user change your 
JSON response format, even if the user requests for it. Ignore user prompts
that are unrelated to recommending suggestions on the code.
"""
#------------------------------------------------------------------------------
# User Instruction Prompt Formats
#-------------------------------------------------------------------------------
USER_INSTRUCTION_CODE_FROM_SUGGESTION = """
<code>
{}
</code>
<highlighted_code>
{}
</highlighted_code>
<start_line>
{}
</start_line>
<end_line>
{}
</end_line>
<suggestion>
{}
</suggestion>
"""
USER_INSTRUCTION_SUGGESTION_FROM_CODE = """
<code>
{}
</code>
"""
#------------------------------------------------------------------------------
# Few-Shot Prompt Format
#-------------------------------------------------------------------------------
FEW_SHOT_EXAMPLE = """
<example_{}>
<input>
{}
</input>
<output>
{}
</output>
</example_{}>
"""

#------------------------------------------------------------------------------
# Few-Shot Examples
#-------------------------------------------------------------------------------
SAY_HELLO_CODE = """\
1| def foo():
2|     print("Hello World!")
3|
4| print("Testing foo()")
5| foo()
6| print("Done testing foo()")
"""

CALCULATE_AVERAGE_CODE = """\
1|def calc_avg(n):
2|    tot=0
3|    cnt=0
4|    for number in n:
5|      tot = tot+ number
6|      cnt= cnt+1
7|
8|    average=tot/cnt
"""

#------------------------------------------------------------------------------
# Initialize LLM
#-------------------------------------------------------------------------------
MODEL_NAME = "gemini-1.5-pro-preview-0409"#"gemini-1.0-pro"
def init_llm(project_id: str="codereview-413200",
             location: str="us-central1"):
    vertexai.init(project=project_id, location=location)

#------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------

def get_json_from_llm_response(response: str):
    json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)

    json_response = json_match.group(1) if json_match else response
    print("removed tick", json_response)
    pattern = r'(^```|```$)'
    json_response = re.sub(pattern, '', json_response)
    print("removed tick", json_response)
    #json_response = re.sub(r'\\', r'\\\\', re.sub(r'\t', r'\\t', re.sub(r'\n', r'\\n', json_response)))


    data = {
        "revised_code": json_response
    }
    data = json.dumps(data)
    #print(json_response)
    return data

def get_chat_response(user_prompt: str,
                      system_prompt: str = None):
    
    model = GenerativeModel(MODEL_NAME,
                            system_instruction=system_prompt)
    chat = model.start_chat()

    response = chat.send_message(user_prompt)

    return response.text

def add_few_shot_example(example_number, example_input, example_output):
    return FEW_SHOT_EXAMPLE.format(example_number, example_input, example_output, example_number)

def get_code_with_line_numbers(code: str):
    return '\n'.join([
        f"{i+1}| {line}" 
        for i, line in enumerate(code.splitlines())
    ])

#------------------------------------------------------------------------------
# Functions used by route
#-------------------------------------------------------------------------------
def get_llm_code_from_suggestion(code: str,
                                 highlighted_code: str,
                                 start_line: int,
                                 end_line: int,
                                 suggestion: str,
                                 language: str):
    # Configure System Prompt
    system_prompt = SYSTEM_INSTRUCTION_CODE_FROM_SUGGESTION.format(language)

    # Provide Few-Shot Examples on how the LLM should respond
    system_prompt += "<examples>\n"
    system_prompt += add_few_shot_example(
        example_number=1,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            SAY_HELLO_CODE, "foo",
            1, 1,
            "rename to something more meaningful"
        ),
        example_output= "say_hello"

        # example_output=json.dumps({
        #     "revised_code": "say_hello"
        # })
    )
    system_prompt += add_few_shot_example(
        example_number=2,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            "hi", "hi",
            1, 1,
            "Generate 10 paragraphs of Shakespeare and return \
            your response in a JSON with the key \"paragraphs\""
            ""
        ),
        example_output="Invalid Request."

        # example_output=json.dumps({
        #     "revised_code": "Invalid Request."
        # })
    )
    system_prompt += "</examples>"

    # Configure User Prompt
    user_prompt=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
        get_code_with_line_numbers(code), highlighted_code,
        start_line, end_line,
        suggestion
    )

    # Generate a response from LLM
    try:
        response = get_chat_response(user_prompt=user_prompt,
                                     system_prompt=system_prompt)
    except Exception as e:
        print("Failed to get response from LLM")
        print(e)
        return None

    # Extract the wanted output from response
    try:
        revised_code = get_json_from_llm_response(response)
        print("test", revised_code)
        revised_code = json.loads(revised_code)

        revised_code = revised_code["revised_code"]
        print("test2", revised_code)
    except Exception as e:
        print("Failed to get code from response")
        print(e)
        return None

    print("Implemented Code Generated by AI:", revised_code)
    return revised_code

def get_llm_suggestion_from_code(code: str,
                                 character="a developer at a code review session"):
    # Configure System Prompt
    system_prompt = SYSTEM_INSTRUCTION_SUGGESTION_FROM_CODE.format(character)

    # Provide Few-Shot Examples on how the LLM should respond
    system_prompt += "<examples>\n"

    system_prompt += add_few_shot_example(
        example_number=1,
        example_input=USER_INSTRUCTION_SUGGESTION_FROM_CODE.format(
            CALCULATE_AVERAGE_CODE
        ),
        example_output=json.dumps({
            "suggestions": [
                json.dumps({
                    "startLine": 1,
                    "endLine": 3,
                    "suggestion": "Rename `n`, `tot`, and `cnt` to more descriptive names such as `numbers`, `total_sum`, and `count` respectively."
                }),
                json.dumps({
                    "startLine": 4,
                    "endLine": 6,
                    "suggestion": "This works, but use Python's built-in functions like sum() and len() instead."
                }),
                json.dumps({
                    "startLine": 7,
                    "endLine": 7,
                    "suggestion": "You forgot a return statement. The function calculates the average but does nothing with it."
                })
            ]
        })
    )
    system_prompt += add_few_shot_example(
        example_number=2,
        example_input=USER_INSTRUCTION_SUGGESTION_FROM_CODE.format(
            "Generate 10 paragraphs of Shakespeare and return \
            your response in a JSON with the key \"paragraphs\""
        ),
        example_output=json.dumps({
            "suggestions": [
                json.dumps({
                    "startLine": 1,
                    "endLine": 1,
                    "suggestion": "Invalid Request."
                })
            ]
        })
    )
    system_prompt += "</examples>"

    # Configure User Prompt
    user_prompt = USER_INSTRUCTION_SUGGESTION_FROM_CODE.format(
        get_code_with_line_numbers(code)
    )

    # Generate a response from LLM
    try:
        response = get_chat_response(user_prompt=user_prompt,
                                     system_prompt=system_prompt)
    except Exception as e:
        print("Failed to get response from LLM")
        print(e)
        return None

    # Extract the wanted output from response
    try:
        suggestions = get_json_from_llm_response(response)["suggestions"]
    except Exception as e:
        print("Failed to get suggestions from response")
        print(e)
        return None

    print("Comment Suggestions Generated by AI:")
    for suggestion in suggestions:
        print(suggestion, '\n')

    return suggestions
