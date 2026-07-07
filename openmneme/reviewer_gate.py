"""Blind Reviewer Gate — fire-and-forget adversarial audit.

Decide whether a piece of text warrants review (skip short / casual),
then run one or more reviewers in parallel and return the worst verdict.

Example:
    >>> import asyncio
    >>> async def fake_rv(text): return ReviewVerdict(clean=True, issues=[], reviewer="haiku")
    >>> asyncio.run(gate("Hello world", [fake_rv]))
    ReviewVerdict(clean=True, issues=[], reviewer='haiku')
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional

# Trigger patterns: 2+ digits, file refs, figure refs, citation patterns
_TRIGGER = re.compile(r"(\d{2,}|\.csv|\.tsv|\.png|\.jpg|fig\.|et al\.|\\cite)", re.I)

Reviewer = Callable[[str], Awaitable["ReviewVerdict"]]


@dataclass
class ReviewVerdict:
    """Result of a single reviewer pass."""

    clean: bool
    issues: list[str] = field(default_factory=list)
    reviewer: str = "default"
    model: Optional[str] = None

    def __bool__(self) -> bool:  # truthy iff clean
        return self.clean


async def should_review(text: str, threshold: int = 400) -> bool:
    """Heuristic: review long text containing citations/figures/numbers.

    Args:
        text: artifact body.
        threshold: minimum character count to consider (default 400).
    """
    if not text or len(text) < threshold:
        return False
    return bool(_TRIGGER.search(text))


async def gate(
    text: str,
    reviewers: list[Reviewer],
    on_clean: Optional[Callable[[str], Awaitable[None] | None]] = None,
) -> ReviewVerdict:
    """Run all reviewers in parallel, return the worst combined verdict.

    Args:
        text: artifact to review.
        reviewers: list of async callables(text) -> ReviewVerdict.
        on_clean: optional async hook fired iff every reviewer says clean.

    Returns:
        ReviewVerdict with clean=False and merged issues if any reviewer
        found a problem; otherwise a clean verdict from the first reviewer.
    """
    if not reviewers:
        raise ValueError("at least one reviewer required")

    verdicts = await asyncio.gather(*[r(text) for r in reviewers])
    bad = [v for v in verdicts if not v.clean]

    if bad:
        issues = [i for v in bad for i in v.issues]
        return ReviewVerdict(
            clean=False,
            issues=issues or ["(reviewer reported no specific issues)"],
            reviewer=bad[0].reviewer,
            model=bad[0].model,
        )

    if on_clean is not None:
        hook = on_clean(text)
        if hasattr(hook, "__await__"):
            await hook

    return verdicts[0]
