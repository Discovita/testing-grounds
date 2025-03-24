"""Function models for OpenAI Responses API.

This module contains models related to function definitions and function calls
for the OpenAI Responses API.
"""

from typing import Dict, Any, Optional, Union, List, Literal
from pydantic import BaseModel, Field, model_serializer
import json
from openai.types.responses import FunctionTool, ResponseFunctionToolCall

class FunctionParameter(BaseModel):
    """Function parameter model for the Responses API.
    
    This model represents a parameter for a function in the Responses API.
    """
    type: Union[str, List[str]] = Field(..., description="The type of the parameter")
    description: Optional[str] = Field(None, description="Description of the parameter")
    enum: Optional[List[Any]] = Field(None, description="Possible values for the parameter")
    
    @model_serializer
    def serialize_model(self) -> Dict[str, Any]:
        """Serialize the model to a dictionary, excluding None values.
        
        This ensures that enum=None is not included in the serialized output,
        which would cause API errors.
        """
        data = {}
        for key, value in self.__dict__.items():
            if value is not None:
                data[key] = value
        return data
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"  # Allow extra fields for function parameters

class FunctionParameters(BaseModel):
    """Function parameters model for the Responses API.
    
    This model represents the parameters for a function in the Responses API.
    """
    type: Literal["object"] = Field("object", description="The type of the parameters object")
    properties: Dict[str, FunctionParameter] = Field(..., description="The properties of the parameters object")
    required: List[str] = Field(..., description="The required properties")
    additionalProperties: bool = Field(False, description="Whether additional properties are allowed")


# Helper function to parse arguments from ResponseFunctionToolCall
def parse_function_call_arguments(function_call: ResponseFunctionToolCall) -> Dict[str, Any]:
    """Parse the JSON-encoded arguments from a ResponseFunctionToolCall into a Python dictionary.
    
    Args:
        function_call: The ResponseFunctionToolCall to parse arguments from
        
    Returns:
        Dict[str, Any]: The parsed arguments
    """
    return json.loads(function_call.arguments) 