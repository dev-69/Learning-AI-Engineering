from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from tools import TOOLS, FUNCTION_NAME_TO_FUNCTION_MAP

import os
import json


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

        response = client.chat.completions.create(
            model=os.getenv("MODEL"),
            messages=messages,
            tools=TOOLS
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        messages.append(msg)

        for tool_call in msg.tool_calls:
            func_name = tool_call.function.name
            func_args = {}

            try: 
                func_args = json.loads(tool_call.function.arguments or "{}")
                #print(f"  [Tool] Calling {func_name}({func_args})")
                fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
                result = fn(**func_args)
                #print(f"  [Tool Result]\n{result}\n")
            except Exception as e: 
                result = f"Error while running the function {func_name} : {e}"

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

    messages.append({
        "role" : "assistant",
        "content" : msg.content
    })

    print("Assistant: " + msg.content)
