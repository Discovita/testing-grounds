"""Service for generating images using OpenAI."""

from openai import APIError
from pydantic import AnyHttpUrl
from .client.client import OpenAIClient
from .models import ImageResponse, ChatMessage, SafeChatRequest, SafeImageResponse

class ImageGenerationService:
    """Service for generating images using OpenAI."""
    
    def __init__(self, client: OpenAIClient):
        self.client = client
    
    async def generate_scene(
        self,
        setting: str,
        outfit: str,
        emotion: str,
        user_description: str | None = None,
        user_feedback: str | None = None,
        previous_augmented_prompt: str | None = None
    ) -> ImageResponse:
        """Generate a scene based on user input."""
        # Build base prompt including user description if available
        person_desc = f"a person with {user_description}" if user_description else "a person"
        base_prompt = f"A photo of {person_desc} in {setting}, wearing {outfit}, expressing {emotion}. Make sure the scene prominently features a person with these physical characteristics.  Make it a realistic, colored, photo-quality image."
        
        if user_feedback and previous_augmented_prompt:
            # If we have feedback and a previous prompt, use those for refinement
            # Emphasize the user feedback by putting it first and making it a requirement
            prompt = f"""IMPORTANT REQUIREMENTS FROM USER: {user_feedback}

Based on these requirements, generate a new version of this scene:
{previous_augmented_prompt}

The above description should be modified to strongly emphasize and incorporate the user's requirements."""
        else:
            prompt = base_prompt

        return await self.client.generate_image(prompt)

    async def safe_generate_scene(
        self,
        setting: str,
        outfit: str,
        emotion: str,
        user_description: str | None = None,
        user_feedback: str | None = None,
        previous_augmented_prompt: str | None = None
    ) -> SafeImageResponse:
        """Generate a scene based on user input with safety handling."""
        # Build base prompt including user description if available
        person_desc = f"a person with {user_description}" if user_description else "a person"
        base_prompt = f"A photo of {person_desc} in {setting}, wearing {outfit}, expressing {emotion}. Make sure the scene prominently features a person with these physical characteristics.  Make it a realistic, colored, photo-quality image."
        
        if user_feedback and previous_augmented_prompt:
            # If we have feedback and a previous prompt, use those for refinement
            # Emphasize the user feedback by putting it first and making it a requirement
            prompt = f"""IMPORTANT REQUIREMENTS FROM USER: {user_feedback}

Based on these requirements, generate a new version of this scene:
{previous_augmented_prompt}

The above description should be modified to strongly emphasize and incorporate the user's requirements."""
        else:
            prompt = base_prompt

        return await self.client.safe_generate_image(prompt)
