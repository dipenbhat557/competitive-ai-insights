"""Normalizer: turn heterogeneous platform snapshots into one canonical view.

Given a list of platform snapshots (LeetCode, Codeforces, CodeChef, HackerRank)
this produces:

  * Canonical topic stats (single vocabulary)
  * Per-platform rating percentile (0-100) AND a single combined rating
    percentile (max across platforms)
  * Difficulty breakdown (easy/medium/hard/expert) summed across platforms
  * Weighted problem-volume score that respects difficulty AND platform
  * Top platform per topic (where the user is strongest)

The output is consumed by the Insight Generator, the Skill Matcher, and the
profile dashboard so they can reason about the user as a single entity rather
than four disjoint accounts.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

from app.services.normalizer.ratings import (
    DIFFICULTY_BUCKETS,
    rating_to_percentile,
    weighted_volume,
)
from app.services.normalizer.taxonomy import (
    CANONICAL_TOPICS,
    TOPIC_LABELS,
    canonicalize_topic,
)


@dataclass
class NormalizedProfile:
    """Per-platform normalized view."""
    platform: str
    username: str
    problems_solved: int
    raw_rating: Optional[float]
    rating_percentile: Optional[float]
    canonical_topics: dict[str, int] = field(default_factory=dict)
    difficulty_breakdown: dict[str, int] = field(default_factory=dict)
    weighted_volume: float = 0.0


@dataclass
class NormalizedAggregate:
    """User-level aggregate across all linked platforms."""
    platforms: list[str]
    total_problems_raw: int                  # naive sum (kept for transparency)
    total_weighted_volume: float             # difficulty + platform-weighted
    canonical_topic_stats: dict[str, int]    # canonical id -> total problems
    canonical_topic_share: dict[str, float]  # canonical id -> 0-1 share
    difficulty_breakdown: dict[str, int]     # easy/medium/hard/expert (summed)
    per_platform: list[NormalizedProfile]
    rating_percentile_per_platform: dict[str, Optional[float]]
    rating_percentile_overall: Optional[float]   # max across platforms
    top_topic: Optional[str]                     # canonical id, or None
    weakest_known_topic: Optional[str]           # within canonical set, lowest>0
    coverage: int                                # # of canonical topics touched
    label_for: dict[str, str]                    # canonical_id -> pretty label


class Normalizer:
    """Stateless normalizer; methods accept raw snapshot dicts."""

    @staticmethod
    def normalize_snapshot(snapshot: dict[str, Any]) -> NormalizedProfile:
        """Normalize one platform's snapshot dict.

        Expects keys: platform, username (optional), problems_solved,
        contest_rating, topic_stats, raw_data (containing optional 'difficulty').
        """
        platform = (snapshot.get("platform") or "").lower()
        username = snapshot.get("username") or ""
        problems_solved = int(snapshot.get("problems_solved") or 0)
        raw_rating = snapshot.get("contest_rating")

        # Canonicalize topic stats.
        canonical: dict[str, int] = defaultdict(int)
        for raw_name, count in (snapshot.get("topic_stats") or {}).items():
            canonical_id = canonicalize_topic(platform, str(raw_name))
            if not canonical_id:
                continue
            try:
                canonical[canonical_id] += int(count or 0)
            except (TypeError, ValueError):
                continue

        # Difficulty breakdown comes from raw_data.difficulty (set by scrapers
        # that have it; CodeChef approximates from star rating; HackerRank
        # leaves it unset).
        raw_data = snapshot.get("raw_data") or {}
        difficulty = raw_data.get("difficulty") if isinstance(raw_data, dict) else None
        if not isinstance(difficulty, dict):
            difficulty = {}

        # Coerce difficulty keys/values, dropping anything outside the canonical
        # bucket set so callers can rely on the shape.
        clean_difficulty: dict[str, int] = {}
        for bucket in DIFFICULTY_BUCKETS:
            try:
                clean_difficulty[bucket] = int(difficulty.get(bucket) or 0)
            except (TypeError, ValueError):
                clean_difficulty[bucket] = 0

        weighted = weighted_volume(
            platform,
            difficulty_breakdown=clean_difficulty if any(clean_difficulty.values()) else None,
            fallback_total=problems_solved,
        )

        return NormalizedProfile(
            platform=platform,
            username=username,
            problems_solved=problems_solved,
            raw_rating=float(raw_rating) if raw_rating is not None else None,
            rating_percentile=rating_to_percentile(platform, raw_rating),
            canonical_topics=dict(canonical),
            difficulty_breakdown=clean_difficulty,
            weighted_volume=weighted,
        )

    @classmethod
    def aggregate(cls, snapshots: Iterable[dict[str, Any]]) -> NormalizedAggregate:
        """Aggregate multiple snapshot dicts into one normalized view."""
        per_platform: list[NormalizedProfile] = [
            cls.normalize_snapshot(s) for s in snapshots
        ]

        platforms = [p.platform for p in per_platform if p.platform]
        total_raw = sum(p.problems_solved for p in per_platform)
        total_weighted = round(sum(p.weighted_volume for p in per_platform), 2)

        merged_topics: dict[str, int] = defaultdict(int)
        merged_difficulty: dict[str, int] = {b: 0 for b in DIFFICULTY_BUCKETS}

        for p in per_platform:
            for topic, count in p.canonical_topics.items():
                merged_topics[topic] += count
            for bucket, count in p.difficulty_breakdown.items():
                merged_difficulty[bucket] = merged_difficulty.get(bucket, 0) + int(count or 0)

        topic_total = sum(merged_topics.values()) or 1
        topic_share = {
            t: round(v / topic_total, 4) for t, v in merged_topics.items()
        }

        percentile_per_platform = {
            p.platform: p.rating_percentile for p in per_platform
        }
        percentiles_present = [
            v for v in percentile_per_platform.values() if v is not None
        ]
        overall_percentile = round(max(percentiles_present), 2) if percentiles_present else None

        top_topic = max(merged_topics, key=merged_topics.get) if merged_topics else None
        weakest_known = None
        if merged_topics:
            # Lowest non-zero count among topics the user has touched.
            ranked = sorted(merged_topics.items(), key=lambda kv: kv[1])
            weakest_known = next((t for t, v in ranked if v > 0), None)

        coverage = len([t for t in merged_topics if merged_topics[t] > 0])

        # Build labels only for the topics that actually appear.
        label_for = {t: TOPIC_LABELS.get(t, t) for t in merged_topics.keys()}

        return NormalizedAggregate(
            platforms=platforms,
            total_problems_raw=total_raw,
            total_weighted_volume=total_weighted,
            canonical_topic_stats=dict(merged_topics),
            canonical_topic_share=topic_share,
            difficulty_breakdown=merged_difficulty,
            per_platform=per_platform,
            rating_percentile_per_platform=percentile_per_platform,
            rating_percentile_overall=overall_percentile,
            top_topic=top_topic,
            weakest_known_topic=weakest_known,
            coverage=coverage,
            label_for=label_for,
        )

    @staticmethod
    def to_dict(agg: NormalizedAggregate) -> dict[str, Any]:
        """JSON-serializable view of an aggregate (for API responses + prompts)."""
        return {
            "platforms": agg.platforms,
            "total_problems_raw": agg.total_problems_raw,
            "total_weighted_volume": agg.total_weighted_volume,
            "canonical_topic_stats": agg.canonical_topic_stats,
            "canonical_topic_share": agg.canonical_topic_share,
            "difficulty_breakdown": agg.difficulty_breakdown,
            "rating_percentile_per_platform": agg.rating_percentile_per_platform,
            "rating_percentile_overall": agg.rating_percentile_overall,
            "top_topic": agg.top_topic,
            "weakest_known_topic": agg.weakest_known_topic,
            "coverage": agg.coverage,
            "topic_labels": agg.label_for,
            "per_platform": [
                {
                    "platform": p.platform,
                    "username": p.username,
                    "problems_solved": p.problems_solved,
                    "raw_rating": p.raw_rating,
                    "rating_percentile": p.rating_percentile,
                    "canonical_topics": p.canonical_topics,
                    "difficulty_breakdown": p.difficulty_breakdown,
                    "weighted_volume": p.weighted_volume,
                }
                for p in agg.per_platform
            ],
            "all_canonical_topics": CANONICAL_TOPICS,
        }
