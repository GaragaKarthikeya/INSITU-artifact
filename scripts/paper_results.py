#!/usr/bin/env python3
"""Validate the archived 12-window grid and regenerate the paper's frontier."""
import argparse
import csv
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def load_grid(path):
    data = json.loads(path.read_text())
    expected = {"baseline"} | {f"k{k}v{v}-{mode}" for k in range(2, 7)
                              for v in range(2, 7) for mode in "AB"}
    if set(data) - {"meta"} != expected:
        raise ValueError("Expected baseline plus all 25 A/B configurations")
    meta = data["meta"]
    if (meta["context"], meta["n_windows"], meta["kv_heads"], meta["head_dim"],
            meta["layers"], meta["dtype"]) != (2048, 12, 8, 64, 16, "float32"):
        raise ValueError("Grid metadata does not match the paper's protocol")
    points = []
    for name in sorted(expected):
        row = data[name]
        if row["windows"] != 12 or row["tokens"] != 12 * 2047:
            raise ValueError(f"Incomplete grid entry: {name}")
        if len(row["per_window"]) != 12:
            raise ValueError(f"Missing per-window measurements: {name}")
        if not math.isclose(math.exp(row["nll"] / row["tokens"]), row["ppl"],
                            rel_tol=1e-10):
            raise ValueError(f"NLL/perplexity mismatch: {name}")
        if name != "baseline":
            k, v = map(int, re.fullmatch(r"k(\d+)v(\d+)-[AB]", name).groups())
            payload = (64 * (k + v) // 8 + 4) * 8
            if row["bytes_per_token_per_layer"] != payload:
                raise ValueError(f"Payload mismatch: {name}")
            if name.endswith("-B"):
                points.append(dict(config=f"{k}/{v}", key_bits=k, value_bits=v,
                                   bytes_per_token_per_layer=payload,
                                   perplexity=row["ppl"]))
    best = {}
    for point in points:
        b = point["bytes_per_token_per_layer"]
        if b not in best or point["perplexity"] < best[b]["perplexity"]:
            best[b] = point
    frontier = []
    lowest = math.inf
    for b, point in sorted(best.items()):
        if point["perplexity"] < lowest:
            frontier.append(point)
            lowest = point["perplexity"]
    return data["baseline"]["ppl"], frontier


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", type=Path,
                    default=ROOT / "results/llama32-grid/results.json")
    ap.add_argument("--out", type=Path, default=ROOT / "results/generated")
    ap.add_argument("--check-only", action="store_true")
    args = ap.parse_args()
    baseline, points = load_grid(args.results)
    print(f"Validated 51 configurations, 12 windows each; baseline {baseline:.4f}")
    for p in points:
        print(f"{p['config']:>3}  {p['bytes_per_token_per_layer']:3} B/token/layer  "
              f"perplexity {p['perplexity']:.4f}")
    if args.check_only:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "frontier.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(points[0]))
        writer.writeheader()
        writer.writerows(points)
    fig, ax = plt.subplots(figsize=(6.2, 3.1))
    ax.plot([p["bytes_per_token_per_layer"] for p in points],
            [p["perplexity"] for p in points], "o--", label="Pareto frontier")
    ax.axhline(baseline, color="0.35", linestyle=":", label="Unmodified baseline")
    for p in points:
        ax.annotate(p["config"], (p["bytes_per_token_per_layer"], p["perplexity"]),
                    xytext=(5, 7), textcoords="offset points", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlim(260, 850)
    ax.set_ylim(8, 150)
    ax.set_yticks([10, 20, 50, 100], labels=["10", "20", "50", "100"])
    ax.set_xticks([288, 416, 544, 672, 800])
    ax.set_xlabel("KV bytes / token / layer")
    ax.set_ylabel("Perplexity (lower is better)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(args.out / f"figure1.{ext}", dpi=200)
    plt.close(fig)
    print(f"Wrote figure and CSV to {args.out}")


if __name__ == "__main__":
    main()
