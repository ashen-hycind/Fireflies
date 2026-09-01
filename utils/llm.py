"""
LLM Utility module for Fireflies Swarm.

Provides a unified interface for calling LLMs (Google Gemini, OpenAI) with structured Pydantic outputs.
"""

import os
from typing import Type, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

# Default models
DEFAULT_FAST_MODEL = os.getenv("DEFAULT_FAST_MODEL", "gemini-1.5-flash")
DEFAULT_REASONING_MODEL = os.getenv("DEFAULT_REASONING_MODEL", "gemini-1.5-flash")


def _call_gemini_structured(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: str = "gemini-1.5-flash",
    temperature: float = 0.2,
) -> T:
    """Invokes Google Gemini API with Pydantic structured output using google-genai SDK."""
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set in .env")

    client = genai.Client(api_key=api_key)
    
    # Strip any prefix like 'gemini/' if passed
    model_name = model.replace("gemini/", "")
    
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=response_model,
        temperature=temperature,
        system_instruction=system_prompt if system_prompt else None,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=config,
    )
    
    return response_model.model_validate_json(response.text)


def _call_openai_structured(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> T:
    """Invokes OpenAI API with structured outputs (response_format)."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set in .env")

    client = OpenAI(api_key=api_key)
    messages: List[Dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=response_model,
        temperature=temperature,
    )
    return completion.choices[0].message.parsed


def generate_structured(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_retries: int = 2,
) -> T:
    """
    Calls the configured LLM (Gemini or OpenAI) with Pydantic structured output validation.
    """
    selected_model = model or DEFAULT_FAST_MODEL
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            if "gemini" in selected_model.lower():
                return _call_gemini_structured(
                    prompt=prompt,
                    response_model=response_model,
                    system_prompt=system_prompt,
                    model=selected_model,
                    temperature=temperature,
                )
            else:
                return _call_openai_structured(
                    prompt=prompt,
                    response_model=response_model,
                    system_prompt=system_prompt,
                    model=selected_model,
                    temperature=temperature,
                )
        except Exception as e:
            last_error = e

    raise RuntimeError(
        f"Failed to generate valid structured response for {response_model.__name__} after {max_retries} retries. Error: {last_error}"
    )
