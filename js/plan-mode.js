// Plan Mode — JS mirror of openmneme.plan_mode

export class Plan {
  constructor(sessionId, goal = "", todos = []) {
    this.sessionId = sessionId;
    this.goal = goal;
    this.todos = [...todos];
    this.mode = "build";      // "build" | "plan"
    this.approved = false;
  }

  enter(goal) {
    if (this.mode === "plan") throw new AlreadyInPlan(this.sessionId);
    this.mode = "plan";
    this.goal = goal;
    this.approved = false;
    return this;
  }

  write(items) {
    if (this.mode !== "plan") throw new NotInPlan(this.sessionId);
    this.todos = Array.from(items);
    return this;
  }

  exit(approved) {
    if (this.mode !== "plan") throw new NotInPlan(this.sessionId);
    this.approved = Boolean(approved);
    this.mode = "build";
    return this;
  }

  reset() {
    this.goal = "";
    this.todos = [];
    this.approved = false;
    this.mode = "build";
    return this;
  }
}

export class PlanError extends Error {}
export class AlreadyInPlan extends PlanError {
  constructor(sessionId) { super(`session ${sessionId} already in plan mode`); this.name = "AlreadyInPlan"; this.sessionId = sessionId; }
}
export class NotInPlan extends PlanError {
  constructor(sessionId) { super(`session ${sessionId} not in plan mode`); this.name = "NotInPlan"; this.sessionId = sessionId; }
}
