"""
ASGI app wrapper for CodeAsk Agent on Cloud Run.
Uses ADK's built-in web server for agent interaction.
"""

import os
from google.adk.cli.fast_api import get_web_app

from agent import root_agent

app = get_web_app(agent=root_agent)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
