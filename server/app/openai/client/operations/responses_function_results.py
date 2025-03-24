"""OpenAI Responses API function results operations.

This module contains operations for submitting function results to the OpenAI Responses API
and handling the final response.
"""

from typing import Union, List, Dict, Any
from openai import AsyncOpenAI
from openai.types.responses import Response
from app.openai.models import (
    ResponsesMessage,
)

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)


async def submit_function_results(
    client: AsyncOpenAI,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    function_outputs: Union[Dict[str, Any], List[Dict[str, Any]]],
    tools: List[Dict[str, Any]] = None,
    model: str = "gpt-4o",
    tool_choice: Union[str, Dict[str, Any]] = None,
    store: bool = True,
    previous_response_id: str = None,
) -> Response:
    """Submit function results to the OpenAI Responses API.

    This function sends function results back to the OpenAI Responses API
    and returns the final response. It uses the previous_response_id to reference
    the response containing the function calls.

    Args:
        client: OpenAI client instance
        input_data: Input data, which can be a string or a list of messages
        function_outputs: Function outputs to submit. Each output should be a dictionary
                         with 'tool_call_id' and 'output' keys.
        tools: Optional tools (including functions) available to the model
        model: The model to use (default: "gpt-4o")
        tool_choice: Optional parameter to control which tool the model uses
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response in a conversation

    Returns:
        Response: The response from the OpenAI Responses API
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
            messages = input_data.copy()  # Make a copy to avoid modifying the original
    else:
        raise ValueError("Input must be a string or a list of messages")

    # Process function outputs and add them as function_call_output messages
    if function_outputs:
        if isinstance(function_outputs, list):
            for output in function_outputs:
                if "tool_call_id" in output and "output" in output:
                    # Add as function_call_output message
                    messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": output["tool_call_id"],
                            "output": output["output"],
                        }
                    )
                else:
                    # Invalid format
                    raise ValueError(f"Invalid function output format: {output}")
        else:
            # Single output, not a list
            if "tool_call_id" in function_outputs and "output" in function_outputs:
                # Add as function_call_output message
                messages.append(
                    {
                        "type": "function_call_output",
                        "call_id": function_outputs["tool_call_id"],
                        "output": function_outputs["output"],
                    }
                )
            else:
                # Invalid format
                raise ValueError(f"Invalid function output format: {function_outputs}")

    # Create the request parameters for the Responses API
    request_params = {
        "model": model,
        "input": messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "store": store,
        "previous_response_id": previous_response_id,
    }

    # Remove None values
    request_params = {k: v for k, v in request_params.items() if v is not None}

    log.info(f"Request Params: {request_params}")

    # Send the request to the API
    response = await client.responses.create(**request_params)

    log.debug(f"Response: {response}")

    # Return the raw response
    return response
