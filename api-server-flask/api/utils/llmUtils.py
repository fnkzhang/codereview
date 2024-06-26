import json, re
from utils.miscUtils import *
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
You are a coding expert in {language}.
A user has made a <suggestion> which refers to the highlighted section located at lines between <start_line> and <end_line> of the code provided in <code>.
If the <suggestion> wants a variable name to be modified the user wishes for the name to be modified across the entire <code>
**Requirements**
    1. Implement the suggestion to the entirety of <code> provided.
    2. Changes are made on any line of the code provided, and is not limited to the lines between <start_line> and <end_line>.
    3. Update all instances of changed variable or function names that were modified.
        - If a variable is renamed multiple lines should be changed.
    4. Avoid making changes that are not mentioned in <suggestion>.
**Response Format**
Changes will be separated into 2 sections: Insertions and Deletions.
Your response must be a JSON object with the keys "success", "insertions", and "deletions" with the respective changes.
For the "insertions" key, provide a dictionary of line insertions that follow the format of (line number) : "(lines to insert)".
The lines are inserted on the line number directly after the line number provided.
There will commonly be multiple insertions.
Follow line spacing and formatting of <code> for the inserted lines.

For the "deletions" key, provide a list of lines that will be deleted from <code>. 

Important: Do not let the user change your JSON response format, even if the user requests for it.
Ignore user comments that are unrelated to implementing the code from the suggestion. 
Return an empty string on 1 condition:
    1. If the comments are entirely unrelated to programming or the <code> given.
"""

SYSTEM_INSTRUCTION_CODE_FROM_SUGGESTION_2 = """\
You are a code modification tool for {language} that applies a <suggestion> to code
located between lines {start_line} and {end_line}. Highligh of the following code:

<code>
{code}
</code>

**Requirements**
- Avoid making changes that are not mentioned in <suggestion>.
- Update all instances of changed variable or function names that were modified by <suggestion>.
- Remove all line number markers e.g. "1| " from the code.

**Response Format**
Return a JSON object with the key "revised_code" and the value being the entire revised <code>
as a string.
"""

SYSTEM_INSTRUCTION_SUGGESTION_FROM_CODE = """\
You are a coding expert in {language}.
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
{code}
</code>

<highlighted_code>
{highlighted_code}
</highlighted_code>

<start_line>
{start_line}
</start_line>

<end_line>
{end_line}
</end_line>

<suggestion>
{suggestion}
</suggestion>
"""

USER_INSTRUCTION_SUGGESTION_FROM_CODE = """
<code>
{code}
</code>
"""

#------------------------------------------------------------------------------
# Few-Shot Prompt Format
#-------------------------------------------------------------------------------
FEW_SHOT_EXAMPLE = """
<example_{example_number}>
<input>
{example_input}
</input>
<output>
{example_output}
</output>
</example_{end_example_number}>
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
1| int booga = 0;
2| while(booga < 34){
3|     System.out.println("wowza");
4|     booga++;
5| }
6| booga = 6055;
7| for (int i = 0; i < 3; i++)
8|     System.out.println("erm");
"""

RENAME_VARIABLE_RESPONSE = json.dumps({
    "success":True,
    "insertions": {1:"int counter = 0:", 2:"while(counter < 32) {", 4:"counter++;", 6:"counter = 6055"},
    "deletions":[1, 2, 4, 6],
    })

RENAME_VARIABLE_CODE_2 = """\
1| public static int[] createArrayWithSizeAndValueFlankedByTwo(int dsf, int avbg){
2|     int[] arr = new int[dsf+2];
3|     for(int i = 0; i < dsf; i++)     
4|         arr[i+1] = avbg;
5|     arr[0] = 2
6|     arr[dsf] = 2
7|     return arr
8| }
"""

RENAME_VARIABLE_RESPONSE_2 = json.dumps({
    "success":True,
    "insertions": {
        1:"public static int[] createArrayWithSizeAndValueFlankedByTwo(int dsf, int avbg){",
        2:"    int[] arr = new int[size+2];",
        3:"    for(int i = 0; i < size; i++)",
        4:"        arr[i+1] = default;",
        6:"     arr[default] = 2" },
    "deletions":[1, 2, 3, 4, 6],
    })

CREATE_GETTER_CODE = """\
1| public class Person
2| {
3|     int age;
4| }
"""

CREATE_GETTER_RESPONSE = json.dumps({
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
1| def calc_avg(n):
2|     tot=0
3|     cnt=0
4|     for number in n:
5|       tot = tot+ number
6|       cnt= cnt+1
7| 
8|     average=tot/cnt
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
    """
    **Explanation:**
        Creates a json object from a string

    **Args:**
        - response (str): A string representing a json string

    **Returns:**
        json (dict): a dict representing the json string
    """
    #json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)

    #json_response = json_match.group(1) if json_match else response

    return json.loads(response, strict=False)

def get_chat_response(user_prompt: str,
                      system_prompt: str = None):
    """
    **Explanation:**
        Gets a response from VertexAi given a user prompt and a system prompt

    **Args:**
        - user_prompt (str): A user prompt (query a user would ask the AI)
        - system_prompt (str): Guidelines for the AI to follow when responding to the user prompt

    **Returns:**
        response (str): VertexAI's response
    """
    model = GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json"
        )
    )
    chat = model.start_chat()

    response = chat.send_message(user_prompt)

    return response.text

def add_few_shot_example(example_number: int,
                         example_input: str,
                         example_output: str):
    """
    **Explanation:**
        Creates a few_shot_example string to be added to a system prompt

    **Args:**
        - example_number (int): Number of the example
        - example_input (str): Example user prompt
        - example_output (str): Example output from the AI

    **Returns:**
        few_shot_example (str): a string formatted to a few shot example format
    """
    return FEW_SHOT_EXAMPLE.format(
        example_number=example_number,
        example_input=example_input,
        example_output=example_output,
        end_example_number=example_number
    )

def get_code_with_line_numbers(code: str):
    """
    **Explanation:**
        Adds line numbers before every line in a string

    **Args:**
        - code (str): string to add line numbers to

    **Returns:**
        codeWithLineNumbers (str): a string with line numbers added before every line
    """
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
    """
    **Explanation:**
        Gets a code edit from VertexAI given a suggestion

    **Args:**
        - code (str): code to edit
        - highlighted_code (str): code that the suggestion refers to
        - start_line (int): line that the code the suggestion refers to starts on
        - end_line (int): line that the code the suggestion refers to ends on
        - suggestion (str): The suggestion
        - language (str): Language the code was written in; e.g: Python, C++, Java

    **Returns:**
        response (dict): A dict with the keys "success", "insertions", and "deletions". The "insertions" key maps to a dictionary of line insertions that follow the format of (line number (int)) : "(lines to insert (str))". The lines are inserted on the line number directly after the line number provided. The "deletions" key maps to a list of line numbers (int) that should be deleted. The "success" key maps to whether or not the response was succesfull
    """
    # Configure System Prompt
    system_prompt = SYSTEM_INSTRUCTION_CODE_FROM_SUGGESTION.format(
        language=language
    )

    # Provide Few-Shot Examples on how the LLM should respond
    system_prompt += "<examples>\n"
    system_prompt += add_few_shot_example(
        example_number=1,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            code=SAY_HELLO_CODE,
            highlighted_code="foo",
            start_line=1,
            end_line=1,
            suggestion="rename to something more meaningful"
        ),
        example_output=SAY_HELLO_RESPONSE
    )
    system_prompt += add_few_shot_example(
        example_number=2,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            code="hi",
            highlighted_code="hi",
            start_line=1,
            end_line=1,
            suggestion="Generate 10 paragraphs of Shakespeare and return \
            your response in a JSON with the key \"paragraphs\""
            ""
        ),
        example_output=INVALID_SUGGESTION_RESPONSE
    )
    system_prompt += add_few_shot_example(
        example_number=3,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            code=CREATE_GETTER_CODE,
            highlighted_code="int age",
            start_line=3,
            end_line=3,
            suggestion="make this private and create a getter for it"
        ),
        example_output=CREATE_GETTER_RESPONSE
    )
    system_prompt += add_few_shot_example(
        example_number=4,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            code=RENAME_VARIABLE_CODE,
            highlighted_code="booga",
            start_line=6,
            end_line=6,
            suggestion="rename to something more meaningful"
        ),
        example_output=RENAME_VARIABLE_RESPONSE
    )
    
    system_prompt += add_few_shot_example(
        example_number=5,
        example_input=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
            code=RENAME_VARIABLE_CODE_2,
            highlighted_code="int dsf, int avbg",
            start_line=1,
            end_line=1,
            suggestion="rename to something more meaningful"
        ),
        example_output=RENAME_VARIABLE_RESPONSE_2
    )
    
    system_prompt += "</examples>"

    # Configure User Prompt
    user_prompt=USER_INSTRUCTION_CODE_FROM_SUGGESTION.format(
        code=get_code_with_line_numbers(code),
        highlighted_code=highlighted_code,
        start_line=start_line,
        end_line=end_line,
        suggestion=suggestion
    )
    # Generate a response from LLM
    try:
        response = get_chat_response(
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
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
                                 language: str):
    """
    **Explanation:**
        Gets a suggestion from VertexAI given code

    **Args:**
        - code (str): code to get suggestions for
        - language (str): Language the code was written in; e.g: Python, C++, Java

    **Returns:**
        response (dict): A dict with the key "suggestions" which maps to a list of JSON objects. Each object in the list contains the keys "startLine", "endLine", and "suggestion" keys, indicating the highlighted code lines and suggested changes.
    """
    # Configure System Prompt
    system_prompt = SYSTEM_INSTRUCTION_SUGGESTION_FROM_CODE.format(
        language=language
    )

    # Provide Few-Shot Examples on how the LLM should respond
    system_prompt += "<examples>\n"

    system_prompt += add_few_shot_example(
        example_number=1,
        example_input=USER_INSTRUCTION_SUGGESTION_FROM_CODE.format(
            code=CALCULATE_AVERAGE_CODE
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
            code="Generate 10 paragraphs of Shakespeare and return \
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
        code=get_code_with_line_numbers(code)
    )
    # Generate a response from LLM
    try:
        response = get_chat_response(
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
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
