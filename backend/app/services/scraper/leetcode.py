import httpx

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"


class LeetCodeScraper(AbstractPlatformScraper):
    async def scrape(self, username: str) -> ScrapedProfile:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch user profile and problem stats
            profile_query = """
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                    submitStatsGlobal {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                    tagProblemCounts {
                        advanced {
                            tagName
                            problemsSolved
                        }
                        intermediate {
                            tagName
                            problemsSolved
                        }
                        fundamental {
                            tagName
                            problemsSolved
                        }
                    }
                }
            }
            """
            profile_resp = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": profile_query, "variables": {"username": username}},
            )
            profile_data = profile_resp.json()

            # Fetch contest ranking
            contest_query = """
            query userContestRankingInfo($username: String!) {
                userContestRanking(username: $username) {
                    rating
                    globalRanking
                    attendedContestsCount
                }
            }
            """
            contest_resp = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": contest_query, "variables": {"username": username}},
            )
            contest_data = contest_resp.json()

            # Fetch submission calendar
            calendar_query = """
            query userProfileCalendar($username: String!) {
                matchedUser(username: $username) {
                    userCalendar {
                        submissionCalendar
                    }
                }
            }
            """
            calendar_resp = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": calendar_query, "variables": {"username": username}},
            )
            calendar_data = calendar_resp.json()

        # Parse problems solved
        problems_solved = 0
        matched_user = profile_data.get("data", {}).get("matchedUser")
        if matched_user:
            ac_stats = matched_user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
            for stat in ac_stats:
                if stat.get("difficulty") == "All":
                    problems_solved = stat.get("count", 0)
                    break

        # Parse topic stats
        topic_stats = {}
        if matched_user:
            tag_counts = matched_user.get("tagProblemCounts", {})
            for level in ("fundamental", "intermediate", "advanced"):
                for tag in tag_counts.get(level, []):
                    name = tag.get("tagName", "")
                    count = tag.get("problemsSolved", 0)
                    if name:
                        topic_stats[name] = topic_stats.get(name, 0) + count

        # Parse contest rating
        contest_rating = None
        ranking_data = contest_data.get("data", {}).get("userContestRanking")
        if ranking_data:
            contest_rating = ranking_data.get("rating")

        # Parse submission calendar
        submission_calendar = {}
        cal_user = calendar_data.get("data", {}).get("matchedUser")
        if cal_user:
            cal = cal_user.get("userCalendar", {}).get("submissionCalendar", "{}")
            if isinstance(cal, str):
                import json
                try:
                    submission_calendar = json.loads(cal)
                except (json.JSONDecodeError, TypeError):
                    submission_calendar = {}
            elif isinstance(cal, dict):
                submission_calendar = cal

        return ScrapedProfile(
            platform="leetcode",
            username=username,
            problems_solved=problems_solved,
            contest_rating=contest_rating,
            topic_stats=topic_stats,
            submission_calendar=submission_calendar,
            raw_data={
                "profile": profile_data.get("data", {}),
                "contest": contest_data.get("data", {}),
                "calendar": calendar_data.get("data", {}),
            },
        )

    async def validate_username(self, username: str) -> bool:
        async with httpx.AsyncClient(timeout=15.0) as client:
            query = """
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                }
            }
            """
            resp = await client.post(
                LEETCODE_GRAPHQL_URL,
                json={"query": query, "variables": {"username": username}},
            )
            data = resp.json()
            return data.get("data", {}).get("matchedUser") is not None
