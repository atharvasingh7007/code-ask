"""
CodeAsk Agent — Entry Point
Exposes root_agent for ADK discovery.
"""

from dotenv import load_dotenv
load_dotenv()

from agent import root_agent

__all__ = ["root_agent"]
