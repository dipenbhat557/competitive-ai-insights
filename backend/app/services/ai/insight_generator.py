import json
from typing import Any

from app.services.ai.gemini_client import GeminiClient
from app.services.ai.prompts import INSIGHT_GENERATION_PROMPT


class InsightGenerator:
    """Generates AI-powered insight reports from profile data."""

    def __init__(self):
        self.client = GeminiClient()

    async def generate(self, profile_snapshots: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Generate insights from aggregated profile data.

        Args:
            profile_snapshots: list of dicts with platform data.

        Returns:
            dict with keys: strengths, weaknesses, career_recs, roadmap, overall_score, summary_text
        """
        profile_data_str = json.dumps(profile_snapshots, indent=2, default=str)
        prompt = INSIGHT_GENERATION_PROMPT.format(profile_data=profile_data_str)

        response_text = await self.client.generate_content(prompt)

        # Parse JSON response
        try:
            # Try to extract JSON from potential markdown code blocks
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                # Remove first and last lines (``` markers)
                lines = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
                cleaned = "\n".join(lines)

            result = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            # If parsing fails, return a default structure
            result = {
                "strengths": ["Unable to parse AI response"],
                "weaknesses": ["Unable to parse AI response"],
                "career_recs": ["Unable to parse AI response"],
                "roadmap": [],
                "overall_score": 0.0,
                "summary_text": response_text,
            }

        return {
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "career_recs": result.get("career_recs", []),
            "roadmap": result.get("roadmap", []),
            "overall_score": float(result.get("overall_score", 0)),
            "summary_text": result.get("summary_text", ""),
        }
