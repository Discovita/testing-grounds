# Discovitas OpenAI Client

A powerful, type-safe client for interacting with OpenAI's APIs, offering comprehensive access to OpenAI's capabilities including Chat Completions, Responses API, DALL-E image generation, and Vision capabilities.

## Features

- **Chat Completions API** - Generate text completions with GPT models
- **Responses API** - Use OpenAI's newer, more agentic API with built-in function calling and structured outputs
- **Image Generation** - Create images with DALL-E models
- **Vision API** - Analyze and describe images with GPT-4 Vision

## Installation

The OpenAI client is part of the Discovitas backend and is available in the `app.openai` package.

## Basic Usage

### Initializing the Client

```python
from app.openai.client import OpenAIClient

# Initialize with your API key
client = OpenAIClient(api_key="your-api-key")

# For testing (no API calls will be made)
test_client = OpenAIClient(api_key="fake-key", test_mode=True)
```

## Chat Completions API

The Chat Completions API provides a simple way to generate text completions from GPT models.

### Basic Text Completion

```python
async def get_simple_completion():
    client = OpenAIClient(api_key="your-api-key")
    
    # Get a simple text completion
    response = await client.get_completion("What is the capital of France?")
    
    print(response)  # "The capital of France is Paris."
```

### Structured Completion with Pydantic Models

Use Pydantic models to get structured, validated responses from the model:

```python
from pydantic import Field
from app.openai.models import LLMResponseModel

class WeatherInfo(LLMResponseModel):
    """Model for weather information structured output."""
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition (e.g., sunny, rainy)")
    location: str = Field(..., description="Location for the weather report")

async def get_structured_weather():
    client = OpenAIClient(api_key="your-api-key")
    
    messages = [
        {"role": "system", "content": "You are a weather assistant."},
        {"role": "user", "content": "What's the weather like in Paris today?"}
    ]
    
    # Get a structured completion
    weather = await client.get_structured_completion(messages, WeatherInfo)
    
    print(f"Temperature: {weather.temperature}°C")
    print(f"Condition: {weather.condition}")
    print(f"Location: {weather.location}")
```

## Responses API

The Responses API is OpenAI's newer, more agentic API that provides enhanced capabilities for function calling and structured outputs. It's designed to be used in modern agent applications.

### Basic Response

```python
async def create_simple_response():
    client = OpenAIClient(api_key="your-api-key")
    
    # Create a simple response
    response = await client.create_response_with_responses(
        input_data="What is the capital of France?",
        model="gpt-4o"
    )
    
    # Access the text output directly with the convenience property
    print(response.output_text)  # "The capital of France is Paris."
```

### Function Calling

The Responses API makes it easy to define functions that the model can call:

```python
from openai.types.responses import FunctionTool

async def use_function_calling():
    client = OpenAIClient(api_key="your-api-key")
    
    # Define a calculator function
    calculator_function = FunctionTool(
        type="function",
        name="calculator",
        description="Perform basic arithmetic operations",
        parameters={
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "The operation to perform (add, subtract, multiply, divide)",
                    "enum": ["add", "subtract", "multiply", "divide"]
                },
                "a": {
                    "type": "number",
                    "description": "The first number"
                },
                "b": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "a", "b"],
            "additionalProperties": False
        },
        strict=True
    )
    
    # Define function handler
    async def calculator(args):
        operation = args["operation"]
        a = args["a"]
        b = args["b"]
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            result = a / b
        
        return f"Result of {a} {operation} {b} = {result}"
    
    function_handlers = {
        "calculator": calculator
    }
    
    # Call functions with automatic handling
    final_response = await client.call_functions_with_responses(
        input_data="What is 25 plus 17?",
        functions=[calculator_function],
        function_handlers=function_handlers,
        model="gpt-4o"
    )
    
    print(final_response.output_text)  # "25 plus 17 equals 42."
```

### Multi-Function Calling

You can define multiple functions that the model can choose from:

```python
async def use_multiple_functions():
    client = OpenAIClient(api_key="your-api-key")
    
    # Define calculator and weather functions
    calculator_function = FunctionTool(...)  # As defined above
    
    weather_function = FunctionTool(
        type="function",
        name="get_weather",
        description="Get the current weather for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and country, e.g., 'Paris, France'"
                }
            },
            "required": ["location"],
            "additionalProperties": False
        },
        strict=True
    )
    
    # Define function handlers
    async def get_weather(args):
        location = args["location"]
        # In a real implementation, you would call a weather API
        return f"The weather in {location} is sunny with a temperature of 22°C"
    
    function_handlers = {
        "calculator": calculator,
        "get_weather": get_weather
    }
    
    # Let the model decide which function to call based on the query
    response = await client.call_functions_with_responses(
        input_data="What's the weather like in Paris today?",
        functions=[calculator_function, weather_function],
        function_handlers=function_handlers,
        model="gpt-4o"
    )
    
    print(response.output_text)  # "The weather in Paris today is sunny with a temperature of 22°C."
```

### Structured Outputs with Pydantic Models

The Responses API can also return structured outputs using Pydantic models:

```python
from pydantic import Field
from app.openai.models import LLMResponseModel

class WeatherResponse(LLMResponseModel):
    """Model for weather information structured output."""
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition (e.g., sunny, rainy)")
    location: str = Field(..., description="Location for the weather report")

async def get_structured_response():
    client = OpenAIClient(api_key="your-api-key")
    
    # Get a structured response
    result = await client.get_structured_response_with_responses(
        input_data="What's the weather like in Paris?",
        response_model=WeatherResponse,
        model="gpt-4o"
    )
    
    # Check if the response is valid
    if result.is_valid:
        # Access the parsed data as a Pydantic model
        weather = result.parsed
        print(f"Temperature: {weather.temperature}°C")
        print(f"Condition: {weather.condition}")
        print(f"Location: {weather.location}")
    else:
        # Handle error
        print(f"Error: {result.error}")
```

### Conversation Management

The Responses API provides built-in conversation state management:

```python
async def manage_conversation():
    client = OpenAIClient(api_key="your-api-key")
    
    # First message
    response1 = await client.create_response_with_responses(
        input_data="Hello, my name is Alice.",
        model="gpt-4o",
        store=True  # Store the response for future reference
    )
    
    # Continue the conversation using the previous response ID
    response2 = await client.create_response_with_responses(
        input_data="What's my name?",
        model="gpt-4o",
        previous_response_id=response1.id  # Link to previous conversation
    )
    
    print(response2.output_text)  # "Your name is Alice."
```

## Image Generation

### Generate an Image with DALL-E

```python
async def generate_image():
    client = OpenAIClient(api_key="your-api-key")
    
    # Generate an image
    response = await client.generate_image("A futuristic city with flying cars")
    
    print(f"Image URL: {response.url}")
```

### Safe Image Generation with Error Handling

For cases where content safety filters might be triggered:

```python
async def generate_safe_image():
    client = OpenAIClient(api_key="your-api-key")
    
    # Generate an image with safety handling
    response = await client.safe_generate_image("A beautiful sunset over mountains")
    
    if response.success:
        print(f"Image URL: {response.url}")
    else:
        print(f"Error: {response.error}")
```

### Using the Image Generation Service

For more complex image generation scenarios, use the `ImageGenerationService`:

```python
from app.openai.image_generation import ImageGenerationService

async def generate_scene():
    client = OpenAIClient(api_key="your-api-key")
    service = ImageGenerationService(client)
    
    # Generate a scene with specific parameters
    response = await service.generate_scene(
        setting="a beach at sunset",
        outfit="casual summer clothes",
        emotion="happy and relaxed",
        user_description="brown hair and glasses"
    )
    
    print(f"Image URL: {response.url}")
```

## Vision API

### Describe an Image

```python
from pydantic import AnyHttpUrl

async def describe_image():
    client = OpenAIClient(api_key="your-api-key")
    
    # URL of the image to describe
    image_url = AnyHttpUrl("https://example.com/image.jpg")
    
    # Get a description of the image
    description = await client.describe_image_with_vision(
        image_url=image_url,
        prompt="What can you see in this image?"
    )
    
    print(description)
```

## Error Handling

The client includes robust error handling for various scenarios:

```python
async def handle_errors():
    try:
        client = OpenAIClient(api_key="your-api-key")
        
        # This might fail if the model refuses to generate a response
        response = await client.create_response_with_responses(
            input_data="Generate harmful content",
            model="gpt-4o"
        )
        
    except Exception as e:
        print(f"Error: {str(e)}")
```

## Testing

The client includes a test mode that can be used for unit testing:

```python
async def test_client():
    # Initialize in test mode
    client = OpenAIClient(api_key="fake-key", test_mode=True)
    
    # This won't make an actual API call
    response = await client.get_completion("What is the capital of France?")
    
    assert response == "This is a test response"
```

## Which API Should I Use?

- **Chat Completions API**: 
  - Use for simple text generation tasks
  - When you need compatibility with existing code
  - For basic structured outputs

- **Responses API**: 
  - Recommended for new projects
  - When you need function calling capabilities
  - For complex structured outputs
  - When you need conversation management
  - For building agentic applications

The Responses API is OpenAI's newer API with enhanced capabilities, but both APIs are fully supported.

## API Reference

### OpenAIClient Methods

#### Chat Completions API
- `get_completion(prompt: str) -> str` - Get a simple text completion
- `get_structured_completion(messages: List[Dict[str, Any]], response_model: Type[T]) -> T` - Get a structured completion

#### Responses API
- `create_response_with_responses(input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]], model: str = "gpt-4o", ...) -> Response` - Create a response
- `call_function_with_responses(input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]], functions: List[Union[Dict[str, Any], FunctionTool]], ...) -> Response` - Call functions
- `call_functions_with_responses(input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]], functions: List[Union[Dict[str, Any], FunctionTool]], function_handlers: Dict[str, Callable], ...) -> Response` - Call functions and handle responses
- `submit_function_results_with_responses(input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]], function_outputs: Union[Dict[str, Any], List[Dict[str, Any]]], ...) -> Response` - Submit function results
- `get_structured_response_with_responses(input_data: Union[str, List[Dict[str, Any]], List[ResponsesMessage]], response_model: Type[T], ...) -> StructuredResponseResult[T]` - Get a structured response

#### Image Generation
- `generate_image(prompt: str) -> ImageResponse` - Generate an image
- `safe_generate_image(prompt: str) -> SafeImageResponse` - Generate an image with safety handling

#### Vision
- `describe_image_with_vision(image_url: AnyHttpUrl, prompt: str) -> str` - Describe an image 