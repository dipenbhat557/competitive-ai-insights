"""Canonical topic taxonomy and per-platform alias maps.

Each platform exposes its own topic vocabulary:

    LeetCode    "Dynamic Programming", "Two Pointers", "Hash Table", ...
    Codeforces  "dp", "two pointers", "data structures", "math", ...
    CodeChef    similar to CF (often empty in practice)
    HackerRank  "Algorithms", "Data Structures", "30 Days of Code"  -- umbrella
                                                                       categories

This module collapses them into one canonical set of ~22 topics so
cross-platform aggregation is meaningful.
"""

from typing import Optional


# Canonical topic IDs used everywhere downstream (insights, prompts, matcher).
CANONICAL_TOPICS: list[str] = [
    "dp",
    "graphs",
    "trees",
    "two_pointers",
    "greedy",
    "strings",
    "math",
    "data_structures",
    "binary_search",
    "bit_manipulation",
    "dfs_bfs",
    "sorting",
    "hashing",
    "heap",
    "segment_tree",
    "geometry",
    "backtracking",
    "sliding_window",
    "recursion",
    "stack_queue",
    "linked_list",
    "matrix",
    "simulation",
    "number_theory",
]


# Pretty labels for UI / prompts.
TOPIC_LABELS: dict[str, str] = {
    "dp": "Dynamic Programming",
    "graphs": "Graphs",
    "trees": "Trees",
    "two_pointers": "Two Pointers",
    "greedy": "Greedy",
    "strings": "Strings",
    "math": "Math",
    "data_structures": "Data Structures",
    "binary_search": "Binary Search",
    "bit_manipulation": "Bit Manipulation",
    "dfs_bfs": "DFS / BFS",
    "sorting": "Sorting",
    "hashing": "Hashing",
    "heap": "Heap / Priority Queue",
    "segment_tree": "Segment Tree",
    "geometry": "Geometry",
    "backtracking": "Backtracking",
    "sliding_window": "Sliding Window",
    "recursion": "Recursion",
    "stack_queue": "Stack / Queue",
    "linked_list": "Linked List",
    "matrix": "Matrix",
    "simulation": "Simulation / Implementation",
    "number_theory": "Number Theory",
}


# All alias keys are normalized to lowercase + stripped before lookup.
# Mapping to None means "drop" (e.g. HR umbrella categories).

LEETCODE_ALIASES: dict[str, Optional[str]] = {
    "dynamic programming": "dp",
    "memoization": "dp",
    "graph": "graphs",
    "topological sort": "graphs",
    "shortest path": "graphs",
    "minimum spanning tree": "graphs",
    "tree": "trees",
    "binary tree": "trees",
    "binary search tree": "trees",
    "two pointers": "two_pointers",
    "greedy": "greedy",
    "string": "strings",
    "string matching": "strings",
    "math": "math",
    "geometry": "geometry",
    "number theory": "number_theory",
    "combinatorics": "math",
    "probability and statistics": "math",
    "array": "data_structures",
    "matrix": "matrix",
    "hash table": "hashing",
    "hash function": "hashing",
    "binary search": "binary_search",
    "bit manipulation": "bit_manipulation",
    "bitmask": "bit_manipulation",
    "depth-first search": "dfs_bfs",
    "breadth-first search": "dfs_bfs",
    "sorting": "sorting",
    "bucket sort": "sorting",
    "merge sort": "sorting",
    "quickselect": "sorting",
    "heap (priority queue)": "heap",
    "priority queue": "heap",
    "segment tree": "segment_tree",
    "binary indexed tree": "segment_tree",
    "stack": "stack_queue",
    "queue": "stack_queue",
    "monotonic stack": "stack_queue",
    "monotonic queue": "stack_queue",
    "linked list": "linked_list",
    "doubly-linked list": "linked_list",
    "backtracking": "backtracking",
    "sliding window": "sliding_window",
    "recursion": "recursion",
    "divide and conquer": "recursion",
    "trie": "data_structures",
    "ordered set": "data_structures",
    "union find": "data_structures",
    "design": None,           # too generic
    "interactive": None,
    "shell": None,
    "concurrency": None,
    "database": None,
    "iterator": None,
    "rolling hash": "hashing",
    "simulation": "simulation",
    "enumeration": "simulation",
    "counting": "math",
    "prefix sum": "data_structures",
}


CODEFORCES_ALIASES: dict[str, Optional[str]] = {
    "dp": "dp",
    "graphs": "graphs",
    "graph matchings": "graphs",
    "shortest paths": "graphs",
    "flows": "graphs",
    "trees": "trees",
    "dsu": "data_structures",
    "data structures": "data_structures",
    "two pointers": "two_pointers",
    "greedy": "greedy",
    "strings": "strings",
    "string suffix structures": "strings",
    "hashing": "hashing",
    "math": "math",
    "number theory": "number_theory",
    "combinatorics": "math",
    "probabilities": "math",
    "geometry": "geometry",
    "binary search": "binary_search",
    "ternary search": "binary_search",
    "bitmasks": "bit_manipulation",
    "dfs and similar": "dfs_bfs",
    "sortings": "sorting",
    "implementation": "simulation",
    "brute force": "simulation",
    "constructive algorithms": "math",
    "matrices": "matrix",
    "divide and conquer": "recursion",
    "fft": "math",
    "games": "math",
    "expression parsing": "strings",
    "interactive": None,
    "*special": None,
    "schedules": None,
    "chinese remainder theorem": "number_theory",
    "meet-in-the-middle": "math",
    "ternary": "binary_search",
}


# CodeChef tags overlap heavily with CF; reuse CF mapping as the base.
CODECHEF_ALIASES: dict[str, Optional[str]] = {
    **CODEFORCES_ALIASES,
    "ad-hoc": "simulation",
    "basic programming": "simulation",
}


# HackerRank "topics" are mostly umbrella categories ("Algorithms",
# "Data Structures") rather than specific skills, so most map to None.
HACKERRANK_ALIASES: dict[str, Optional[str]] = {
    "algorithms": None,
    "data structures": None,
    "mathematics": "math",
    "regex": "strings",
    "python": None,
    "java": None,
    "c": None,
    "cpp": None,
    "sql": None,
    "ruby": None,
    "linux shell": None,
    "functional programming": None,
    "ai": None,
    "30 days of code": None,
    "10 days of statistics": None,
    "machine learning": None,
}


PLATFORM_ALIASES: dict[str, dict[str, Optional[str]]] = {
    "leetcode": LEETCODE_ALIASES,
    "codeforces": CODEFORCES_ALIASES,
    "codechef": CODECHEF_ALIASES,
    "hackerrank": HACKERRANK_ALIASES,
}


def canonicalize_topic(platform: str, raw_topic: str) -> Optional[str]:
    """Map a platform-specific topic name to a canonical id, or None to drop."""
    if not raw_topic:
        return None
    aliases = PLATFORM_ALIASES.get(platform.lower())
    if aliases is None:
        return None
    key = raw_topic.strip().lower()
    if key in aliases:
        return aliases[key]
    # Direct match against canonical id (already canonical).
    if key.replace(" ", "_") in CANONICAL_TOPICS:
        return key.replace(" ", "_")
    return None
