import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CHAT_FOLDER = os.getenv("CHAT_FOLDER")

# loading chat from the path
def load_chat(path):
    with open(path, "r", encoding="utf -8") as f:
        data = json.load(f)

    return data

def save_chat(path, messages):

    os.makedirs(CHAT_FOLDER, exist_ok=True)

    # path -> None the chat is happening for the first time
    if path is None:
        fileName = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
        path = os.path.join(CHAT_FOLDER, f"{fileName}.json")

    data = {
        "title" : messages[0]["content"][:40],
        "updated" : datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        "messages" : messages,
    }

    # write to a temporary file first, then replace
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp_path, path)

    return path

# most recently edited/updatedd first
def list_chats():

    # if the path does not exist
    if not os.path.exists(CHAT_FOLDER):
        return []

    chats = []

    for chat_file_name in os.listdir(CHAT_FOLDER):
        if not chat_file_name.endswith(".json"):
            continue

        path = os.path.join(CHAT_FOLDER, chat_file_name)

        data = load_chat(path)

        if data is None:
            print(f"Skipping unreadable piece of shit -> {chat_file_name}\n")
            continue

        chats.append({
            "path" : path,
            "title": data.get("title", "(untitled)"),
            "updated" : data.get("updated"),
            "count" : len(data.get("messages"))
        })

        
    chats.sort(key=lambda chat:chat["updated"], reverse=True)
    return chats
    

