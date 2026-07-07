"""Plan Mode — read-only pre-execution planning gate.

Three transitions: enter (read-only), write (plan items), exit (approved|rejected).
After exit, mode is back to 'build' and plan is either approved (proceed) or not
(rewrite).

Example:
    >>> p = Plan(session_id="s1", goal="", todos=[])
    >>> p.enter("migrate ingest").write(["read schema", "write migrator", "smoke test"]).exit(True)
    Plan(session_id='s1', goal='migrate ingest', mode='build', approved=True, ...)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Mode = Literal["build", "plan"]


@dataclass
class Plan:
    """In-memory plan state. Single session = single Plan instance.

    Pure stdlib: safe to serialize via dataclasses.asdict / json.
    """

    session_id: str
    goal: str = ""
    todos: list[str] = field(default_factory=list)
    mode: Mode = "build"
    approved: bool = False

    def enter(self, goal: str) -> "Plan":
        """Switch to read-only plan mode with a goal."""
        if self.mode == "plan":
            raise AlreadyInPlan(self.session_id)
        self.mode = "plan"
        self.goal = goal
        self.approved = False
        return self

    def write(self, items: list[str]) -> "Plan":
        """Replace todos (last-write-wins). Requires plan mode."""
        if self.mode != "plan":
            raise NotInPlan(self.session_id)
        self.todos = list(items)
        return self

    def exit(self, approved: bool) -> "Plan":
        """Leave plan mode. approved=True proceeds to build."""
        if self.mode != "plan":
            raise NotInPlan(self.session_id)
        self.approved = bool(approved)
        self.mode = "build"
        return self

    def reset(self) -> "Plan":
        """Wipe plan (next round)."""
        self.goal = ""
        self.todos = []
        self.approved = False
        self.mode = "build"
        return self


class PlanError(Exception):
    """Base class for plan mode errors."""


class AlreadyInPlan(PlanError):
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"session {session_id!r} already in plan mode")


class NotInPlan(PlanError):
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(f"session {session_id!r} not in plan mode")
