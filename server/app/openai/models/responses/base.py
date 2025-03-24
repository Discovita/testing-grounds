"""Base models for OpenAI Responses API.

This module contains the basic message and request/response models for
interacting with OpenAI's Responses API.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field

class ResponsesMessage(BaseModel):
    """Message model for the Responses API.
    
    This model represents a message in the Responses API format, which can be
    used as input to the API or received as part of the response.
    """
    role: Literal["user", "assistant"] = Field(..., description="The role of the message sender")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="The content of the message")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for future compatibility

class ResponsesRequest(BaseModel):
    """Request model for the Responses API.
    
    This model represents a request to the Responses API, which can include
    various parameters such as the model to use, the input messages, and
    function definitions.
    """
    model: str = Field("gpt-4o", description="The model to use for the response")
    input: Union[str, List[ResponsesMessage]] = Field(..., description="The input to the model")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tools (including functions) available to the model")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Control which tool the model uses")
    store: bool = Field(True, description="Whether to store the response for future reference")
    previous_response_id: Optional[str] = Field(None, description="ID of the previous response in a conversation")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for future compatibility 