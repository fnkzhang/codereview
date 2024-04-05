from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
import torch

device = None
tokenizer = None
model = None

def init_llm():
    global device, tokenizer, model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct",
                                              trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained("deepseek-ai/deepseek-coder-1.3b-instruct",
                                                 trust_remote_code=True,
                                                 torch_dtype=torch.bfloat16).to(device)

def query_llm(system_prompt,
              user_prompt,
              max_new_tokens=128):
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    inputs = tokenizer.apply_chat_template(messages,
                                           tokenize=True,
                                           add_generation_prompt=True,
                                           return_tensors="pt").to(device)
    # streamer skip_prompt=True: display the response in terminal
    # streamer skip_prompt=False: display system prompt, instruction, and response in terminal
    streamer = TextStreamer(tokenizer, skip_prompt=False, skip_special_tokens=True)
    outputs = model.generate(inputs,
                             max_new_tokens=max_new_tokens,
                             do_sample=True,
                             temperature=0.75,
                             streamer=streamer)
    response = tokenizer.decode(outputs[0][len(inputs[0]):],
                                skip_special_tokens=True)
    
    return response

def get_llm_code_from_suggestion(old_code, coding_language, suggestion):
    system_prompt = (
        "You are a code editor. Your task is to implement the suggestion "
        "to the given code while adhering to best practices.\n"
    )

    user_prompt = (
        f"```{coding_language}\n"
        f"{old_code}\n"
        "```\n"
        f"Here is a suggestion to improve the code: {suggestion}\n"
        "Revise the code to implement the suggestion.\n"
    )

    try:
        new_code = query_llm(system_prompt=system_prompt,
                             user_prompt=user_prompt,
                             max_new_tokens=len(old_code)+128)
    except Exception as e:
        return None
    
    return new_code

def get_llm_suggestion_from_code(code, coding_language):
    system_prompt = (
        "You are a code reviewer. Your task is to identify mistakes such as "
        "overly complex code, unclear variable names, temporary or "
        "commented out code, unhandled edge cases, or long functions that "
        "need to be refactored, then explain how those changes would improve "
        "the code.\n"
    )

    user_prompt = (
        f"```{coding_language}\n"
        f"{code}\n"
        "```\n"
        "Identify an issue with the code, and explain how a "
        "possible revision would improve the code.\n"
    )

    try:
        suggestion = query_llm(system_prompt=system_prompt,
                             user_prompt=user_prompt,
                             max_new_tokens=500)
    except Exception as e:
        return None

    return suggestion
