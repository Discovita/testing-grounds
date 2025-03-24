"""OpenAI Chat API operations."""

from typing import TypeVar, Type, List, Dict, Any
from openai import AsyncOpenAI
from app.openai.models.llm_response import LLMResponseModel
from app.openai.models import CompletionRequest, ChatMessage, ChatResponse

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)

T = TypeVar("T", bound=LLMResponseModel)


async def get_completion(client: AsyncOpenAI, prompt: str) -> str:
    """Get a completion from GPT-4."""
    request = CompletionRequest(messages=[ChatMessage(role="user", content=prompt)])
    log.info(f"Request data: {request.model_dump()}")
    response = await client.chat.completions.create(**request.model_dump())
    log.debug(f"Response: {response}")

    return ChatResponse.from_openai_response(response).content


async def get_structured_completion(
    client: AsyncOpenAI, messages: List[Dict[str, Any]], response_model: Type[T]
) -> T:
    """Get a structured completion from GPT-4.

    Args:
        client: OpenAI client instance
        messages: List of message dictionaries with role and content
        response_model: Pydantic model class for response validation that extends LLMResponseModel
    """
    # Get schema instruction for the response model
    schema_instruction = response_model.get_prompt_instruction()

    # Add schema instruction to the last message
    final_messages = messages[:-1]
    last_message = messages[-1].copy()
    last_message["content"] = (
        f"{last_message['content']}\n\n"
        f"Please provide a valid JSON response following this schema:\n"
        f"{response_model.model_json_schema()}\n"
        f"Do not include the schema in your response, only the data."
    )
    final_messages.append(last_message)

    request = CompletionRequest(
        messages=[ChatMessage(**msg) for msg in final_messages],
        response_format={"type": "json_object"},
        max_tokens=1000,  # Increase token limit to avoid truncation
    )
    log.info(f"Request data: {request.model_dump()}")
    response = await client.chat.completions.create(**request.model_dump())
    log.debug(f"Response: {response}")

    # Extract content from the response
    content = response.choices[0].message.content

    # Handle case where content is wrapped in markdown code blocks
    if content.startswith("```") and "```" in content[3:]:
        # Extract JSON from markdown code block
        content = content.split("```", 2)[1]
        if content.startswith("json\n"):
            content = content[5:]  # Remove "json\n" prefix
        elif content.startswith("json"):
            content = content[4:]  # Remove "json" prefix

        # Remove trailing backticks if present
        if "```" in content:
            content = content.split("```")[0]

    # Find the first valid JSON object in the content
    import json
    import re

    # Try to find a JSON object pattern
    json_pattern = r"(\{.*\})"
    matches = re.findall(json_pattern, content, re.DOTALL)

    for potential_json in matches:
        try:
            # Validate it's proper JSON by parsing it
            parsed = json.loads(potential_json)
            # If it parses successfully, use this JSON
            return response_model.model_validate(parsed)
        except json.JSONDecodeError:
            continue

    # If we couldn't find a valid JSON object, try the original content
    return response_model.model_validate_json(content)
