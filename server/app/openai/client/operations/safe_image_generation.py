"""OpenAI Image Generation with safety handling."""

from openai import AsyncOpenAI, APIError
from app.openai.models import SafeImageResponse
from .chat import get_completion
from .image_generation import generate_image

async def safe_generate_image(
    client: AsyncOpenAI,
    api_key: str,
    prompt: str,
) -> SafeImageResponse:
    """Generate an image with safety handling."""
    try:
        response = await generate_image(client, api_key, prompt)
        return SafeImageResponse(
            success=True,
            original_prompt=prompt,
            error=None,
            safety_violation=False,
            cleaned_prompt=None,
            data=response
        )
    except APIError as e:
        error_str = str(e)
        if "safety system" in error_str:
            system_prompt = """You are an AI that helps make image generation prompts safe and appropriate. 
            Rewrite the following prompt to remove any content that might violate content policies 
            while preserving the core intent. Focus on making the prompt family-friendly and non-violent.
            
            Original prompt: """
            
            try:
                cleaned_prompt = await get_completion(client, system_prompt + prompt)
                try:
                    response = await generate_image(client, api_key, cleaned_prompt)
                    return SafeImageResponse(
                        success=True,
                        data=response,
                        original_prompt=prompt,
                        error=None,
                        safety_violation=True,
                        cleaned_prompt=cleaned_prompt
                    )
                except APIError as retry_error:
                    return SafeImageResponse(
                        success=False,
                        error=str(retry_error),
                        safety_violation=True,
                        original_prompt=prompt,
                        data=None,
                        cleaned_prompt=cleaned_prompt
                    )
            except APIError as clean_error:
                return SafeImageResponse(
                    success=False,
                    error=str(clean_error),
                    safety_violation=True,
                    original_prompt=prompt,
                    cleaned_prompt=None,
                    data=None
                )
        return SafeImageResponse(
            success=False,
            error=error_str,
            original_prompt=prompt,
            safety_violation=False,
            cleaned_prompt=None,
            data=None
        )
