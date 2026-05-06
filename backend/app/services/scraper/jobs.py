"""External job scraper.

Pulls live job postings from public job-board APIs:
  * RemoteOK    - https://remoteok.com/api  (JSON, no auth)
  * Greenhouse  - https://boards-api.greenhouse.io/v1/boards/{board}/jobs (no auth)

Both endpoints are publicly documented and serve the same data their hosted
career pages render in the browser, so no login or API key is required.
"""

import asyncio
import re
from dataclasses import dataclass, field
from typing import Any

import httpx


REMOTEOK_URL = "https://remoteok.com/api"
GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"

# Default Greenhouse boards we sample. These are well-known public career pages.
DEFAULT_GREENHOUSE_BOARDS = [
    "stripe",
    "airbnb",
    "gitlab",
    "doordash",
    "robinhood",
]

USER_AGENT = "CodePulse-JobScraper/1.0 (+https://codepulse.dev)"

_TAG_REGEX = re.compile(r"<[^>]+>")
_WS_REGEX = re.compile(r"\s+")


def _strip_html(html: str) -> str:
    if not html:
        return ""
    text = _TAG_REGEX.sub(" ", html)
    text = _WS_REGEX.sub(" ", text).strip()
    return text


@dataclass
class ExternalJob:
    """A job posting fetched from an external public job board."""

    source: str            # "remoteok" | "greenhouse:<board>"
    source_id: str         # stable id within the source
    title: str
    company: str
    description: str
    required_skills: list[str] = field(default_factory=list)
    location: str | None = None
    apply_url: str | None = None
    posted_at: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "required_skills": self.required_skills,
            "location": self.location,
            "apply_url": self.apply_url,
            "posted_at": self.posted_at,
        }


class ExternalJobsScraper:
    """Aggregates jobs from multiple public job boards."""

    def __init__(self, greenhouse_boards: list[str] | None = None):
        self.greenhouse_boards = greenhouse_boards or DEFAULT_GREENHOUSE_BOARDS

    async def fetch_all(self, limit_per_source: int = 25) -> list[ExternalJob]:
        tasks = [self._fetch_remoteok(limit_per_source)]
        for board in self.greenhouse_boards:
            tasks.append(self._fetch_greenhouse(board, limit_per_source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        jobs: list[ExternalJob] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            jobs.extend(result)
        return jobs

    async def _fetch_remoteok(self, limit: int) -> list[ExternalJob]:
        try:
            async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(REMOTEOK_URL)
                if resp.status_code != 200:
                    return []
                data = resp.json()
        except (httpx.HTTPError, ValueError):
            return []

        if not isinstance(data, list):
            return []

        jobs: list[ExternalJob] = []
        # RemoteOK's first array element is metadata; skip it.
        for item in data[1:]:
            if not isinstance(item, dict):
                continue
            position = item.get("position") or item.get("title")
            company = item.get("company")
            if not position or not company:
                continue
            jobs.append(
                ExternalJob(
                    source="remoteok",
                    source_id=str(item.get("id") or item.get("slug") or position),
                    title=position,
                    company=company,
                    description=_strip_html(item.get("description", ""))[:4000],
                    required_skills=[t for t in (item.get("tags") or []) if isinstance(t, str)],
                    location=item.get("location") or "Remote",
                    apply_url=item.get("apply_url") or item.get("url"),
                    posted_at=item.get("date"),
                    raw=item,
                )
            )
            if len(jobs) >= limit:
                break
        return jobs

    async def _fetch_greenhouse(self, board: str, limit: int) -> list[ExternalJob]:
        url = GREENHOUSE_URL.format(board=board)
        try:
            async with httpx.AsyncClient(timeout=20.0, headers={"User-Agent": USER_AGENT}) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return []
                data = resp.json()
        except (httpx.HTTPError, ValueError):
            return []

        postings = data.get("jobs", []) if isinstance(data, dict) else []

        jobs: list[ExternalJob] = []
        for posting in postings[:limit]:
            if not isinstance(posting, dict):
                continue
            title = posting.get("title")
            if not title:
                continue

            description = _strip_html(posting.get("content", ""))[:4000]
            location_obj = posting.get("location") or {}
            location = location_obj.get("name") if isinstance(location_obj, dict) else None

            # Greenhouse exposes departments + metadata; we infer skills from title keywords
            # since structured skill tags aren't always present.
            inferred_skills = _infer_skills_from_text(f"{title} {description}")

            jobs.append(
                ExternalJob(
                    source=f"greenhouse:{board}",
                    source_id=str(posting.get("id") or title),
                    title=title,
                    company=board.capitalize(),
                    description=description,
                    required_skills=inferred_skills,
                    location=location,
                    apply_url=posting.get("absolute_url"),
                    posted_at=posting.get("updated_at"),
                    raw=posting,
                )
            )
        return jobs


# Lightweight keyword extractor used for sources that don't ship skill tags.
_SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "go", "rust", "c++", "kotlin",
    "swift", "scala", "ruby", "php", "react", "next.js", "vue", "angular",
    "node.js", "django", "flask", "fastapi", "spring", "rails",
    "aws", "gcp", "azure", "kubernetes", "docker", "terraform",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "kafka",
    "graphql", "rest", "grpc",
    "machine learning", "deep learning", "nlp", "llm", "pytorch", "tensorflow",
    "data structures", "algorithms", "system design", "distributed systems",
    "frontend", "backend", "fullstack", "full-stack", "devops", "sre",
]


def _infer_skills_from_text(text: str) -> list[str]:
    if not text:
        return []
    lower = text.lower()
    found = []
    for kw in _SKILL_KEYWORDS:
        if kw in lower:
            found.append(kw)
    return found[:12]
