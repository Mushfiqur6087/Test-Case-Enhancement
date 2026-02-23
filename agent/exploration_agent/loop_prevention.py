"""
Lightweight loop prevention for the LLM-guided Exploration Agent.
Tracks visited URLs and detects navigation cycles.
"""

from typing import Dict, List, Set


class LoopPrevention:
    """Tracks visited URLs and detects cycles in recent navigation."""

    def __init__(self, max_recent: int = 12):
        self._visited_urls: Set[str] = set()
        self._recent_urls: List[str] = []
        self._max_recent = max_recent
        self._revisit_counts: Dict[str, int] = {}  # URL -> times revisited

    def is_visited(self, url: str) -> bool:
        """Check if this URL has been visited before."""
        return url in self._visited_urls

    def mark_visited(self, url: str) -> None:
        """Record a URL as visited and track for cycle detection."""
        if url in self._visited_urls:
            self._revisit_counts[url] = self._revisit_counts.get(url, 0) + 1
        self._visited_urls.add(url)
        self._recent_urls.append(url)
        if len(self._recent_urls) > self._max_recent:
            self._recent_urls.pop(0)

    def detect_cycle(self) -> bool:
        """
        Check recent visits for a repeating cycle pattern.
        Returns True if a cycle of length 2-4 is detected repeating.
        """
        visits = self._recent_urls
        if len(visits) < 6:
            return False

        for cycle_len in range(2, 5):
            if len(visits) >= cycle_len * 2:
                recent = visits[-cycle_len:]
                previous = visits[-cycle_len * 2 : -cycle_len]
                if recent == previous:
                    return True

        return False

    def get_revisit_warning(self, url: str) -> str:
        """
        Return a warning string if the LLM keeps revisiting the same URL.
        Empty string if no issue.
        """
        count = self._revisit_counts.get(url, 0)
        if count >= 3:
            return f"WARNING: You have revisited {url} {count} times. Try a different URL."
        return ""

    def get_stats(self) -> Dict[str, int]:
        """Return visit statistics."""
        return {
            "visited_urls": len(self._visited_urls),
            "total_revisits": sum(self._revisit_counts.values()),
        }
