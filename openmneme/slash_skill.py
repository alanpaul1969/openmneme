"""Slash-skill invocation protocol.

When a user message starts with /<name>, the FIRST output token MUST be
a tool call to that skill — no preamble, no "Loading X...".

Example:
    >>> parse("/weather Tokyo")
    'weather'
    >>> parse("/plan")
    'plan'
    >>> parse("hello world")
    None
    >>> parse("/BadName")  # uppercase rejected
    None
"""

from __future__ import annotations

import re
from typing import Awaitable, Callable, Union

# Slash command = message starts with /<name>; remainder (after first whitespace) is the arg string.
# We only match the prefix so skills can parse their own arguments.
SLASH_PATTERN = re.compile(r"^/([a-z][a-z0-9-]{0,63})(?:\s|$)")

SyncOrAsyncResult = Union[str, Awaitable[str]]


def parse(message: str) -> str | None:
    """Return skill name if message is a slash command, else None.

    The match only inspects the prefix; the rest of the line is the
    skill's own argument string (e.g. "/weather Tokyo" -> skill='weather', args='Tokyo').
    """
    m = SLASH_PATTERN.match((message or "").strip())
    return m.group(1) if m else None


def args_after(message: str) -> str:
    """Return the argument string after the slash command, or '' if none."""
    m = SLASH_PATTERN.match((message or "").strip())
    if not m:
        return ""
    rest = (message or "").strip()[m.end():]
    return rest.strip()


async def invoke(name: str, registry: dict[str, Callable[..., SyncOrAsyncResult]]) -> str:
    """Resolve and call a skill from the registry.

    Supports both sync and async callables.

    Raises:
        SkillNotFound: when name is not in registry.
    """
    if name not in registry:
        raise SkillNotFound(name)
    fn = registry[name]
    result = fn()
    if hasattr(result, "__await__"):
        result = await result
    return str(result)


class SkillNotFound(KeyError):
    """Raised when a slash-skill name is not in the registry."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"/{name} not in registry")

    def __str__(self) -> str:
        return f"SkillNotFound(/{self.name})"
