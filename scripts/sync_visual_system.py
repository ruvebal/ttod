#!/usr/bin/env python3
"""Synchronize the canonical visual contract into isolated build contexts."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shared" / "visual-system"
TARGETS = (
    ROOT / "docs" / "public" / "assets" / "visual-system",
    ROOT / "services" / "frontend" / "public" / "visual-system",
)


def files(directory: Path) -> list[Path]:
    return sorted(path for path in directory.iterdir() if path.is_file())


def check() -> int:
    drift: list[str] = []
    expected = {path.name: path.read_bytes() for path in files(SOURCE)}
    for target in TARGETS:
        actual_names = {path.name for path in files(target)} if target.exists() else set()
        if actual_names != set(expected):
            drift.append(str(target.relative_to(ROOT)))
            continue
        for name, content in expected.items():
            if (target / name).read_bytes() != content:
                drift.append(str((target / name).relative_to(ROOT)))
    if drift:
        print("Visual-system drift: " + ", ".join(drift), file=sys.stderr)
        return 1
    print("PASS: shared visual system is synchronized")
    return 0


def sync() -> int:
    expected = {path.name for path in files(SOURCE)}
    for target in TARGETS:
        target.mkdir(parents=True, exist_ok=True)
        for stale in files(target):
            if stale.name not in expected:
                stale.unlink()
        for source in files(SOURCE):
            shutil.copyfile(source, target / source.name)
    return check()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail instead of synchronizing drift")
    args = parser.parse_args()
    return check() if args.check else sync()


if __name__ == "__main__":
    raise SystemExit(main())
