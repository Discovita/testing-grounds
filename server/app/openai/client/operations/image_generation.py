"""OpenAI Image Generation API operations."""

from openai import AsyncOpenAI
from app.openai.models import (
    ImageGenerationRequest,
    ImageResponse,
    GeneratedImage
)

# ------------------ Configure Logging ------------------ #
from cws_helpers.logger import configure_logging

# Configure logging for this module
log = configure_logging(__name__)

async def generate_image(
    client: AsyncOpenAI,
    prompt: str,
) -> ImageResponse:
    """Generate an image from a text prompt."""
    request = ImageGenerationRequest(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1792x1024",
        quality="standard"
    )
    log.debug(f"Request: {request.model_dump()}")
    response = await client.images.generate(**request.model_dump(exclude_none=True))
    log.debug(f"Response: {response}")
    return ImageResponse(
        created=int(response.created),
        data=[
            GeneratedImage(
                url=str(img.url),
                revised_prompt=getattr(img, "revised_prompt", prompt)
            )
            for img in response.data
        ]
    )
