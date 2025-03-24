"""OpenAI Responses API function calling operations.

This module contains operations for function calling with the OpenAI Responses API,
including calling functions and handling function call responses.
"""

from typing import Union, List, Dict, Any, Callable, Awaitable
from openai import AsyncOpenAI
from openai.types.responses import Response, FunctionTool
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
import json
from app.openai.models import (
    ResponsesMessage,
)

from .responses_basic import create_response
from .responses_function_results import submit_function_results

async def call_function(
    client: AsyncOpenAI,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    functions: List[Union[Dict[str, Any], FunctionTool]],
    model: str = "gpt-4o",
    tool_choice: Union[str, Dict[str, Any]] = "auto",
    store: bool = True,
    previous_response_id: str = None
) -> Response:
    """Call a function using the OpenAI Responses API.
    
    This function sends a request to the OpenAI Responses API with function
    definitions and returns the response, which may include function calls.
    
    Args:
        client: AsyncOpenAI client
        input_data: Input data, which can be a string or a list of messages
        functions: List of function definitions
        model: The model to use (default: "gpt-4o")
        tool_choice: Control which tool the model uses (default: "auto")
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response in a conversation
        
    Returns:
        Response: The response from the OpenAI Responses API
    """
    # Convert function definitions to tools if needed
    tools = []
    for func in functions:
        if isinstance(func, dict) and func.get("type") == "function":
            tools.append(func)
        elif isinstance(func, FunctionTool):
            tools.append(func.model_dump())
        else:
            raise ValueError(f"Unsupported function type: {type(func)}")
    
    # Call the API with the tools
    return await create_response(
        client=client,
        input_data=input_data,
        model=model,
        tools=tools,
        tool_choice=tool_choice,
        store=store,
        previous_response_id=previous_response_id
    )

async def handle_function_call_response(
    client: AsyncOpenAI,
    response: Response,
    function_handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[Any]]],
    context: Dict[str, Any] = None,
    model: str = "gpt-4o",
    store: bool = True
) -> Response:
    """Handle function call responses from the OpenAI Responses API.
    
    This function processes function calls in a response, executes the appropriate
    handlers, and returns the results.
    
    Args:
        client: AsyncOpenAI client
        response: Response from the OpenAI Responses API
        function_handlers: Dictionary mapping function names to handler functions
        context: Additional context to pass to the function handlers
        model: The model to use for follow-up requests (default: "gpt-4o")
        store: Whether to store the response for future reference
        
    Returns:
        Response: Final response after function execution or the original response if no functions called
    """
    # Default context
    if context is None:
        context = {}
        
    # Check if there are function calls in the response
    function_calls = [output for output in response.output if isinstance(output, ResponseFunctionToolCall)]
    
    if not function_calls:
        return response  # No function calls to handle
    
    # Process function calls
    outputs = []
    for func_call in function_calls:
        tool_call_id = func_call.id
        func_name = func_call.name
        
        if func_name not in function_handlers:
            outputs.append({
                "tool_call_id": tool_call_id,
                "output": f"Error: No handler for function '{func_name}'"
            })
            continue
        
        try:
            # Parse arguments
            args = {}
            if func_call.arguments:
                try:
                    args = json.loads(func_call.arguments)
                except json.JSONDecodeError:
                    outputs.append({
                        "tool_call_id": tool_call_id,
                        "output": f"Error: Could not parse arguments: {func_call.arguments}"
                    })
                    continue
            
            # Call handler
            result = await function_handlers[func_name](args, context)
            
            # Add result to outputs
            outputs.append({
                "tool_call_id": tool_call_id,
                "output": str(result)
            })
        except Exception as e:
            outputs.append({
                "tool_call_id": tool_call_id,
                "output": f"Error executing function: {str(e)}"
            })
    
    # Submit function results and return final response
    return await submit_function_results(
        client=client,
        input_data=[],  # Empty input because we're continuing from previous response
        function_outputs=outputs,
        model=model,
        store=store,
        previous_response_id=response.id
    ) 