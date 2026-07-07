"""Recursive Language Model — artifact-by-reference with TTL.

Long artifacts (CSVs, JSON dumps, binaries) are stored on disk and
referenced by short id. The LLM context only holds the id + summary.
Lazy-load via resolve() when needed. Prune() handles TTL cleanup.

Example:
    >>> store = ArtifactStore()  # doctest: +SKIP
    >>> art = store.register("s1", b"col1,col2\\n1,2\\n", "csv", "tiny table")  # doctest: +SKIP
    >>> store.resolve("s1", art.id)  # doctest: +SKIP
    b'col1,col2\\n1,2\\n'
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


@dataclass
class Artifact:
    """Handle to a stored artifact."""

    id: str
    kind: str
    path: Path
    bytes: int
    created_at: float
    summary: str = ""

    def short_ref(self) -> str:
        """Return compact reference string for LLM context (~25 tokens)."""
        ago = int((time.time() - self.created_at) / 3600)
        return f"art:{self.id} [{self.kind}, {self.bytes}B, {ago}h, {self.summary!r}]"


class ArtifactStore:
    """Filesystem-backed artifact store keyed by (session, id)."""

    def __init__(self, root: PathLike = "~/.openmneme/artifacts") -> None:
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)

    def _session_dir(self, session: str) -> Path:
        d = self.root / session
        d.mkdir(parents=True, exist_ok=True)
        return d

    def register(
        self,
        session: str,
        data: bytes,
        kind: str,
        summary: str = "",
    ) -> Artifact:
        """Persist data and return a short Artifact handle."""
        sid = uuid.uuid4().hex[:8]
        path = self._session_dir(session) / f"art-{sid}.dat"
        path.write_bytes(data)
        return Artifact(
            id=sid,
            kind=kind,
            path=path,
            bytes=len(data),
            created_at=time.time(),
            summary=summary[:200],
        )

    def resolve(self, session: str, ref: str) -> bytes:
        """Load full artifact by reference. Accepts 'art:<id>' or bare '<id>'."""
        bare = ref.split(":", 1)[-1]
        path = self._session_dir(session) / f"art-{bare}.dat"
        if not path.exists():
            raise ArtifactNotFound(f"{session}/{ref}")
        return path.read_bytes()

    def list(self, session: str) -> list[Artifact]:
        """All artifacts for a session, newest first."""
        sdir = self._session_dir(session)
        out: list[Artifact] = []
        for p in sorted(sdir.glob("art-*.dat"), key=lambda p: -p.stat().st_mtime):
            sid = p.stem[len("art-"):]
            st = p.stat()
            out.append(Artifact(id=sid, kind="unknown", path=p, bytes=st.st_size, created_at=st.st_mtime))
        return out

    def prune(self, ttl_days: int = 7) -> int:
        """Delete artifacts older than TTL. Returns number removed."""
        cutoff = time.time() - ttl_days * 86400
        n = 0
        for p in self.root.rglob("art-*.dat"):
            if p.stat().st_mtime < cutoff:
                p.unlink()
                n += 1
        return n


class ArtifactNotFound(KeyError):
    def __init__(self, ref: str) -> None:
        self.ref = ref
        super().__init__(ref)

    def __str__(self) -> str:
        return f"ArtifactNotFound({self.ref!r})"
