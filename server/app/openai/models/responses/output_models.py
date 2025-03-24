"""Output models for OpenAI Responses API.

This module contains models related to the output of the OpenAI Responses API,
including text output and response models.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from openai.types.responses import ResponseFunctionToolCall, Response as OpenAIResponse

class OutputText(BaseModel):
    """Output text model for the Responses API.
    
    This model represents text output in the Responses API.
    """
    type: Literal["output_text"] = Field("output_text", description="Type of the output item")
    text: str = Field(..., description="The text content")
    annotations: List[Dict[str, Any]] = Field(default_factory=list, description="Annotations for the text")

class ResponsesOutput(BaseModel):
    """Output model for the Responses API.
    
    This model represents the output of the Responses API, which can be
    either text or a function call.
    """
    type: str = Field(..., description="Type of the output item")
    
    # Additional fields based on type
    # For function_call
    id: Optional[str] = Field(None, description="Unique identifier for the function call")
    call_id: Optional[str] = Field(None, description="ID used to associate the function call with its output")
    name: Optional[str] = Field(None, description="Name of the function to call")
    arguments: Optional[str] = Field(None, description="JSON-encoded arguments for the function call")
    
    # For output_text
    text: Optional[str] = Field(None, description="The text content")
    annotations: Optional[List[Dict[str, Any]]] = Field(None, description="Annotations for the text")
    
    @field_validator('type')
    def validate_type(cls, v):
        """Validate the type field."""
        if v not in ["function_call", "output_text"]:
            raise ValueError(f"Invalid type: {v}. Must be one of: function_call, output_text")
        return v
    
    def is_function_call(self) -> bool:
        """Check if this output is a function call.
        
        Returns:
            bool: True if this output is a function call, False otherwise
        """
        return self.type == "function_call"
    
    def is_text(self) -> bool:
        """Check if this output is text.
        
        Returns:
            bool: True if this output is text, False otherwise
        """
        return self.type == "output_text"
    
    def as_function_call(self) -> ResponseFunctionToolCall:
        """Convert this output to a ResponseFunctionToolCall if it is a function call.
        
        Returns:
            ResponseFunctionToolCall: The function call
            
        Raises:
            ValueError: If this output is not a function call
        """
        if not self.is_function_call():
            raise ValueError("This output is not a function call")
        
        return ResponseFunctionToolCall(
            id=self.id,
            call_id=self.call_id,
            type="function_call",
            name=self.name,
            arguments=self.arguments,
            status="completed"  # Adding the status field which is required in ResponseFunctionToolCall
        )
    
    def as_text(self) -> OutputText:
        """Convert this output to an OutputText if it is text.
        
        Returns:
            OutputText: The output text
            
        Raises:
            ValueError: If this output is not text
        """
        if not self.is_text():
            raise ValueError("This output is not text")
        
        return OutputText(
            type="output_text",
            text=self.text,
            annotations=self.annotations or []
        )

# Using the OpenAI SDK's Response model directly
ResponsesResponse = OpenAIResponse

# Add a compatibility layer for code that still expects the old interface
# This can be removed once all code is updated to use the SDK's Response model
class ResponsesResponseCompat(OpenAIResponse):
    """Compatibility layer for code that still expects the old ResponsesResponse interface.
    
    This class extends the SDK's Response model with methods that were previously 
    available in our custom ResponsesResponse model.
    """
    
    @property
    def function_calls(self) -> List[ResponseFunctionToolCall]:
        """Get the function calls from the response.
        
        Returns:
            List[ResponseFunctionToolCall]: The function calls, or an empty list if there are no function calls
        """
        result = []
        for item in self.output:
            # In the SDK's model, function calls are in a different format
            # We need to extract them accordingly
            if hasattr(item, 'type') and item.type == 'function_call':
                result.append(ResponseFunctionToolCall(
                    id=item.id,
                    call_id=item.call_id,
                    type="function_call",
                    name=item.name,
                    arguments=item.arguments,
                    status="completed"
                ))
        return result
    
    def has_function_calls(self) -> bool:
        """Check if the response has any function calls.
        
        Returns:
            bool: True if the response has function calls, False otherwise
        """
        return any(hasattr(item, 'type') and item.type == 'function_call' for item in self.output) 