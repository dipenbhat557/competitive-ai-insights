"""Convert platform-specific contest ratings to a comparable 0-100 percentile.

Each platform uses a different ELO-like scale and means very different things:

  Platform     Typical range   Notes
  ----------   -------------   -----
  LeetCode     1500 baseline   contest rating; strong inflation past 2000
  Codeforces   ~800 - 3500     well-published rank bands (newbie ... LGM)
  CodeChef     ~1000 - 2700    reported as star rating (1*..7*); we expect raw int
  HackerRank   ~0   - 3000     less standardized, contest_rating from REST

The percentiles below are *piecewise-linear* approximations of the public
distribution data each platform publishes (and community estimates where
official numbers are unavailable). They are intended to compare *relative
standing*, not to predict job performance.
"""

from typing import Optional


def _piecewise(value: float, anchors: list[tuple[float, float]]) -> float:
    """Linear-interpolate `value` against (x, y) anchor pairs (x ascending)."""
    if value <= anchors[0][0]:
        return anchors[0][1]
    if value >= anchors[-1][0]:
        return anchors[-1][1]
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        if x0 <= value <= x1:
            t = (value - x0) / (x1 - x0) if x1 != x0 else 0.0
            return y0 + t * (y1 - y0)
    return anchors[-1][1]


# ---- per-platform anchors (raw_rating -> percentile) ----------------------

# Sources: LeetCode community percentile estimates published in user blogs +
# the platform's own "Top X%" badges shown on contest pages.
_LEETCODE_ANCHORS: list[tuple[float, float]] = [
    (1300, 10),
    (1500, 35),     # ~median active competitor
    (1700, 60),
    (1900, 80),
    (2100, 92),     # "Knight" badge territory
    (2300, 97),     # "Guardian" ~top 5%
    (2600, 99.5),
]

# Codeforces publishes its rank distribution; numbers below approximate the
# % of *rated* users at-or-below each band edge.
_CODEFORCES_ANCHORS: list[tuple[float, float]] = [
    (1200, 30),     # newbie ceiling
    (1400, 50),     # pupil ceiling
    (1600, 70),     # specialist ceiling
    (1900, 85),     # expert ceiling
    (2100, 92),     # candidate-master ceiling
    (2300, 96),     # master ceiling
    (2400, 98),     # IM ceiling
    (2600, 99),     # GM ceiling
    (3000, 99.9),
]

# CodeChef stars: 1*<=1399, 2*<=1599, 3*<=1799, 4*<=1999, 5*<=2199,
# 6*<=2499, 7*>=2500. Percentiles approximate community estimates.
_CODECHEF_ANCHORS: list[tuple[float, float]] = [
    (1399, 35),     # 1-star ceiling
    (1599, 60),     # 2-star ceiling
    (1799, 78),     # 3-star ceiling
    (1999, 88),     # 4-star ceiling
    (2199, 94),     # 5-star ceiling
    (2499, 98),     # 6-star ceiling
    (2700, 99.5),
]

# HackerRank doesn't publish distributions; estimate conservatively.
_HACKERRANK_ANCHORS: list[tuple[float, float]] = [
    (1000, 25),
    (1500, 50),
    (2000, 75),
    (2500, 92),
    (3000, 99),
]


def rating_to_percentile(platform: str, rating: Optional[float]) -> Optional[float]:
    """Return 0-100 percentile for a raw platform rating, or None if unknown."""
    if rating is None:
        return None
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return None

    plat = platform.lower()
    if plat == "leetcode":
        anchors = _LEETCODE_ANCHORS
    elif plat == "codeforces":
        anchors = _CODEFORCES_ANCHORS
    elif plat == "codechef":
        anchors = _CODECHEF_ANCHORS
    elif plat == "hackerrank":
        anchors = _HACKERRANK_ANCHORS
    else:
        return None

    return round(_piecewise(r, anchors), 2)


# ---- difficulty bucketing -------------------------------------------------

# Canonical difficulty buckets used across the app.
DIFFICULTY_BUCKETS = ["easy", "medium", "hard", "expert"]


def cf_problem_rating_to_bucket(rating: Optional[int]) -> str:
    """Map a Codeforces *problem* rating (e.g. 800, 1500, 2400) to a bucket."""
    if rating is None:
        return "medium"  # CF problems without a rating are usually mid
    if rating < 1200:
        return "easy"
    if rating < 1900:
        return "medium"
    if rating < 2400:
        return "hard"
    return "expert"


def cc_stars_to_bucket(stars: Optional[float]) -> str:
    """Map a CodeChef star count (1-7) or rating to a bucket."""
    if stars is None:
        return "medium"
    if stars <= 2:
        return "easy"
    if stars <= 4:
        return "medium"
    if stars <= 6:
        return "hard"
    return "expert"


# Difficulty *weights* used when computing a normalized "weighted problem
# score" so 100 hards aren't lumped with 100 easies.
DIFFICULTY_WEIGHTS = {
    "easy": 1.0,
    "medium": 2.0,
    "hard": 4.0,
    "expert": 8.0,
}


# Rough platform multiplier for the weighted-volume score. The hierarchy
# reflects that CF problems are typically harder per-rating than LC, and
# HR challenges are easier on average. These are conservative estimates.
PLATFORM_VOLUME_WEIGHTS = {
    "leetcode": 1.0,
    "codeforces": 1.2,
    "codechef": 1.0,
    "hackerrank": 0.7,
}


def weighted_volume(
    platform: str,
    difficulty_breakdown: dict[str, int] | None,
    fallback_total: int = 0,
) -> float:
    """Compute a weighted problem-volume score.

    If `difficulty_breakdown` is missing/empty, falls back to treating
    `fallback_total` as 100% medium.
    """
    plat_w = PLATFORM_VOLUME_WEIGHTS.get(platform.lower(), 1.0)
    if not difficulty_breakdown:
        return round(fallback_total * DIFFICULTY_WEIGHTS["medium"] * plat_w, 2)
    score = 0.0
    for bucket, count in difficulty_breakdown.items():
        w = DIFFICULTY_WEIGHTS.get(bucket, DIFFICULTY_WEIGHTS["medium"])
        score += float(count or 0) * w
    return round(score * plat_w, 2)
