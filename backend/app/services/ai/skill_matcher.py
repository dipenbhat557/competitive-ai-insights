import json
from typing import Any

from app.services.ai.gemini_client import GeminiClient
from app.services.ai.prompts import SKILL_MATCH_PROMPT


class SkillMatcher:
    """Matches candidate profiles against job requirements using AI."""

    def __init__(self):
        self.client = GeminiClient()

    async def match(
        self,
        candidate_profile: dict[str, Any],
        job_title: str,
        job_description: str,
        required_skills: list[str],
        min_score: float | None = None,
    ) -> dict[str, Any]:
        """
        Evaluate candidate-job match.

        Returns:
            dict with match_score, reasoning, skill_gaps, highlights
        """
        prompt = SKILL_MATCH_PROMPT.format(
            candidate_profile=json.dumps(candidate_profile, indent=2, default=str),
            job_title=job_title,
            job_description=job_description,
            required_skills=", ".join(required_skills),
            min_score=min_score if min_score is not None else "None specified",
        )

        response_text = await self.client.generate_content(prompt)

        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                lines = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
                cleaned = "\n".join(lines)
            result = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError):
            result = {
                "match_score": 0.0,
                "reasoning": response_text,
                "skill_gaps": [],
                "highlights": [],
            }

        return {
            "match_score": float(result.get("match_score", 0)),
            "reasoning": result.get("reasoning", ""),
            "skill_gaps": result.get("skill_gaps", []),
            "highlights": result.get("highlights", []),
        }
