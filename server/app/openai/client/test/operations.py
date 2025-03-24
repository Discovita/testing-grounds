"""Test operations that return static responses."""

from pathlib import Path
from typing import TypeVar, Type, List, Dict, Any
from openai import AsyncOpenAI
from pydantic import AnyHttpUrl, BaseModel
from app.openai.models import (
    ImageResponse,
    GeneratedImage,
    SafeImageResponse
)

T = TypeVar('T', bound=BaseModel)

DUMMY_IMAGE_PATH = Path("backend/src/discovita/service/icons8/client/example_images/base_face_darth.png")

async def safe_generate_image(
    client: AsyncOpenAI,
    api_key: str,
    prompt: str,
) -> SafeImageResponse:
    """Return dummy safe image generation response."""
    response = ImageResponse(
        created=1234567890,
        data=[
            GeneratedImage(
                url="https://api.openai.com/test/safe-image.png",
                revised_prompt=f"A highly detailed digital art {prompt}, 8k resolution, cinematic lighting"
            )
        ]
    )
    return SafeImageResponse(
        success=True,
        original_prompt=prompt,
        error=None,
        safety_violation=False,
        cleaned_prompt=None,
        data=response
    )

async def describe_image_with_vision(
    client: AsyncOpenAI,
    image_url: AnyHttpUrl,
    prompt: str
) -> str:
    """Return dummy image description."""
    return "A person with dark brown hair, hazel eyes, and a warm smile. They have defined cheekbones and a strong jawline."

async def get_completion(client: AsyncOpenAI, prompt: str) -> str:
    """Return dummy completion."""
    return "Dark brown hair, hazel eyes, defined cheekbones, strong jawline."

async def get_structured_completion(
    client: AsyncOpenAI,
    messages: List[Dict[str, Any]],
    response_model: Type[T]
) -> T:
    """Return dummy structured completion."""
    # Return a basic instance of the response model
    return response_model.model_validate({})

async def generate_image(
    client: AsyncOpenAI,
    api_key: str,
    prompt: str,
) -> ImageResponse:
    """Return dummy image URL."""
    return ImageResponse(
        created=1234567890,
        data=[
            GeneratedImage(
                url="https://api.openai.com/test/image.png",  # Use https URL for test
                revised_prompt=f"A highly detailed digital art {prompt}, 8k resolution, cinematic lighting"
            )
        ]
    )
