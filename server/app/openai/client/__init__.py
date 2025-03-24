"""OpenAI DALL-E client package."""

from .client import OpenAIClient
import logging as python_logging

# Configure root logger
python_logging.basicConfig(level=python_logging.INFO)


__all__ = ["OpenAIClient"]
