#!/usr/bin/env python3
"""Check SHA-256 hashes for the source release, without importing the model."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    count = 0
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Checksum mismatch: {name}")
        count += 1
    print(f"Verified {count} source-release file hashes.")


if __name__ == "__main__":
    main()
