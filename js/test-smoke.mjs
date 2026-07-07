// Smoke tests for all 4 JS primitives. Run with: node js/test-smoke.mjs

import assert from "node:assert/strict";
import { parse, argsAfter, invoke, SkillNotFound } from "./slash-skill.js";
import { Plan, AlreadyInPlan, NotInPlan } from "./plan-mode.js";
import { shouldReview, gate, ReviewVerdict } from "./reviewer-gate.js";
import { ArtifactStore } from "./rlm.js";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// 1. slash-skill
assert.equal(parse("/weather Tokyo"), "weather");
assert.equal(parse("/plan"), "plan");
assert.equal(parse("hello world"), null);
assert.equal(parse("/BadName"), null);
assert.equal(argsAfter("/weather Tokyo"), "Tokyo");
const v = await invoke("echo", { echo: () => "ok" });
assert.equal(v, "ok");
await assert.rejects(() => invoke("nope", {}), SkillNotFound);
console.log("  [1/4] slash-skill OK");

// 2. plan-mode
const p = new Plan("s1");
p.enter("migrate").write(["a", "b"]).exit(true);
assert.equal(p.approved, true);
assert.equal(p.mode, "build");
assert.deepEqual(p.todos, ["a", "b"]);
// Re-enter then try to enter again -> AlreadyInPlan
p.enter("second");
assert.throws(() => p.enter("third"), (e) => e instanceof AlreadyInPlan);
const p2 = new Plan("s2");
assert.throws(() => p2.write(["x"]), (e) => e instanceof NotInPlan);
p2.enter("g").write(["x"]).exit(false);
assert.equal(p2.approved, false);
console.log("  [2/4] plan-mode OK");

// 3. reviewer-gate
assert.equal(await shouldReview("hi"), false);
assert.equal(await shouldReview("x".repeat(500) + " see fig. 2"), true);
const cleanR = async (t) => new ReviewVerdict(true, [], "haiku");
const dirtyR = async (t) => new ReviewVerdict(false, ["fake ref"], "sonnet");
const v1 = await gate("x".repeat(500), [cleanR]);
assert.equal(v1.clean, true);
const v2 = await gate("x".repeat(500), [cleanR, dirtyR]);
assert.equal(v2.clean, false);
assert.deepEqual(v2.issues, ["fake ref"]);
await assert.rejects(() => gate("x", []), /at least one reviewer/);
console.log("  [3/4] reviewer-gate OK");

// 4. rlm
const tmp = mkdtempSync(join(tmpdir(), "openmneme-js-"));
try {
  const store = new ArtifactStore(tmp);
  const art = await store.register("s1", Buffer.from("col1,col2\n1,2\n"), "csv", "tiny table");
  assert.equal(art.bytes, 14);
  assert.ok(art.shortRef().includes("tiny table"));
  const data = await store.resolve("s1", art.id);
  assert.equal(Buffer.compare(data, Buffer.from("col1,col2\n1,2\n")), 0);
  const list = await store.list("s1");
  assert.equal(list.length, 1);
  await assert.rejects(() => store.resolve("s1", "nope"));
  const n = await store.prune(0);
  assert.ok(n >= 1);
} finally {
  rmSync(tmp, { recursive: true, force: true });
}
console.log("  [4/4] rlm OK");

console.log("\nALL 4 PRIMITIVES: SMOKE OK");
