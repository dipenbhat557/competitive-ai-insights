import asyncio
from functools import partial

import google.generativeai as genai

from app.config import settings


class GeminiClient:
    """Wrapper around Google Generative AI SDK."""

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)

    async def generate_content(self, prompt: str) -> str:
        """Generate content asynchronously using Gemini."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(self.model.generate_content, prompt),
        )
        return response.text

    async def generate_chat(self, messages: list[dict[str, str]]) -> str:
        """
        Generate a chat response.

        Args:
            messages: list of dicts with 'role' and 'content' keys.
                      Roles should be 'user' or 'model'.
        """
        loop = asyncio.get_event_loop()

        chat = self.model.start_chat(history=[])

        # Send all messages except the last one as history
        for msg in messages[:-1]:
            role = "model" if msg["role"] == "assistant" else "user"
            chat.history.append({"role": role, "parts": [msg["content"]]})

        # Send the last message to get a response
        last_message = messages[-1]["content"] if messages else ""
        response = await loop.run_in_executor(
            None,
            partial(chat.send_message, last_message),
        )
        return response.text
