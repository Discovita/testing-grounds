"""Schema models for OpenAI Responses API.

This module contains models related to JSON schemas for structured outputs
in the OpenAI Responses API.
"""

from typing import Dict, Any, Optional, TypeVar, Type
from pydantic import BaseModel, Field

from app.openai.models.llm_response import LLMResponseModel

T = TypeVar('T', bound=LLMResponseModel)

class StructuredOutputSchema(BaseModel):
    """Structured output schema model for the Responses API.
    
    This model represents a JSON schema for structured outputs in the
    Responses API.
    """
    name: str = Field(..., description="The name of the schema")
    schema: Dict[str, Any] = Field(..., description="The JSON schema")
    strict: bool = Field(True, description="Whether to enforce strict mode for the schema")
    
    @classmethod
    def from_llm_response_model(cls, model_class: Type[T], name: Optional[str] = None) -> "StructuredOutputSchema":
        """Create a structured output schema from an LLMResponseModel class.
        
        Args:
            model_class: The LLMResponseModel class to create the schema from
            name: The name of the schema (defaults to the class name)
            
        Returns:
            StructuredOutputSchema: The structured output schema
        """
        schema_name = name or model_class.__name__
        schema = model_class.get_openai_schema()
        
        return cls(
            name=schema_name,
            schema=schema,
            strict=True
        ) 