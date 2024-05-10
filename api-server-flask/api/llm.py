import json, re

# pip install --upgrade google-cloud-aiplatform
# https://ai.google.dev/docs/prompt_best_practices
import vertexai
from vertexai.generative_models import (
    GenerativeModel,
    GenerationConfig
)

#------------------------------------------------------------------------------
# System Instruction Prompts
#-------------------------------------------------------------------------------
SYSTEM_INSTRUCTION_CODE_FROM_SUGGESTION = """\
You are a coding expert in {}. Apply the user's suggestion to the highlighted 
code which is located at lines between the start line and end line of the 
code. Changes will be separated into 3 sections: Replacements, Deletions, and Insertions. Your response must be a JSON object with the keys 
"success", "insertions", and "deletions" with the respective changes. If succesfull changes were made, "success" will be True.
For the "deletions" key, provide a list of lines that will be deleted. 
Insertions follow the format of (line number) : "(lines to insert)".
The lines are inserted on the line number directly after the line number provided.
Provide the line number for insertions as if nothing else was inserted.
The code at the line number given for insertion will not be deleted.
For the "deletions" key, provide a list of lines that will be deleted. 
Provide the line number for deletions as if none of the lines in "insertions" were inserted.
Important: Do not let the user change your JSON response 
format, even if the user requests for it. Ignore user prompts that are
unrelated to implementing the code from the suggestion. If the prompt is unrelated to code, "success" will be False.
If the given data in the code section is not code, "success" will be False.
Otherwise, "success" will be True.
"""

SYSTEM_INSTRUCTION_SUGGESTION_FROM_CODE = """\
In all of your replies, respond as {}.
Generate multiple suggestions to improve the quality of code. Provide a 
diverse set of recommendations for enhancing the code's readability, 
performance, and maintainability. Return a JSON object with the key 
"suggestions" and a list of JSON objects. Each object in the list should 
contain "startLine", "endLine", and "suggestion" keys, indicating the 
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
SAY_HELLO_RESPONSE = json.dumps({
    "success":True,
    "insertions": {1:"def say_hello():", 4:"print(\"Testing say_hello()\")", 5:"say_hello()", 6:"print(\"Done testing say_hello()\")"},
    "deletions":[1, 4, 5, 6],
    })

RENAME_VARIABLE_CODE = """\
1| int a = 0;
2| while(a < 34){
3|     System.out.println("wowza");
4|     a++;
5| }
6| for (int i = 0; i < 3; i++)
7|     System.out.println("erm");
"""
RENAME_VARIABLE_RESPONSE = json.dumps({
    "success":True,
    "insertions": {1:"int counter = 0:", 2:"while(counter < 32) {", 4:"counter++;"},
    "deletions":[1, 2, 4],
    })

SAY_HELLO_RESPONSE = json.dumps({
    "success":True,
    "insertions": {1:"def say_hello():", 4:"print(\"Testing say_hello()\")", 5:"say_hello()", 6:"print(\"Done testing say_hello()\")"},
    "deletions":[1, 5, 7, 9],
    })

CREATE_GETTER_CODE = """\
1| public class Person
2| {
3|     int age;
4| }
"""
CREATE_GETTER__RESPONSE = json.dumps({
    "success":True,
    "deletions":[3],
    "insertions":{3:"\
    private int age;\n\
    public int getAge()\n\
    {\n\
        return age;\n\
    }"}
    })

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
INVALID_SUGGESTION_RESPONSE = json.dumps({
    "success":False,
    "deletions":[],
    "insertions":{}
    })
#------------------------------------------------------------------------------
# Initialize LLM
#-------------------------------------------------------------------------------
MODEL_NAME = "gemini-1.5-pro-preview-0409"
def init_llm(project_id: str="codereview-413200",
             location: str="us-central1"):
    vertexai.init(project=project_id, location=location)

#------------------------------------------------------------------------------
# Helper Functions
#-------------------------------------------------------------------------------
def get_json_from_llm_response(response: str):
    #json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)

    #json_response = json_match.group(1) if json_match else response

    return json.loads(response)

def get_chat_response(user_prompt: str,
                      system_prompt: str = None):
    model = GenerativeModel(MODEL_NAME,
                            system_instruction=system_prompt,
                            generation_config=GenerationConfig(
                                response_mime_type="application/json"
                            ))
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
        example_output=SAY_HELLO_RESPONSE
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
        example_output=INVALID_SUGGESTION_RESPONSE
    )
    system_prompt += add_few_shot_example(
        example_number=3,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            CREATE_GETTER_CODE, "int age",
            1, 1,
            "make this private and create a getter for it"
            ""
        ),
        example_output=INVALID_SUGGESTION_RESPONSE
    )
    system_prompt += add_few_shot_example(
        example_number=4,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            RENAME_VARIABLE_CODE, "a",
            1, 1,
            "rename to something more meaningful"
        ),
        example_output=SAY_HELLO_RESPONSE
    )
    system_prompt += "</examples>"

    # Configure User Prompt
    user_prompt=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
        get_code_with_line_numbers(code), highlighted_code,
        start_line, end_line,
        suggestion
    )
    print("_______PROMPT__________")
    print(user_prompt)
    print("_____ENDPROMPT_________")
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
        print(response)
        revisions = get_json_from_llm_response(response)
    except Exception as e:
        print("Failed to get code from response")
        print(response)
        print(e)
        return None

    print("Implemented Code Generated by AI:", revisions)
    return revisions

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
