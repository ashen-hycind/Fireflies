"""
LLM Utility module for Fireflies Swarm.

Provides a unified interface for calling LLMs with structured Pydantic outputs.
Supports OpenAI, Gemini, Anthropic, and local models via litellm/openai.
"""

import os
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv
import litellm

load_dotenv()

T = TypeVar("T", bound=BaseModel)

# Default models (can be overridden via environment variables or function arguments)
DEFAULT_FAST_MODEL = os.getenv("DEFAULT_FAST_MODEL", "gpt-4o-mini")
DEFAULT_REASONING_MODEL = os.getenv("DEFAULT_REASONING_MODEL", "gpt-4o")


def generate_structured(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_retries: int = 2,
) -> T:
    """
    Calls the LLM and guarantees a structured Pydantic response matching `response_model`.
    
    Args:
        prompt: The main user/task prompt.
        response_model: The Pydantic model class to validate and return.
        system_prompt: Optional system instructions defining the agent role.
        model: Model identifier (e.g. 'gpt-4o-mini', 'gemini/gemini-1.5-flash', 'claude-3-5-sonnet-20240620').
        temperature: Sampling temperature (default: 0.2 for deterministic reasoning).
        max_retries: Number of retry attempts on schema validation failure.
        
    Returns:
        An instance of `response_model` populated with the LLM's structured output.
    """
    selected_model = model or DEFAULT_FAST_MODEL
    
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            # Use litellm with response_format for structured outputs
            response = litellm.completion(
                model=selected_model,
                messages=messages,
                response_format=response_model,
                temperature=temperature,
            )
            content = response.choices[0].message.content
            # Parse & validate against Pydantic model
            return response_model.model_validate_json(content)
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                # Append correction prompt for retry
                messages.append({
                    "role": "user",
                    "content": f"Your previous response failed validation with error: {str(e)}. Please output valid JSON strictly matching the schema."
                })
    
    raise RuntimeError(f"Failed to generate valid structured response for {response_model.__name__} after {max_retries} retries. Error: {last_error}")
