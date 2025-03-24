"""OpenAI Responses API basic operations.

This module contains basic operations for the OpenAI Responses API,
including creating responses and handling text outputs.
"""

from typing import Union, List, Dict, Any
from openai import AsyncOpenAI
from openai.types.responses import Response
from app.openai.models import ResponsesMessage, ResponsesRequest

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)


async def create_response(
    client: AsyncOpenAI,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    model: str = "gpt-4o",
    tools: List[Dict[str, Any]] = None,
    tool_choice: Union[str, Dict[str, Any]] = None,
    store: bool = True,
    previous_response_id: str = None,
) -> Response:
    """Create a response using the OpenAI Responses API.

    This function sends a request to the OpenAI Responses API and returns
    the response. It handles both text and message list inputs.

    Args:
        client: OpenAI client instance
        input_data: Input data, which can be a string or a list of messages
        model: The model to use (default: "gpt-4o")
        tools: Optional tools (including functions) available to the model
        tool_choice: Optional parameter to control which tool the model uses
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response in a conversation

    Returns:
        Response: The raw response from the OpenAI Responses API
    """
    # Convert input to the format expected by the API
    if isinstance(input_data, str):
        # If input is a string, convert it to a single user message
        messages = [{"role": "user", "content": input_data}]
    elif isinstance(input_data, list):
        if all(isinstance(msg, ResponsesMessage) for msg in input_data):
            # If input is a list of ResponsesMessage objects, convert to dicts
            messages = [msg.model_dump() for msg in input_data]
        else:
            # Assume input is already a list of message dicts
            # Filter out any messages with role other than 'user' or 'assistant'
            messages = []
            for msg in input_data:
                if msg.get("role") == "system":
                    # Convert system messages to assistant messages
                    messages.append(
                        {
                            "role": "assistant",
                            "content": f"[System instruction: {msg.get('content')}]",
                        }
                    )
                elif msg.get("role") in ["user", "assistant"]:
                    messages.append(msg)
    else:
        raise ValueError("Input must be a string or a list of messages")

    # Create the request
    request = ResponsesRequest(
        model=model,
        input=input_data if isinstance(input_data, str) else messages,
        tools=tools,
        tool_choice=tool_choice,
        store=store,
        previous_response_id=previous_response_id,
    )
    log.debug(f"Request: {request.model_dump()}")

    # Send the request to the API
    response = await client.responses.create(**request.model_dump())

    log.debug(f"Response: {response}")

    # Return the raw response
    return response
