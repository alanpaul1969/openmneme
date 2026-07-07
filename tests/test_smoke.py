"""Smoke tests for all 4 primitives. Run with: python3 tests/test_smoke.py"""

import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openmneme import slash_skill, plan_mode, reviewer_gate, rlm


def test_slash_skill():
    assert slash_skill.parse("/weather Tokyo") == "weather"
    assert slash_skill.parse("/plan") == "plan"
    assert slash_skill.parse("hello world") is None
    assert slash_skill.parse("/BadName") is None
    assert slash_skill.args_after("/weather Tokyo") == "Tokyo"
    assert slash_skill.args_after("/plan") == ""

    async def run():
        reg = {"echo": lambda: "ok", "async_echo": lambda: asyncio.sleep(0, "async-ok")}
        assert await slash_skill.invoke("echo", reg) == "ok"
        assert await slash_skill.invoke("async_echo", reg) == "async-ok"
        try:
            await slash_skill.invoke("nope", reg)
        except slash_skill.SkillNotFound as e:
            assert e.name == "nope"
        else:
            raise AssertionError("expected SkillNotFound")

    asyncio.run(run())
    print("  [1/4] slash_skill OK")


def test_plan_mode():
    p = plan_mode.Plan(session_id="s1")
    p.enter("goal A").write(["a", "b"]).exit(True)
    assert p.approved and p.mode == "build" and p.todos == ["a", "b"]

    p.enter("goal B").write(["c"])
    try:
        p.enter("goal C")  # already in plan
    except plan_mode.AlreadyInPlan:
        pass
    else:
        raise AssertionError("expected AlreadyInPlan")

    p2 = plan_mode.Plan(session_id="s2")
    try:
        p2.write(["x"])  # not in plan
    except plan_mode.NotInPlan:
        pass
    else:
        raise AssertionError("expected NotInPlan")
    p2.enter("g").write(["x"]).exit(False)
    assert p2.approved is False and p2.mode == "build"
    print("  [2/4] plan_mode OK")


def test_reviewer_gate():
    assert asyncio.run(reviewer_gate.should_review("hi")) is False
    long_with_fig = "x" * 500 + " see fig. 2"
    assert asyncio.run(reviewer_gate.should_review(long_with_fig)) is True

    async def clean_rv(text):
        return reviewer_gate.ReviewVerdict(clean=True, issues=[], reviewer="haiku")

    async def dirty_rv(text):
        return reviewer_gate.ReviewVerdict(clean=False, issues=["fake ref"], reviewer="sonnet")

    v1 = asyncio.run(reviewer_gate.gate("x" * 500, [clean_rv]))
    assert v1.clean and v1.reviewer == "haiku"

    v2 = asyncio.run(reviewer_gate.gate("x" * 500, [clean_rv, dirty_rv]))
    assert not v2.clean and "fake ref" in v2.issues and v2.reviewer == "sonnet"

    try:
        asyncio.run(reviewer_gate.gate("x" * 500, []))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for empty reviewers")

    print("  [3/4] reviewer_gate OK")


def test_rlm():
    with tempfile.TemporaryDirectory() as tmp:
        store = rlm.ArtifactStore(root=tmp)
        art = store.register("s1", b"col1,col2\n1,2\n", "csv", "tiny table")
        assert art.bytes == 14
        assert "tiny table" in art.short_ref()
        assert store.resolve("s1", art.id) == b"col1,col2\n1,2\n"
        assert store.resolve("s1", f"art:{art.id}") == b"col1,col2\n1,2\n"
        assert len(store.list("s1")) == 1

        try:
            store.resolve("s1", "nope")
        except rlm.ArtifactNotFound:
            pass
        else:
            raise AssertionError("expected ArtifactNotFound")

        # prune
        store.register("s1", b"old", "text")
        n = store.prune(ttl_days=0)
        assert n >= 1
    print("  [4/4] rlm OK")


if __name__ == "__main__":
    test_slash_skill()
    test_plan_mode()
    test_reviewer_gate()
    test_rlm()
    print("\nALL 4 PRIMITIVES: SMOKE OK")
