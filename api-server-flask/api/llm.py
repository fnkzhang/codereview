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
              assistant_prompt,
              max_new_tokens=128):
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        },
        {
            "role": "assistant",
            "content": assistant_prompt
        }
    ]

    inputs = tokenizer.apply_chat_template(messages,
                                           tokenize=True,
                                           add_generation_prompt=True,
                                           return_tensors="pt").to(device)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    outputs = model.generate(inputs,
                             max_new_tokens=max_new_tokens,
                             streamer=streamer)
    response = tokenizer.decode(outputs[0][len(inputs[0]):],
                                skip_special_tokens=True)
    
    return response

def get_llm_code_from_suggestion(old_code, suggestion):
    system_prompt = (
        "Implement code changes based on the user's comment"
        "while adhering to best practices."
    )

    user_prompt = (
        f"Code: {old_code}"
        f"Comment Suggestion: {suggestion}"
    )

    assistant_prompt = (
        "Here is the code:\n"
    )

    try:
        new_code = query_llm(system_prompt=system_prompt,
                             user_prompt=user_prompt,
                             assistant_prompt=assistant_prompt,
                             max_new_tokens=len(old_code)+128)
    except Exception as e:
        return None
    
    return new_code
