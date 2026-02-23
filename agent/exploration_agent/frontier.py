"""
Exploration queue for the LLM-guided exploration agent.
The LLM decides what to add, skip, and visit next.
This is a simple state tracker, not a priority queue.
"""

from typing import Any, Dict, List, Set

from test_case_enhancer.agent.exploration_agent.models import QueueItem


class ExplorationQueue:
    """Tracks unvisited, visited, and skipped URLs for LLM-guided exploration."""

    def __init__(self):
        self._unvisited: List[QueueItem] = []
        self._visited: List[QueueItem] = []
        self._skipped: List[QueueItem] = []
        self._all_urls: Set[str] = set()  # dedup across all lists

    def add(self, item: QueueItem) -> bool:
        """Add a URL to the unvisited queue. Returns False if already tracked."""
        if item.url in self._all_urls:
            return False
        self._all_urls.add(item.url)
        self._unvisited.append(item)
        return True

    def add_batch(self, items: List[QueueItem]) -> int:
        """Add multiple items. Returns count of newly added."""
        added = 0
        for item in items:
            if self.add(item):
                added += 1
        return added

    def mark_visited(self, url: str) -> None:
        """Move a URL from unvisited to visited."""
        for i, item in enumerate(self._unvisited):
            if item.url == url:
                self._visited.append(self._unvisited.pop(i))
                return
        # URL might not be in unvisited (e.g. navigated directly)
        # Still track it as visited
        if url not in self._all_urls:
            self._all_urls.add(url)
            self._visited.append(QueueItem(url=url, label="", source_page="", reason="direct navigation"))

    def mark_skipped(self, url: str, reason: str = "") -> None:
        """Move a URL from unvisited to skipped."""
        for i, item in enumerate(self._unvisited):
            if item.url == url:
                self._skipped.append(self._unvisited.pop(i))
                return

    def mark_skipped_batch(self, urls: List[str]) -> None:
        """Mark multiple URLs as skipped."""
        for url in urls:
            self.mark_skipped(url)

    def is_known(self, url: str) -> bool:
        """Check if a URL is already tracked in any list."""
        return url in self._all_urls

    def is_visited(self, url: str) -> bool:
        """Check if a URL has been visited."""
        return any(item.url == url for item in self._visited)

    @property
    def unvisited_count(self) -> int:
        return len(self._unvisited)

    @property
    def visited_count(self) -> int:
        return len(self._visited)

    def get_unvisited_urls(self) -> List[str]:
        """Return all unvisited URLs."""
        return [item.url for item in self._unvisited]

    def get_visited_urls(self) -> List[str]:
        """Return all visited URLs."""
        return [item.url for item in self._visited]

    def get_state_summary(self) -> str:
        """
        Return a formatted summary of the queue state for the LLM prompt.
        Shows unvisited and visited URLs with labels.
        """
        lines = []

        lines.append(f"=== Exploration Queue ({self.unvisited_count} unvisited, {self.visited_count} visited) ===")

        if self._unvisited:
            lines.append("\nUnvisited (to explore):")
            for i, item in enumerate(self._unvisited, 1):
                label_str = f" - {item.label}" if item.label else ""
                lines.append(f"  {i}. {item.url}{label_str}")
        else:
            lines.append("\nUnvisited: (empty)")

        if self._visited:
            lines.append("\nAlready Visited:")
            for i, item in enumerate(self._visited, 1):
                label_str = f" - {item.label}" if item.label else ""
                lines.append(f"  {i}. {item.url}{label_str}")

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Return queue statistics."""
        return {
            "unvisited": self.unvisited_count,
            "visited": self.visited_count,
            "skipped": len(self._skipped),
            "total_discovered": len(self._all_urls),
        }
