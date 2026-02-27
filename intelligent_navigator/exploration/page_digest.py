"""
Page digest: compact page representation cached per page template.

Populated by the Explorer agent (LLM-based Pass 2 filtering + summary).
Consumed by the Navigator agent to reduce selector map noise.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from intelligent_navigator.exploration.page_identity import PageIdentityComputer


@dataclass
class PageDigest:
    """Cached page analysis: LLM-filtered element indexes + summary."""

    summary: str = ""                                 # LLM-generated page summary
    keep_indexes: Set[int] = field(default_factory=set)  # Element indexes to show Navigator


class PageDigestCache:
    """
    Shared cache: populated by Explorer, consumed by Navigator.
    Keyed by normalized page template so revisits don't need another LLM call.
    """

    def __init__(self, page_identity_computer: PageIdentityComputer):
        self._pic = page_identity_computer
        self._cache: Dict[str, PageDigest] = {}

    def store(self, url: str, digest: PageDigest) -> None:
        template, _, _ = self._pic.normalize_path(url)
        self._cache[template] = digest

    def get(self, url: str) -> Optional[PageDigest]:
        template, _, _ = self._pic.normalize_path(url)
        return self._cache.get(template)

    @property
    def size(self) -> int:
        return len(self._cache)
