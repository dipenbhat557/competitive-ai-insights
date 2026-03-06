import asyncio
from collections import defaultdict

from app.services.scraper.base import AbstractPlatformScraper, ScrapedProfile


class ProfileAggregator:
    """Aggregates scraping results from multiple platform scrapers."""

    def __init__(self, scrapers: dict[str, AbstractPlatformScraper]):
        self.scrapers = scrapers

    async def scrape_all(self, profiles: dict[str, str]) -> list[ScrapedProfile]:
        """
        Scrape all provided profiles concurrently.

        Args:
            profiles: dict mapping platform name to username, e.g.
                      {"leetcode": "user1", "codeforces": "user2"}

        Returns:
            List of ScrapedProfile results.
        """
        tasks = []
        for platform, username in profiles.items():
            scraper = self.scrapers.get(platform)
            if scraper:
                tasks.append(self._safe_scrape(scraper, username, platform))

        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _safe_scrape(
        self,
        scraper: AbstractPlatformScraper,
        username: str,
        platform: str,
    ) -> ScrapedProfile | None:
        try:
            return await scraper.scrape(username)
        except Exception:
            return None

    @staticmethod
    def merge_topic_stats(profiles: list[ScrapedProfile]) -> dict[str, float]:
        """
        Merge topic stats from all profiles with weighted normalization.
        Each platform's stats are normalized by the total problems on that platform,
        then combined.
        """
        merged: dict[str, float] = defaultdict(float)
        platform_count = 0

        for profile in profiles:
            total = sum(profile.topic_stats.values()) if profile.topic_stats else 0
            if total == 0:
                continue
            platform_count += 1
            for topic, count in profile.topic_stats.items():
                normalized = count / total
                merged[topic] += normalized

        # Average across platforms
        if platform_count > 0:
            for topic in merged:
                merged[topic] = round(merged[topic] / platform_count, 4)

        return dict(merged)

    @staticmethod
    def combine_results(profiles: list[ScrapedProfile]) -> dict:
        """Combine results from multiple platforms into a summary dict."""
        total_problems = sum(p.problems_solved for p in profiles)
        ratings = {p.platform: p.contest_rating for p in profiles if p.contest_rating is not None}
        merged_topics = ProfileAggregator.merge_topic_stats(profiles)

        return {
            "total_problems_solved": total_problems,
            "contest_ratings": ratings,
            "merged_topic_stats": merged_topics,
            "platforms": [p.platform for p in profiles],
            "per_platform": {
                p.platform: {
                    "problems_solved": p.problems_solved,
                    "contest_rating": p.contest_rating,
                    "topic_stats": p.topic_stats,
                }
                for p in profiles
            },
        }
