from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrapedProfile:
    platform: str
    username: str
    problems_solved: int = 0
    contest_rating: Optional[float] = None
    topic_stats: dict = field(default_factory=dict)
    submission_calendar: dict = field(default_factory=dict)
    raw_data: dict = field(default_factory=dict)


class AbstractPlatformScraper(ABC):
    @abstractmethod
    async def scrape(self, username: str) -> ScrapedProfile:
        ...

    @abstractmethod
    async def validate_username(self, username: str) -> bool:
        ...
