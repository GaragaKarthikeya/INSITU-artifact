# INSITU

**Reconstruction-Free Attention over a Compressed KV Cache on FPGA**

INSITU computes attention directly from quantized cache codes on a Xilinx
ZCU104. Query-dependent tables score the keys, four shared weighted-centroid
products accumulate the values, and an online softmax processes the context
in one scan. Outputs stay in the rotated basis; the inverse rotation is folded
into the host's output projection.

The implemented configuration is Llama-3.2-1B, 64 components per head,
four-bit keys and two-bit values, eight KV heads processed sequentially,
and four query lanes sharing each fetched cache row, at 250 MHz.

This is the software and hardware artifact accompanying the INSITU paper by
Karthikeya Garaga, Lohith Prapoorna Chandra Gonuguntla, and Madhav Rao,
International Institute of Information Technology Bangalore.

## What is included

| Path | Contents |
|---|---|
| `kernel/` | NumPy reference, fixed-point arithmetic, model adapter, host clients, evaluation runners, and tests |
| `rtl/` | SystemVerilog attention engine and DDR reader/writer |
| `tb/` | Twelve self-checking benches and regenerated golden vectors |
| `sw/` | A53 firmware, UDP/lwIP server, and supporting raw Ethernet code |
| `host/` | XSDB board launchers |
| `scripts/` | Vector checks, figure generation, simulation, synthesis, and board builds |
| `results/` | Completed Llama grid, board logs, DDR measurements, and implementation reports |
| `docs/` | Reproduction guide, claim-to-evidence mapping, source provenance, and release procedure |

Model weights, dataset downloads, generated tool projects, and bitstreams are
excluded. Obtain Llama weights separately under their own access terms.

## Run without a board

Use Python 3.10 or newer. The release checks were run with Python 3.14;
the exact environment is recorded in `docs/environment.json`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m kernel.tests.run
python scripts/check_vectors.py
```

The host checks include a C/Python protocol comparison and need a C compiler
(`cc` or `gcc`). No pytest is used. Regenerating the golden vectors needs only
NumPy. Install the `evaluation` extra to exercise the optional Torch adapter
checks as well. To run all twelve RTL benches, install Icarus Verilog and run:

```bash
./scripts/regress.sh
```

The simulation script uses local `iverilog`/`vvp` when available, or the
`ubuntu-work` distrobox on the original development machine.

## Regenerate the paper's payload–perplexity figure

```bash
python -m pip install -e '.[evaluation]'
python scripts/paper_results.py
```

This reads the archived 12-window Llama results, verifies their coverage and
perplexity aggregates, and writes `results/generated/figure1.png`,
`figure1.pdf`, and `frontier.csv`. It does not download a model or rerun inference.

The selected format uses 52 bytes per token per KV head, including scales:
32 bytes of keys, 16 bytes of values, and four bytes of scales. Across eight
KV heads this is 416 bytes per token per layer, versus 2,048 for FP16,
a **79.6875% payload reduction**. DDR allocation padding is additional.

## Reproduce inference and board measurements

See [docs/reproduction.md](docs/reproduction.md) for the model-quality protocol,
Vivado/Vitis 2026.1 build commands, board launch, exactness check, and
perplexity commands. The FPGA computes attention; the host runs the remaining
model operations.

The paper contains two different perplexity experiments. The 12-window software
sweep gives **9.3895 → 11.1043** for the unmodified model and the selected
format. The earlier 4,096-token board run gives **9.074 → 10.640**. They use
different corpus preparation and execution paths, and the board run predates
a change to the host cast boundary. See [docs/evidence.md](docs/evidence.md)
before comparing or citing these numbers.

Exact FPGA/reference agreement is reported for 16,384 layer decoding steps
through context 1,024. It establishes agreement with the same fixed-point
arithmetic. Long-context scan probes measure throughput and do not establish
numerical correctness at context 32,768.

## Citation and license

MIT licensed. `CITATION.cff` and `.zenodo.json` name the paper's three authors.
The Zenodo DOI is assigned when this repository's release is archived;
no DOI has been invented in this source tree. See
[docs/release.md](docs/release.md) for the GitHub–Zenodo sequence.
