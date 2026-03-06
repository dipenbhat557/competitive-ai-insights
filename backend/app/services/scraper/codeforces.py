from collections import defaultdict

import httpx

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile

CF_API_BASE = "https://codeforces.com/api"


class CodeforcesScraper(AbstractPlatformScraper):
    async def scrape(self, username: str) -> ScrapedProfile:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch user info
            info_resp = await client.get(f"{CF_API_BASE}/user.info", params={"handles": username})
            info_data = info_resp.json()

            # Fetch rating history
            rating_resp = await client.get(f"{CF_API_BASE}/user.rating", params={"handle": username})
            rating_data = rating_resp.json()

            # Fetch submissions
            status_resp = await client.get(
                f"{CF_API_BASE}/user.status",
                params={"handle": username, "from": 1, "count": 10000},
            )
            status_data = status_resp.json()

        # Parse contest rating
        contest_rating = None
        if info_data.get("status") == "OK":
            users = info_data.get("result", [])
            if users:
                contest_rating = users[0].get("rating")

        # Count solved problems and topic stats from submissions
        solved_problems = set()
        topic_counts: dict[str, int] = defaultdict(int)
        submission_calendar: dict[str, int] = defaultdict(int)

        if status_data.get("status") == "OK":
            for sub in status_data.get("result", []):
                if sub.get("verdict") == "OK":
                    problem = sub.get("problem", {})
                    problem_id = f"{problem.get('contestId', '')}{problem.get('index', '')}"
                    if problem_id and problem_id not in solved_problems:
                        solved_problems.add(problem_id)
                        for tag in problem.get("tags", []):
                            topic_counts[tag] += 1

                # Build submission calendar (group by date)
                creation_time = sub.get("creationTimeSeconds")
                if creation_time:
                    date_str = str(creation_time)
                    submission_calendar[date_str] = submission_calendar.get(date_str, 0) + 1

        return ScrapedProfile(
            platform="codeforces",
            username=username,
            problems_solved=len(solved_problems),
            contest_rating=float(contest_rating) if contest_rating else None,
            topic_stats=dict(topic_counts),
            submission_calendar=dict(submission_calendar),
            raw_data={
                "info": info_data.get("result", []),
                "rating_history_count": len(rating_data.get("result", [])),
            },
        )

    async def validate_username(self, username: str) -> bool:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{CF_API_BASE}/user.info", params={"handles": username})
            data = resp.json()
            return data.get("status") == "OK"
