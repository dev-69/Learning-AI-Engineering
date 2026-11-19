import os

from openai import OpenAI
from dotenv import load_dotenv

from tools import TOOLS,run_tool
from utilities.utilities import log

load_dotenv()


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

        log(f"  Step {step+1} : model requested {len(msg.tool_calls)} tool calls ")


        messages.append(msg)

        for tool_call in msg.tool_calls:
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

    messages.append({
        "role" : "assistant",
        "content" : msg.content
    })

    print("Assistant: " + (msg.content or ""))
