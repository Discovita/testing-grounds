"""OpenAI Vision API operations."""

from openai import AsyncOpenAI
from pydantic import AnyHttpUrl
from app.openai.models import (
    VisionRequest,
    ChatMessage,
    ChatResponse
)

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)

async def describe_image_with_vision(
    client: AsyncOpenAI,
    image_url: AnyHttpUrl,
    prompt: str
) -> str:
    """Get a description of an image using GPT-4 Vision."""
    request = VisionRequest(
        messages=[
            ChatMessage(
                role="system",
                content="You are trained to analyze and describe people's physical appearance in images. Your role is to provide detailed, factual descriptions of facial features, hair, and other visible physical characteristics. You should make responsible observations about race, gender, and other physical traits that would be relevant for generating an accurate image of the person."
            ),
            ChatMessage(
                role="user",
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": str(image_url)}
                    }
                ]
            )
        ]
    )
    
    log.debug(f"Request: {request.model_dump()}")
    response = await client.chat.completions.create(**request.model_dump())
    log.debug(f"Response: {response}")
    return ChatResponse.from_openai_response(response).content
