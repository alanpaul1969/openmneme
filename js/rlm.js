// RLM — JS mirror of openmneme.rlm (filesystem artifact store)

import { promises as fs } from "node:fs";
import { join, resolve as pathResolve } from "node:path";
import { homedir } from "node:os";
import { randomBytes } from "node:crypto";

export class Artifact {
  constructor({ id, kind, path, bytes, createdAt, summary = "" }) {
    this.id = id;
    this.kind = kind;
    this.path = path;
    this.bytes = bytes;
    this.createdAt = createdAt;
    this.summary = summary.slice(0, 200);
  }
  shortRef() {
    const ago = Math.max(0, Math.floor((Date.now() / 1000 - this.createdAt) / 3600));
    return `art:${this.id} [${this.kind}, ${this.bytes}B, ${ago}h, ${JSON.stringify(this.summary)}]`;
  }
}

export class ArtifactStore {
  constructor(root = join(homedir(), ".openmneme", "artifacts")) {
    this.root = pathResolve(root);
    fs.mkdir(this.root, { recursive: true }).catch(() => {});
  }

  async _sessionDir(session) {
    const d = join(this.root, session);
    await fs.mkdir(d, { recursive: true });
    return d;
  }

  async register(session, data, kind, summary = "") {
    const sid = randomBytes(4).toString("hex");
    const d = await this._sessionDir(session);
    const p = join(d, `art-${sid}.dat`);
    const buf = Buffer.isBuffer(data) ? data : Buffer.from(data);
    await fs.writeFile(p, buf);
    return new Artifact({
      id: sid,
      kind,
      path: p,
      bytes: buf.length,
      createdAt: Math.floor(Date.now() / 1000),
      summary,
    });
  }

  async resolve(session, ref) {
    const bare = String(ref).split(":").pop();
    const d = await this._sessionDir(session);
    const p = join(d, `art-${bare}.dat`);
    try {
      return await fs.readFile(p);
    } catch (e) {
      throw new ArtifactNotFound(`${session}/${ref}`);
    }
  }

  async list(session) {
    const d = await this._sessionDir(session);
    let names = [];
    try { names = await fs.readdir(d); } catch { return []; }
    const out = [];
    for (const name of names) {
      if (!name.startsWith("art-") || !name.endsWith(".dat")) continue;
      const sid = name.slice(4, -4);
      const p = join(d, name);
      const st = await fs.stat(p);
      out.push(new Artifact({
        id: sid,
        kind: "unknown",
        path: p,
        bytes: st.size,
        createdAt: Math.floor(st.mtimeMs / 1000),
      }));
    }
    return out.sort((a, b) => b.createdAt - a.createdAt);
  }

  async prune(ttlDays = 7) {
    const cutoff = Date.now() / 1000 - ttlDays * 86400;
    let n = 0;
    async function walk(dir) {
      let entries = [];
      try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { return; }
      for (const e of entries) {
        const p = join(dir, e.name);
        if (e.isDirectory()) { await walk(p); continue; }
        if (e.name.startsWith("art-") && e.name.endsWith(".dat")) {
          const st = await fs.stat(p);
          if (st.mtimeMs / 1000 < cutoff) {
            await fs.unlink(p); n++;
          }
        }
      }
    }
    await walk(this.root);
    return n;
  }
}

export class ArtifactNotFound extends Error {
  constructor(ref) { super(`ArtifactNotFound(${JSON.stringify(ref)})`); this.name = "ArtifactNotFound"; this.ref = ref; }
}
