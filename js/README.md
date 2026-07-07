# openmneme (npm)

JavaScript mirror of the 4 Python primitives. Zero dependencies, ESM + CJS friendly.

```js
import { parse, args_after, invoke, SkillNotFound } from "openmneme/slash-skill.js";
import { Plan, AlreadyInPlan, NotInPlan } from "openmneme/plan-mode.js";
import { shouldReview, gate, ReviewVerdict } from "openmneme/reviewer-gate.js";
import { ArtifactStore, ArtifactNotFound } from "openmneme/rlm.js";

parse("/weather Tokyo");        // -> "weather"
argsAfter("/weather Tokyo");    // -> "Tokyo"

const p = new Plan("s1");
p.enter("migrate").write(["read", "write"]).exit(true);

const verdict = await gate(longText, [async (t) => new ReviewVerdict(true, [], "haiku")]);

const store = new ArtifactStore();
const art = store.register("s1", Buffer.from("col1,col2\n1,2\n"), "csv", "tiny");
const data = store.resolve("s1", art.id);
```

## License

Apache-2.0
