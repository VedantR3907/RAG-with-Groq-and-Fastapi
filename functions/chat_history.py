import json
from typing import List, Dict

DATABASE_FILE = '../database.json'

async def read_chat_history() -> List[Dict[str, str]]:
    try:
        limit = 5
        with open(DATABASE_FILE, 'r') as file:
            data = json.load(file)
            # Return the last `limit` entries
            return data[-limit:]
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

async def format_chat_history(chat_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
    formatted_history = []
    
    for entry in chat_history:
        # Convert each entry to the new format
        if "user" in entry:
            formatted_history.append({
                "role": "user",
                "content": entry["user"]
            })
        if "assistant" in entry:
            formatted_history.append({
                "role": "assistant",
                "content": entry["assistant"]
            })
    
    return formatted_history