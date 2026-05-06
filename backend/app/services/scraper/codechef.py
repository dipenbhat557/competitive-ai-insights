import httpx
from bs4 import BeautifulSoup

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile

CODECHEF_API_BASE = "https://www.codechef.com/api"


def _approx_difficulty_from_rating(
    total: int, rating: float | None
) -> dict[str, int]:
    """Approximate difficulty distribution from star rating.

    CodeChef doesn't expose per-problem difficulty publicly, so we spread the
    solved count using rating-band heuristics. This is intentionally
    conservative — better than dropping difficulty altogether.
    """
    if total <= 0:
        return {"easy": 0, "medium": 0, "hard": 0, "expert": 0}
    r = rating or 1400
    if r < 1400:
        ratios = (0.7, 0.25, 0.05, 0.0)   # 1*
    elif r < 1600:
        ratios = (0.5, 0.40, 0.10, 0.0)   # 2*
    elif r < 1800:
        ratios = (0.35, 0.45, 0.18, 0.02) # 3*
    elif r < 2000:
        ratios = (0.25, 0.45, 0.25, 0.05) # 4*
    elif r < 2200:
        ratios = (0.15, 0.40, 0.35, 0.10) # 5*
    elif r < 2500:
        ratios = (0.10, 0.30, 0.40, 0.20) # 6*
    else:
        ratios = (0.05, 0.20, 0.40, 0.35) # 7*
    e, m, h, x = ratios
    easy = int(round(total * e))
    medium = int(round(total * m))
    hard = int(round(total * h))
    expert = max(total - easy - medium - hard, 0)
    return {"easy": easy, "medium": medium, "hard": hard, "expert": expert}


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

            # CC doesn't expose per-problem difficulty in the public API.
            # Approximate by spreading the user's solved count according to
            # their star rating: stronger users tend to solve harder problems.
            difficulty_breakdown = _approx_difficulty_from_rating(
                problems_solved, contest_rating
            )

            return ScrapedProfile(
                platform="codechef",
                username=username,
                problems_solved=problems_solved,
                contest_rating=contest_rating,
                topic_stats=topic_stats,
                submission_calendar={},
                raw_data={**data, "difficulty": difficulty_breakdown},
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
