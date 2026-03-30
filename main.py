"""
CodeAsk Agent — ADK Entry Point
Follows the codelab pattern from:
  "Build and deploy an ADK agent on Cloud Run"
"""

import os
import logging

import google.cloud.logging
from dotenv import load_dotenv

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()
logging.info("CodeAsk Agent starting...")

load_dotenv()

from agent import root_agent

__all__ = ["root_agent"]
