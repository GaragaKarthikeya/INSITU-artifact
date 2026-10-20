# Claims and archived evidence

The selected source comes from development commit recorded in
`source-manifest.json`. Untracked completed Llama results and ignored board logs
were included explicitly. Raw evidence is copied unchanged, including original
paths and timestamps. Arithmetic and RTL were not changed during extraction.
The development checkout's committed test vectors were stale relative to the
current model; `tb/vectors/` was regenerated from that model for this release.
The source manifest retains their original hashes and identifies their origin.
Fixing the test suite's source-search path also exposed a legacy demo that used
the wrong rotation constructor; that unrelated demo was excluded.

| Paper result | Included evidence | Scope |
|---|---|---|
| 79.7% payload reduction | `kernel/ops/quantize.py`, `kernel/hw/ddr_layout.py` | 52 B per KV head, 416 B per layer, compared with 2,048 B FP16; excludes DDR padding |
| Figure 1, 12-window frontier | `results/llama32-grid/results.json`, `run.log`, `events.jsonl`; `scripts/paper_results.py` | Host software sweep, all 16 Llama layers, 25 allocations, A/B paths; baseline 9.3895, B k4v2 11.1043 |
| 16,384 matching layer steps | `results/step15_exactness_ctx1024.log` | Live hardware run through context 1,024, all 16 layers |
| Board perplexity 9.074 → 10.640 | `results/step15_perplexity_4096.log` | 4,096 contiguous tokens, historical hardware-in-loop run, per-step comparison disabled |
| Layer latency 30–330 µs | `results/step14_dma_f250.log` | DMA path, contexts 64–8,192, synthetic self-tests |
| Long-context scan throughput | `results/step14_longctx_probe.log` | PRNG scan probe through 32,768 rows; no attention-output verification |
| DDR queue-depth selection | `results/step1_ddr_sweep_run*.log` | Four sequential read streams; not general memcpy bandwidth |
| 250 MHz implementation | `results/attndma_f250_impl_timing.rpt`, `results/attndma_f250_impl_util.rpt` | Archived full-system routed reports; no new implementation run |
| Per-block timing and resources | `results/step5_*`, `results/step6_*` | Archived early standalone rotation/encoding reports |

## Historical board results and the current source

The development log states that the 4,096-token board result **predates moving
the host float-to-fixed cast to after RoPE**. That experiment has not been
remeasured after the change. The included current source models the cast at
the post-RoPE stream boundary. The older live exactness log is likewise a
historical measurement, not a fresh validation of this release's host path.

The software grid uses twelve independent 2,048-token windows with cache reset
and blank-line corpus joins. The board perplexity script joins rows with an
empty string and processes one contiguous, growing context. The software sweep
also uses a batched arithmetic path, while the FPGA uses online softmax.
These differences are why the two baseline/perplexity pairs must remain
separate in reporting.

The software grid was completed before later optional key-bias handling was
added for other checkpoints. That option is off for this Llama experiment.
The exact checkpoint revision, original package lockfile, and the source commit
of every historical board run were not recorded; the release does not claim
those details can be recovered.

The original README used both “FP16 baseline” and “fp32 baseline” in discussing
quality. The archived grid records `dtype: float32`, and its baseline is the
unmodified model. FP16 is the **cache-payload comparison**. The reproduction
instructions use that distinction explicitly.

## What the release checks establish

`validation.md` records checks actually run on this extracted tree. They cover
the reference implementation, C/Python protocol consistency, vector
regeneration, and RTL simulation. They do not rerun the paper's Llama corpus
sweep, program a board, or establish an end-to-end speedup over another device.
