"""
CodeAsk Agent — ADK Agent for Codebase Q&A
Track 1 Project: Build and deploy an ADK agent on Cloud Run

A single AI agent that answers questions about code.
Uses Gemini for inference and maintains session memory via ContextBridge.
"""

import os
import logging

import google.cloud.logging
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.function_tool import FunctionTool

# ─── Setup ────────────────────────────────────────────────────────────────────

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
load_dotenv()

model_name = os.getenv("MODEL", "gemini-2.0-flash")
bridge_url = os.getenv("CONTEXT_BRIDGE_URL", "https://context-bridge-343602196288.us-central1.run.app")

logging.info(f"CodeAsk Agent starting with model: {model_name}")
logging.info(f"ContextBridge: {bridge_url}")

# ─── Session Memory Tools ──────────────────────────────────────────────────────

import json
import urllib.request
import urllib.error
from datetime import datetime


def save_session_memory(
    tool_context: ToolContext,
    session_id: str,
    question: str,
    answer: str,
) -> dict:
    """Save a Q&A exchange to persistent session memory."""
    url = f"{bridge_url}/sessions/{session_id}/context"

    turns = [
        {
            "role": "user",
            "content": question,
            "decisions": [],
            "entities": [],
            "metadata": {"timestamp": datetime.utcnow().isoformat()},
        },
        {
            "role": "agent",
            "content": answer,
            "decisions": [],
            "entities": [],
            "metadata": {"timestamp": datetime.utcnow().isoformat()},
        },
    ]

    data = {
        "summary": f"Q: {question[:100]} | A: {answer[:100]}",
        "turns": turns,
    }

    try:
        req = urllib.request.Request(
            url,
            method="POST",
            headers={"Content-Type": "application/json"},
            data=json.dumps(data).encode(),
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"status": "saved", "session_id": session_id}
    except Exception as e:
        logging.warning(f"Failed to save memory: {e}")
        return {"status": "error", "detail": str(e)}


def load_session_memory(
    tool_context: ToolContext,
    session_id: str,
) -> dict:
    """Load previous Q&A context for a session."""
    url = f"{bridge_url}/sessions/{session_id}/context"

    try:
        req = urllib.request.Request(url, method="GET", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            turns = data.get("turns", [])
            if turns:
                history = "\n".join(
                    f"{t['role'].upper()}: {t['content']}" for t in turns[-6:]
                )
                return {"status": "found", "history": history}
    except Exception as e:
        logging.warning(f"Failed to load memory: {e}")

    return {"status": "fresh", "history": ""}


# ─── Code Explanation Agent ───────────────────────────────────────────────────

code_analyst = Agent(
    name="code_analyst",
    model=model_name,
    description="Analyzes code and explains what it does",
    instruction="""
You are CodeAsk — an expert at reading, understanding, and explaining code.

Your task: Given a piece of code and a question, provide a clear and accurate answer.

Guidelines:
- Be specific and precise about what the code does
- Explain the logic step by step when helpful
- Keep answers focused and technical but accessible
- If the code has bugs or issues, point them out clearly
- Mention relevant programming concepts used

Always answer based on the code provided. If you're unsure, say so.
""",
)

# ─── Root Agent ───────────────────────────────────────────────────────────────

root_agent = Agent(
    name="code_ask_agent",
    model=model_name,
    description=(
        "An AI agent that answers questions about code. "
        "Provide code and ask a question — get a clear explanation."
    ),
    instruction="""
You are CodeAsk — an AI assistant that answers questions about code.

When you receive:
1. CODE — the code to analyze
2. QUESTION — what you need to explain

Your process:
1. Carefully read and understand the code
2. Answer the question clearly and precisely
3. Note any important patterns, bugs, or concerns

Format your response as a helpful technical explanation.
""",
    sub_agents=[code_analyst],
)
