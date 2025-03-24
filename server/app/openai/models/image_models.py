"""Image-related models for OpenAI API."""

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class OpenAIMode(str, Enum):
    """Operating mode for OpenAI client."""
    LIVE = "LIVE"
    TEST = "TEST"

class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    model: str = "dall-e-3"
    prompt: str = Field(..., description="Text description of the desired image")
    n: int = 1
    size: str = "1792x1024"  # 16:9 aspect ratio, should be under 1MB
    quality: str = "standard"

class GeneratedImage(BaseModel):
    """Single generated image result."""
    url: str = Field(..., description="URL of the generated image")
    revised_prompt: str = Field(..., description="OpenAI's augmented version of the input prompt")

class ImageResponse(BaseModel):
    """Response model for image operations."""
    created: int = Field(..., description="Unix timestamp of when the request was created")
    data: List[GeneratedImage]

class SafeImageResponse(BaseModel):
    """Response model for safe image generation with safety handling."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[ImageResponse] = Field(None, description="Generated image data if successful")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    safety_violation: bool = Field(False, description="Whether a safety violation occurred")
    original_prompt: str = Field(..., description="Original prompt that was submitted")
    cleaned_prompt: Optional[str] = Field(None, description="Cleaned prompt if safety violation occurred")
