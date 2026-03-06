from app.services.ai.gemini_client import GeminiClient
from app.services.ai.prompts import CHAT_SYSTEM_PROMPT


class ChatEngine:
    """Handles AI chat interactions with user profile context."""

    def __init__(self):
        self.client = GeminiClient()

    async def get_response(
        self,
        chat_history: list[dict[str, str]],
        profile_context: str = "",
    ) -> str:
        """
        Get an AI response given chat history and user profile context.

        Args:
            chat_history: list of {"role": "user"|"assistant", "content": "..."}
            profile_context: summary of the user's coding profile

        Returns:
            AI-generated response string
        """
        system_prompt = CHAT_SYSTEM_PROMPT.format(
            profile_context=profile_context if profile_context else "No profile data available yet."
        )

        # Build messages with system context as the first user message
        messages = [
            {"role": "user", "content": system_prompt},
            {"role": "assistant", "content": "Understood. I'm ready to help you with competitive programming, interview preparation, and career advice. How can I assist you today?"},
        ]

        # Add chat history
        for msg in chat_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

        response = await self.client.generate_chat(messages)
        return response
