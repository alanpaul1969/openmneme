"""OpenMneme — primitives for local-first AI agents.

v0.1.0 — 4 primitives:
- openmneme.slash_skill : /skill-name invocation protocol
- openmneme.plan_mode   : read-only pre-execution planning gate
- openmneme.reviewer_gate : blind adversarial audit
- openmneme.rlm         : artifact-by-reference with TTL
"""

from openmneme import slash_skill, plan_mode, reviewer_gate, rlm

__version__ = "0.1.0"
__all__ = ["slash_skill", "plan_mode", "reviewer_gate", "rlm", "__version__"]
