// Slash-skill invocation — JS mirror of openmneme.slash_skill
// Pure regex, zero deps. Async-aware via the invoke() helper.

const SLASH_PATTERN = /^\/([a-z][a-z0-9-]{0,63})(?:\s|$)/;

export function parse(message) {
  if (!message) return null;
  const m = SLASH_PATTERN.exec(String(message).trim());
  return m ? m[1] : null;
}

export function argsAfter(message) {
  if (!message) return "";
  const m = SLASH_PATTERN.exec(String(message).trim());
  if (!m) return "";
  return String(message).trim().slice(m[0].length).trim();
}

export async function invoke(name, registry) {
  if (!(name in registry)) throw new SkillNotFound(name);
  const fn = registry[name];
  const result = await fn();
  return String(result);
}

export class SkillNotFound extends Error {
  constructor(name) {
    super(`/${name} not in registry`);
    this.name = "SkillNotFound";
    this.skillName = name;
  }
}

export { SLASH_PATTERN };
