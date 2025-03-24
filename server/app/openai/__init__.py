"""
OpenAI client package for State Machine Demo.

This package provides a type-safe client for interacting with OpenAI's APIs,
including chat completions, responses API, DALL-E image generation, and vision.
"""

from app.openai.client.client import OpenAIClient

# Create a singleton instance for easy access
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TEST_MODE = os.getenv("OPENAI_TEST_MODE", "false").lower() == "true"
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")

# Create client instance with environment configuration
openai_client = OpenAIClient(
    api_key=OPENAI_API_KEY,
    test_mode=TEST_MODE
)

__all__ = ["OpenAIClient", "openai_client"] 