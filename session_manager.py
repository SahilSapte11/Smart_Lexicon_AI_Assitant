# session_manager.py
import os
import json
from datetime import datetime
import uuid

# Base directory for storing all user chat sessions
BASE_DIR = "chat_sessions"

def _get_context_dir(username, context):
    context_dir = os.path.join(BASE_DIR, username, context)
    os.makedirs(context_dir, exist_ok=True)
    return context_dir

def list_sessions(context, username):
    context_dir = _get_context_dir(username, context)
    sessions = []
    for fname in os.listdir(context_dir):
        if fname.endswith(".json"):
            with open(os.path.join(context_dir, fname), "r") as f:
                data = json.load(f)
                sessions.append({
                    "id": data["session_id"],
                    "title": data.get("title", "Untitled"),
                    "updated_at": data.get("updated_at", data.get("created_at"))
                })
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)
    return sessions

def create_new_session(context, username, title=None):
    session_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    session = {
        "session_id": session_id,
        "title": title or "New Chat",
        "created_at": timestamp,
        "updated_at": timestamp,
        "messages": []
    }
    _save_session(context, username, session)
    return session_id

def load_session(context, session_id, username):
    session_path = os.path.join(_get_context_dir(username, context), f"{session_id}.json")
    if os.path.exists(session_path):
        with open(session_path, "r") as f:
            return json.load(f)
    return None

def save_message(context, session_id, role, content, username):
    session = load_session(context, session_id, username)
    if session is None:
        return
    session["messages"].append({"role": role, "content": content})
    if role == "user" and len(session["messages"]) == 1:
        session["title"] = content[:50]  # First user message becomes title
    session["updated_at"] = datetime.utcnow().isoformat()
    _save_session(context, username, session)

def _save_session(context, username, session_data):
    session_path = os.path.join(_get_context_dir(username, context), f"{session_data['session_id']}.json")
    with open(session_path, "w") as f:
        json.dump(session_data, f, indent=2)
