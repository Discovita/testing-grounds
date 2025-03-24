"""OpenAI Responses API structured outputs operations.

This module contains operations for getting structured outputs from the OpenAI Responses API
using JSON schemas.
"""

from typing import Union, List, Dict, Any, TypeVar, Type, Optional, Generic
import json
from openai import AsyncOpenAI
from openai.types.responses import Response
from openai.types.responses.response_output_text import ResponseOutputText
from pydantic import BaseModel
from app.openai.models import (
    ResponsesMessage,
    StructuredOutputSchema,
    LLMResponseModel,
)

from .responses_basic import create_response

T = TypeVar("T", bound=LLMResponseModel)


class StructuredResponseResult(BaseModel, Generic[T]):
    """Result of a structured response operation.

    This model represents the result of a structured response operation,
    including the raw response, parsed data, and validation status.
    """

    response: Response
    parsed: Optional[T] = None
    is_valid: bool = False
    error: Optional[str] = None


async def get_structured_response(
    client: AsyncOpenAI,
    input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]],
    response_model: Type[T],
    model: str = "gpt-4o",
    schema_name: Optional[str] = None,
    store: bool = True,
    previous_response_id: str = None,
) -> StructuredResponseResult[T]:
    """Get a structured response from the OpenAI Responses API.

    This function sends a request to the OpenAI Responses API with a JSON schema
    and returns the response, which should adhere to the schema.

    Args:
        client: OpenAI client instance
        input_data: Input data, which can be a string or a list of messages
        response_model: Pydantic model class for response validation
        model: The model to use (default: "gpt-4o")
        schema_name: Optional name for the schema (default: model class name)
        store: Whether to store the response for future reference
        previous_response_id: ID of the previous response in a conversation

    Returns:
        StructuredResponseResult: The result of the structured response operation
    """
    # Create a schema from the response model
    schema = StructuredOutputSchema.from_llm_response_model(
        response_model, name=schema_name
    )

    # Create the response with the schema as a tool
    response = await create_response(
        client=client,
        input_data=input_data,
        model=model,
        tools=[schema.model_dump()],
        tool_choice={"type": "structured_output", "name": schema.name},
        store=store,
        previous_response_id=previous_response_id,
    )

    # Create the result
    result = StructuredResponseResult(response=response)

    # Check if there's a text output in the response
    text_output = None
    for output_item in response.output:
        if isinstance(output_item, ResponseOutputText):
            text_output = output_item.text
            break

    if text_output:
        try:
            # Parse the JSON output
            data = json.loads(text_output)

            # Validate the data against the model
            parsed = response_model.model_validate(data)

            # Update the result
            result.parsed = parsed
            result.is_valid = True
        except Exception as e:
            # Update the result with the error
            result.error = str(e)

    return result
