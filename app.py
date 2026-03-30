"""
ASGI app wrapper for CodeAsk Agent on Cloud Run.
ADK's get_web_app with agent_loader for auto-discovery.
"""

from google.adk.cli.fast_api import get_web_app
from google.adk.agents import BaseAgentLoader
from dotenv import load_dotenv
load_dotenv()

from agent import root_agent

class AgentLoader(BaseAgentLoader):
    def load(self):
        return root_agent

app = get_web_app(agent_loader=AgentLoader(), web=True)

if __name__ == "__main__":
    import uvicorn, os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
