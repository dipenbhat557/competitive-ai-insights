import httpx

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile

HR_API_BASE = "https://www.hackerrank.com/rest"


class HackerRankScraper(AbstractPlatformScraper):
    async def scrape(self, username: str) -> ScrapedProfile:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            # Fetch scores
            scores_resp = await client.get(
                f"{HR_API_BASE}/hackers/{username}/scores",
                headers={"Accept": "application/json"},
            )

            # Fetch contest info
            contests_resp = await client.get(
                f"{HR_API_BASE}/hackers/{username}/contest_participation",
                headers={"Accept": "application/json"},
            )

            # Fetch badges / submission stats
            profile_resp = await client.get(
                f"{HR_API_BASE}/hackers/{username}",
                headers={"Accept": "application/json"},
            )

        # Parse scores for topic stats and total problems
        topic_stats = {}
        problems_solved = 0
        if scores_resp.status_code == 200:
            scores_data = scores_resp.json()
            for item in scores_data.get("models", []):
                name = item.get("name", "")
                solved = item.get("solved", 0)
                if name:
                    topic_stats[name] = solved
                problems_solved += solved

        # Parse contest rating
        contest_rating = None
        if contests_resp.status_code == 200:
            contest_data = contests_resp.json()
            models = contest_data.get("models", [])
            if models:
                # Use the latest contest rating
                latest = models[-1] if models else {}
                contest_rating_val = latest.get("rating")
                if contest_rating_val is not None:
                    contest_rating = float(contest_rating_val)

        raw_data = {}
        if profile_resp.status_code == 200:
            raw_data = profile_resp.json()

        return ScrapedProfile(
            platform="hackerrank",
            username=username,
            problems_solved=problems_solved,
            contest_rating=contest_rating,
            topic_stats=topic_stats,
            submission_calendar={},
            raw_data=raw_data,
        )

    async def validate_username(self, username: str) -> bool:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(
                f"{HR_API_BASE}/hackers/{username}",
                headers={"Accept": "application/json"},
            )
            return resp.status_code == 200
