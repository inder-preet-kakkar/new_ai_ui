from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import List, Dict

import requests

try:
    import openai
except ImportError:  # pragma: no cover - optional
    openai = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional
    genai = None


Message = Dict[str, str]


class LLMProvider(ABC):
    """Base class for language model providers."""

    @abstractmethod
    def generate(self, messages: List[Message]) -> str:
        """Generate a response from the provider given the chat history."""


class OpenAIProvider(LLMProvider):
    """Use OpenAI's ChatGPT API."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str | None = None):
        """Create a provider for OpenAI's chat models."""
        if openai is None:
            raise RuntimeError("openai package is required for OpenAIProvider")
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        openai.api_key = self.api_key

    def generate(self, messages: List[Message]) -> str:
        """Return the assistant reply for ``messages`` using ChatGPT."""
        response = openai.chat.completions.create(model=self.model, messages=messages)
        return response.choices[0].message.content


class GeminiProvider(LLMProvider):
    """Use Google's Gemini API."""

    def __init__(self, model: str = "gemini-pro", api_key: str | None = None):
        """Use Google's Gemini API to generate text."""
        if genai is None:
            raise RuntimeError("google-generativeai package is required for GeminiProvider")
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model)

    def generate(self, messages: List[Message]) -> str:
        """Generate a reply for ``messages`` using Gemini."""
        # Convert messages to a single text conversation string
        parts = []
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            if role == "user":
                parts.append(f"User: {content}")
            else:
                parts.append(f"Assistant: {content}")
        prompt = "\n".join(parts)
        response = self._model.generate_content(prompt)
        return response.text


class OllamaProvider(LLMProvider):
    """Use a local Ollama instance."""

    def __init__(self, model: str = "llama2", host: str = "http://localhost:11434"):  # pragma: no cover - network
        """Use a local Ollama instance running on ``host``."""
        self.model = model
        self.host = host.rstrip("/")

    def generate(self, messages: List[Message]) -> str:
        """Generate a reply from the local Ollama model."""
        prompt = "\n".join(m["content"] for m in messages)
        url = f"{self.host}/api/generate"
        resp = requests.post(url, json={"model": self.model, "prompt": prompt})
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")
