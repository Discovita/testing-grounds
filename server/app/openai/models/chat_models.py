"""Chat-related models for OpenAI API."""

from typing import List, Union, Dict, Any, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: Union[str, List[Dict[str, Any]]]

class ChatRequest(BaseModel):
    """Base model for chat completion requests."""
    model: str
    messages: List[ChatMessage]
    max_tokens: int = 300

class ContentFilter(BaseModel):
    """Content filter response from OpenAI."""
    is_violating: bool
    category: str | None = None
    explanation_if_violating: str | None = None

class ChatResponse(BaseModel):
    """Base model for chat completion responses."""
    content: str
    content_filter: ContentFilter | None = None

    @classmethod
    def from_openai_response(cls, response: Any) -> "ChatResponse":
        """Create ChatResponse from OpenAI API response."""
        content_filter = None
        if hasattr(response, "content_filter") and response.content_filter is not None:
            content_filter = ContentFilter(
                is_violating=response.content_filter.is_violating,
                category=response.content_filter.category,
                explanation_if_violating=response.content_filter.explanation_if_violating
            )
        return cls(
            content=response.choices[0].message.content,
            content_filter=content_filter
        )

class VisionRequest(ChatRequest):
    """Request model for GPT-4 Vision."""
    model: str = "gpt-4o-mini"

class CompletionRequest(ChatRequest):
    """Request model for GPT-4 text completion."""
    model: str = "gpt-4o"
    response_format: Optional[Dict[str, str]] = None
    max_tokens: int = 1000  # Increase default token limit

class SafeChatRequest(ChatRequest):
    """Request model for safety-enhanced chat completion."""
    model: str = "gpt-4"
    temperature: float = Field(0.7, description="Controls randomness in the response")
