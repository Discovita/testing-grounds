"""Service for getting clean descriptions of headshot images."""

from pydantic import AnyHttpUrl
from .client.client import OpenAIClient

class ImageDescriptionService:
    """Service for getting clean descriptions of headshot images."""
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    async def get_clean_description(self, image_url: AnyHttpUrl) -> str:
        """Get a clean description of a headshot image.
        
        This is a two-step process:
        1. Get a detailed description using GPT-4 Vision
        2. Clean up the description using GPT-4o to remove irrelevant details
        """
        # Step 1: Get initial description
        initial_description = await self.client.describe_image_with_vision(
            image_url,
            "Describe this person's physical appearance in detail. Focus on "+
            "their facial features, hair, and any distinctive characteristics.  In particular, race and gender can and should be included in the description."
        )
        
        # Step 2: Clean up description
        clean_description = await self.client.get_completion(
            f"""Clean up this description of a person by removing any irrelevant details about pose, background, or setting. 
            Keep only physical characteristics of the person that would be relevant for generating a new image of them.
            In particular, race and gender description should be retained.
            
            Description: {initial_description}"""
        )
        
        return clean_description
