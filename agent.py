"""
CodeAsk Agent — ADK Agent for Codebase Q&A
Track 1 Project: GenAI Academy APAC 2026
"""

import os
# Load env FIRST before any other imports
from dotenv import load_dotenv
load_dotenv()

import logging
import google.cloud.logging
cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext

model_name = os.getenv("MODEL", "gemini-2.0-flash")
bridge_url = os.getenv(
    "CONTEXT_BRIDGE_URL",
    "https://context-bridge-343602196288.us-central1.run.app"
)
logging.info(f"CodeAsk starting with model: {model_name}")
logging.info(f"ContextBridge: {bridge_url}")

# Memory tools using urllib (no external deps)
import json, urllib.request, urllib.error
from datetime import datetime

def save_session_memory(tool_context: ToolContext, session_id: str, question: str, answer: str) -> dict:
    url = f"{bridge_url}/sessions/{session_id}/context"
    data = {
        "summary": f"Q: {question[:80]} | A: {answer[:80]}",
        "turns": [
            {"role": "user", "content": question, "decisions": [], "entities": [], "metadata": {"ts": datetime.utcnow().isoformat()}},
            {"role": "agent", "content": answer, "decisions": [], "entities": [], "metadata": {"ts": datetime.utcnow().isoformat()}},
        ],
    }
    try:
        req = urllib.request.Request(url, method="POST", headers={"Content-Type": "application/json"}, data=json.dumps(data).encode())
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"status": "saved", "code": resp.status}
    except Exception as e:
        logging.warning(f"Memory save failed: {e}")
        return {"status": "error"}

def load_session_memory(tool_context: ToolContext, session_id: str) -> dict:
    url = f"{bridge_url}/sessions/{session_id}/context"
    try:
        req = urllib.request.Request(url, method="GET", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            turns = data.get("turns", [])
            if turns:
                history = "\n".join(f"{t['role'].upper()}: {t['content']}" for t in turns[-6:])
                return {"status": "found", "history": history}
    except Exception as e:
        logging.warning(f"Memory load failed: {e}")
    return {"status": "fresh", "history": ""}

root_agent = Agent(
    name="code_ask_agent",
    model=model_name,
    description="An AI agent that explains code. Provide code and a question — get a clear technical explanation.",
    instruction=(
        "You are CodeAsk — an expert at reading and explaining code.\n"
        "When given code and a question: read carefully, then answer clearly.\n"
        "Explain what the code does, how it works, and any potential issues.\n"
        "Keep answers technical but accessible."
    ),
    tools=[save_session_memory, load_session_memory],
)
