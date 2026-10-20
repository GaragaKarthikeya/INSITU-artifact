#!/usr/bin/env python3
"""Regenerate every golden in a temporary directory and compare its bytes."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    expected = ROOT / "tb" / "vectors"
    with tempfile.TemporaryDirectory(prefix="insitu-vectors-") as d:
        actual = Path(d)
        subprocess.run([sys.executable, "-m", "kernel.hw.vectors", "--ctx", "64",
                        "--seed", "0", "--key-bits", "4", "--value-bits", "2",
                        "--out", str(actual)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
        names = {p.name for p in expected.iterdir() if p.is_file()}
        generated = {p.name for p in actual.iterdir() if p.is_file()}
        differences = sorted(names ^ generated)
        differences += sorted(n for n in names & generated
                              if (expected / n).read_bytes() != (actual / n).read_bytes())
        if differences:
            raise SystemExit("Golden differences: " + ", ".join(differences))
        print(f"All {len(names)} committed golden files regenerate byte-for-byte.")


if __name__ == "__main__":
    main()
