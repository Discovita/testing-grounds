"""OpenAI API client implementation."""

from typing import Optional, TypeVar, Type, List, Dict, Any
from openai import AsyncOpenAI
from pydantic import AnyHttpUrl
from app.openai.models.llm_response import LLMResponseModel
from app.openai.models import (
    ImageResponse,
    OpenAIMode,
    SafeImageResponse,
)
from app.openai.client import operations
from app.openai.client.test import operations as test_operations
from app.openai.client.responses_client import (
    create_response_with_responses,
    call_function_with_responses,
    call_functions_with_responses,
    submit_function_results_with_responses,
    get_structured_response_with_responses
)




T = TypeVar('T', bound=LLMResponseModel)

class OpenAIClient:
    """Client for interacting with OpenAI's APIs (DALL-E, Vision, Chat, Responses)."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        test_mode: Optional[bool] = None
    ) -> None:
        self.mode = OpenAIMode.TEST if test_mode else OpenAIMode.LIVE
        if self.mode == OpenAIMode.LIVE and not api_key:
            raise ValueError("API key is required for live mode")
            
        self.base_url = base_url
        self.api_key = api_key
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60.0,
            max_retries=3
        )
        self.ops = test_operations if self.mode == OpenAIMode.TEST else operations

    async def get_completion(self, prompt: str) -> str:
        """Get a completion from GPT-4o."""
        return await self.ops.get_completion(self.client, prompt)

    async def get_structured_completion(
        self,
        messages: List[Dict[str, Any]],
        response_model: Type[T]
    ) -> T:
        """Get a structured completion from GPT-4o."""
        return await self.ops.get_structured_completion(
            self.client,
            messages,
            response_model
        )

    async def generate_image(self, prompt: str) -> ImageResponse:
        """Generate an image from a text prompt using DALL-E."""
        return await self.ops.generate_image(self.client, self.api_key, prompt)
    
    async def safe_generate_image(self, prompt: str) -> SafeImageResponse:
        """Generate an image with safety handling using DALL-E."""
        return await self.ops.safe_generate_image(self.client, self.api_key, prompt)
    
    async def describe_image_with_vision(self, image_url: AnyHttpUrl, prompt: str) -> str:
        """Get a description of an image using GPT-4 Vision."""
        return await self.ops.describe_image_with_vision(self.client, image_url, prompt)
    
    # Responses API methods
    create_response_with_responses = create_response_with_responses
    call_function_with_responses = call_function_with_responses
    call_functions_with_responses = call_functions_with_responses
    submit_function_results_with_responses = submit_function_results_with_responses
    get_structured_response_with_responses = get_structured_response_with_responses
