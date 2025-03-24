"""OpenAI Responses API client methods.

This module contains methods for the OpenAI Responses API that will be mixed into
the OpenAIClient class. These methods provide a high-level interface for interacting
with the Responses API, including function calling and structured outputs.
"""

from typing import Union, List, Dict, Any, TypeVar, Type, Optional, Callable, Awaitable
from openai.types.responses import Response, FunctionTool
from openai.types.responses.response_function_tool_call import ResponseFunctionToolCall
from app.openai.models.llm_response import LLMResponseModel
from app.openai.models import (
    ResponsesMessage,
)
from app.openai.client.operations.responses import (
    create_response,
    call_function,
    handle_function_call_response,
    submit_function_results,
    get_structured_response,
    StructuredResponseResult
)

T = TypeVar('T', bound=LLMResponseModel)

# These methods will be mixed into the OpenAIClient class
async def create_response_with_responses(
    self,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    model: str = "gpt-4o",
    tools: List[Dict[str, Any]] = None,
    tool_choice: Union[str, Dict[str, Any]] = None,
    store: bool = True,
    previous_response_id: str = None
) -> Response:
    """
    Create a response using the OpenAI Responses API.
    
    Args:
        input_data: String message or list of message objects
        model: Model name to use (default: gpt-4o)
        tools: List of tools to make available
        tool_choice: Tool selection strategy
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response for conversation context
        
    Returns:
        OpenAI Response object
    """
    return await create_response(
        self.client,
        input_data,
        model,
        tools,
        tool_choice,
        store,
        previous_response_id
    )

async def call_function_with_responses(
    self,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    functions: List[Union[Dict[str, Any], FunctionTool]],
    model: str = "gpt-4o",
    tool_choice: Union[str, Dict[str, Any]] = "auto",
    store: bool = True,
    previous_response_id: str = None
) -> Response:
    """
    Call a function using the OpenAI Responses API.
    
    Args:
        input_data: String message or list of message objects
        functions: List of function tools to make available
        model: Model name to use (default: gpt-4o)
        tool_choice: Tool selection strategy
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response for conversation context
        
    Returns:
        OpenAI Response object with function call
    """
    return await call_function(
        self.client,
        input_data,
        functions,
        model,
        tool_choice,
        store,
        previous_response_id
    )

async def call_functions_with_responses(
    self,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    functions: List[Union[Dict[str, Any], FunctionTool]],
    function_handlers: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Awaitable[Any]]],
    model: str = "gpt-4o",
    tool_choice: Union[str, Dict[str, Any]] = "auto",
    store: bool = True,
    previous_response_id: str = None,
    context: Dict[str, Any] = None
) -> Response:
    """
    Call functions and handle their execution automatically.
    
    This method will:
    1. Call the API with the provided functions
    2. If a function is called, execute the corresponding handler
    3. Submit the function results back to the API
    4. Return the final response
    
    Args:
        input_data: String message or list of message objects
        functions: List of function tools to make available
        function_handlers: Dict mapping function names to handler functions
        model: Model name to use (default: gpt-4o)
        tool_choice: Tool selection strategy
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response for conversation context
        context: Optional context to pass to function handlers
        
    Returns:
        OpenAI Response object with the final response after function execution
    """
    # Context defaults to empty dict if not provided
    if context is None:
        context = {}
        
    # First, get a response with function calls
    response = await call_function(
        self.client,
        input_data,
        functions,
        model,
        tool_choice,
        store,
        previous_response_id
    )
    
    # Process function calls and get function outputs
    return await handle_function_call_response(
        self.client,
        response,
        function_handlers,
        context,
        model,
        store
    )

async def submit_function_results_with_responses(
    self,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    function_outputs: Union[Dict[str, Any], List[Dict[str, Any]]],
    tools: List[Dict[str, Any]] = None,
    model: str = "gpt-4o",
    tool_choice: Union[str, Dict[str, Any]] = None,
    store: bool = True,
    previous_response_id: str = None
) -> Response:
    """
    Submit function results to the OpenAI Responses API.
    
    Args:
        input_data: String message or list of message objects
        function_outputs: Dict or list of dicts with function outputs
        tools: List of tools to make available
        model: Model name to use (default: gpt-4o)
        tool_choice: Tool selection strategy
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response for conversation context
        
    Returns:
        OpenAI Response object with the final response
    """
    return await submit_function_results(
        self.client,
        input_data,
        function_outputs,
        tools,
        model,
        tool_choice,
        store,
        previous_response_id
    )

async def get_structured_response_with_responses(
    self,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    response_model: Type[T],
    model: str = "gpt-4o",
    schema_name: Optional[str] = None,
    store: bool = True,
    previous_response_id: str = None
) -> StructuredResponseResult[T]:
    """
    Get a structured response from the OpenAI Responses API.
    
    Args:
        input_data: String message or list of message objects
        response_model: Pydantic model for the structured response
        model: Model name to use (default: gpt-4o)
        schema_name: Optional name for the schema
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response for conversation context
        
    Returns:
        StructuredResponseResult with the parsed model or error information
    """
    return await get_structured_response(
        self.client,
        input_data,
        response_model,
        model,
        schema_name,
        store,
        previous_response_id
    ) 