// Reviewer Gate — JS mirror of openmneme.reviewer_gate

const TRIGGER = /(\d{2,}|\.csv|\.tsv|\.png|\.jpg|fig\.|et al\.)/i;

export class ReviewVerdict {
  constructor(clean, issues = [], reviewer = "default", model = null) {
    this.clean = Boolean(clean);
    this.issues = Array.from(issues);
    this.reviewer = reviewer;
    this.model = model;
  }
  get ok() { return this.clean; }
}

export async function shouldReview(text, threshold = 400) {
  if (!text || text.length < threshold) return false;
  return TRIGGER.test(text);
}

export async function gate(text, reviewers, onClean = null) {
  if (!Array.isArray(reviewers) || reviewers.length === 0) {
    throw new Error("at least one reviewer required");
  }
  const verdicts = await Promise.all(reviewers.map(r => Promise.resolve(r(text))));
  const bad = verdicts.filter(v => !v.clean);
  if (bad.length) {
    return new ReviewVerdict(
      false,
      bad.flatMap(v => v.issues.length ? v.issues : ["(reviewer reported no specific issues)"]),
      bad[0].reviewer,
      bad[0].model
    );
  }
  if (onClean) {
    const h = onClean(text);
    if (h && typeof h.then === "function") await h;
  }
  return verdicts[0];
}
