from dataclasses import dataclass
from typing import List


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ChatCompletionRequest:
    messages: List[Message]
    max_tokens: int
    temperature: float
    model: str = "gpt-4"


@dataclass
class ChatCompletionResponse:
    content: str
