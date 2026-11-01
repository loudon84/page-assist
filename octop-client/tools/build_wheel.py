#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(DIST), str(ROOT)]
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        return result.returncode
    wheels = sorted(DIST.glob("page_assist_octop_client-*.whl")) + sorted(DIST.glob("page-assist-octop-client-*.whl"))
    if not wheels:
        print("wheel missing", file=sys.stderr)
        return 1
    wheel = wheels[-1]
    digest = sha256_file(wheel)
    (DIST / "SHA256SUMS").write_text(f"{digest}  {wheel.name}\n", encoding="utf-8")
    print(wheel.name, digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
