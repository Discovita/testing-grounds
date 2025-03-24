"""Base model for LLM responses with schema generation."""

from typing import Dict, Any
import json
from pydantic import BaseModel

class LLMResponseModel(BaseModel):
    """Base model for LLM responses that can generate their own schema documentation."""
    
    @classmethod
    def get_openai_schema(cls) -> Dict[str, Any]:
        """Generate OpenAI-compatible JSON schema."""
        schema = cls.model_json_schema()
        # Ensure all fields are required for OpenAI's Structured Outputs
        schema["required"] = list(schema["properties"].keys())
        return schema

    @classmethod
    def get_prompt_instruction(cls) -> str:
        """Generate prompt instruction with JSON schema."""
        schema_str = json.dumps(cls.get_openai_schema(), indent=2)
        return f"Please provide your response in the following JSON format:\n{schema_str}"
