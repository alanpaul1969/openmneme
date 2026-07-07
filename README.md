# openmneme

Primitives for local-first AI agents. Zero dependencies, pure stdlib.

**v0.1.0** ships four primitives, mirrored in Python and JavaScript:

| Primitive            | Purpose                                                        |
| -------------------- | -------------------------------------------------------------- |
| `slash_skill`        | `/skill-name` invocation protocol — first token is the tool call |
| `plan_mode`          | Read-only pre-execution planning gate (`enter / write / exit`) |
| `reviewer_gate`      | Blind adversarial audit, fire-and-forget, parallel reviewers   |
| `rlm`                | Artifact-by-reference with TTL — store big blobs, pass tiny refs to LLM |

## Install

```bash
pip install openmneme
```

## Quick start

```python
from openmneme import slash_skill, plan_mode, reviewer_gate, rlm
import asyncio

# 1. Slash-skill
print(slash_skill.parse("/weather Tokyo"))   # -> 'weather'
print(slash_skill.args_after("/weather Tokyo"))  # -> 'Tokyo'

# 2. Plan mode
p = plan_mode.Plan(session_id="s1")
p.enter("migrate ingest").write(["read schema", "write migrator", "smoke test"]).exit(True)

# 3. Reviewer gate
async def my_reviewer(text):
    return reviewer_gate.ReviewVerdict(clean=True, issues=[], reviewer="haiku")
verdict = asyncio.run(reviewer_gate.gate("see fig. 1 et al.", [my_reviewer]))

# 4. Artifact store (RLM)
store = rlm.ArtifactStore()  # ~/.openmneme/artifacts
art = store.register("s1", b"col1,col2\n1,2\n", "csv", "tiny table")
print(art.short_ref())  # -> 'art:26028620 [csv, 18B, 0h, "tiny table"]'
data = store.resolve("s1", art.id)  # -> b'col1,col2\n1,2\n'
```

## Design

- **No dependencies** — pure stdlib for Python, zero deps for JS.
- **Async where it matters** — `reviewer_gate` and `rlm` are async-native; `slash_skill` and `plan_mode` are sync.
- **Errors as values** — each primitive raises a typed exception (e.g. `SkillNotFound`, `PlanError`, `ArtifactNotFound`).
- **Cross-language symmetry** — Python and JS expose the same method names.

## Roadmap

- **v0.2.0** — `prune()` cron hook, reviewer pool presets (haiku / sonnet / opus), Hermes skill bridge.
- **v0.3.0** — Provenance DAG (artifact → review → plan chain), remote artifact store.
- **v1.0.0** — Stable API, real-world integrations (Hermes, AutoPKM, OpenScience).

## License

Apache-2.0

## Links

- PyPI: https://pypi.org/project/openmneme/
- npm: https://www.npmjs.com/package/openmneme
- GitHub: https://github.com/alanpaul1969/openmneme
