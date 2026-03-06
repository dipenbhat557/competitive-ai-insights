import httpx
from bs4 import BeautifulSoup

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile

CODECHEF_API_BASE = "https://www.codechef.com/api"


class CodeChefScraper(AbstractPlatformScraper):
    async def scrape(self, username: str) -> ScrapedProfile:
        profile_data = await self._try_api(username)
        if profile_data:
            return profile_data
        return await self._try_html(username)

    async def _try_api(self, username: str) -> ScrapedProfile | None:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(
                    f"{CODECHEF_API_BASE}/users/{username}",
                    headers={"Accept": "application/json"},
                )
                if resp.status_code != 200:
                    return None

                data = resp.json()

            problems_solved = data.get("fully_solved", {}).get("count", 0)
            contest_rating = data.get("rating")
            if contest_rating is not None:
                contest_rating = float(contest_rating)

            # Extract topic stats from problem tags
            topic_stats = {}
            for problem in data.get("fully_solved", {}).get("problems", []):
                for tag in problem.get("tags", []):
                    topic_stats[tag] = topic_stats.get(tag, 0) + 1

            return ScrapedProfile(
                platform="codechef",
                username=username,
                problems_solved=problems_solved,
                contest_rating=contest_rating,
                topic_stats=topic_stats,
                submission_calendar={},
                raw_data=data,
            )
        except Exception:
            return None

    async def _try_html(self, username: str) -> ScrapedProfile:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resp = await client.get(f"https://www.codechef.com/users/{username}")
            resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        problems_solved = 0
        contest_rating = None

        # Try to find problems solved
        problems_section = soup.find("h3", string=lambda t: t and "Problems Solved" in t if t else False)
        if problems_section:
            count_text = problems_section.get_text()
            import re
            match = re.search(r"(\d+)", count_text)
            if match:
                problems_solved = int(match.group(1))

        # Try to find rating
        rating_section = soup.find("div", class_="rating-number")
        if rating_section:
            try:
                contest_rating = float(rating_section.get_text().strip())
            except (ValueError, TypeError):
                pass

        return ScrapedProfile(
            platform="codechef",
            username=username,
            problems_solved=problems_solved,
            contest_rating=contest_rating,
            topic_stats={},
            submission_calendar={},
            raw_data={"source": "html_scrape"},
        )

    async def validate_username(self, username: str) -> bool:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(f"https://www.codechef.com/users/{username}")
            return resp.status_code == 200
