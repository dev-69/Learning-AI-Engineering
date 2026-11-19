import os
from types import SimpleNamespace

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


from tools import TOOLS,run_tool
from utilities.utilities import log



client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

messages = []

MAX_STEPS = 5
# max number of tool calls for a user's question

messages.append(
    {
        "role": "system",
        "content": (
            "You are a helpful, humble AI assistant. Use your tools whenever needed. "
            "When a tool returns detailed information, present a clear, well-structured, "
            "and complete answer to the user."
        )
    }
)

def stream_chat(history):
    stream = client.chat.completions.create(    
        model=os.getenv("MODEL"),
        messages=history,
        tools=os.getenv("TOOLS"),
        stream=True,
    )

    full_response = ""
    calls = {}
    label_printed = False

    try:
        for chunk in stream:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta

            #do we have message content for the LLM
            if delta.content:
                if not label_printed:
                    print("Assistant: ", end="", flush=True)
                    label_printed = True
                print(delta.content, end="", flush=True)
                full_response += delta.content

            #do we have tool calls for the LLM
            for tc in (delta.tool_calls or []):
                obj = calls.setdefault(
                    tc.index, 
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguements=""))
                )
            
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
        print("\n {Stopped by you}")
        calls = {}
    
    if label_printed:
        print()

    calls_list = []
    for key in sorted(calls):
        calls_list.append(calls[key])

    return full_response, calls_list


def build_tool_calls_payload(tool_calls):
    """
    Converts our expected tool calls into the dictionary format that the 
    API expects inside an assistant message 
    """

    payload = []
    for tool_call in tool_calls:
        tool_call_dict = {
            "id" : tool_call.id,
            "type" : "function",
            "function": {
                "name" : tool_call.function.name,
                "arguments" : tool_call.function.arguments
            },
        }
        payload.append(tool_call_dict)
    return payload



while True:

    user_input = input("\nYou: ")

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        break

    messages.append(
        {
            "role":"user",
            "content":user_input
        }
    )

    #Chained Tool Calling
    for step in range(MAX_STEPS):

        full_response, tool_calls = stream_chat(messages)

        # response = client.chat.completions.create(
        #     model=os.getenv("MODEL"),
        #     messages=messages,
        #     tools=TOOLS
        # )

        # msg = response.choices[0].message

        if not tool_calls:
            break

        log(f"  Step {step+1} : model requested {len(tool_calls)} tool calls ")


        #  messages.append(msg) <-- we have to build this part msg now it consists of role, content, tool_calls
        messages.append({
            "role" : "assistant",
            "content" : full_response,
            "tool_calls" : build_tool_calls_payload(tool_calls)
        })

        for tool_call in tool_calls:
            result = run_tool(tool_call)

            messages.append({
                "role" : "tool",
                "tool_id" : tool_call.id,
                "content" : str(result)
            })
    else :
        fallback = "Sorry, exhausted the number of tool calling set by the developer"
        messages.append({
            "role" : "assistant",
            "content" : fallback
        })
        print("Assistant: " + fallback)
        continue

    # messages.append({
    #     "role" : "assistant",
    #     "content" : msg.content
    # })

    # print("Assistant: " + (msg.content or ""))
    
    #  removing everything because we are already doing it before in the earlier loop
