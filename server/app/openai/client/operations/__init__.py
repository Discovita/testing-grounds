"""OpenAI API operations."""

from .vision import describe_image_with_vision
from .chat import get_completion, get_structured_completion
from .image_generation import generate_image
from .safe_image_generation import safe_generate_image
from .responses import (
    create_response,
    call_function,
    handle_function_call_response,
    submit_function_results,
    get_structured_response,
    StructuredResponseResult
)

__all__ = [
    "describe_image_with_vision",
    
    # Chat operations
    "get_completion",
    "get_structured_completion",
    
    # Image generation operations
    "generate_image",
    "safe_generate_image",
    
    # Responses API operations
    "create_response",
    "call_function",
    "handle_function_call_response",
    "submit_function_results",
    "get_structured_response",
    "StructuredResponseResult"
]
