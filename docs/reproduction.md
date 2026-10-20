# Reproduction

Run commands from the INSITU repository root. The Python package is named
`kernel` even when the checkout directory is named `INSITU`. Core arithmetic,
RTL, and firmware were copied from the development repository without
numerical changes. `source-manifest.json` records every selected source file
and its original SHA-256 hash. Golden vectors were refreshed from the current
reference; they are checked again byte-for-byte by `scripts/check_vectors.py`.

## Software environment

The NumPy reference needs Python >=3.10 and NumPy. Model evaluation additionally
needs PyTorch, Transformers, and Datasets; plots need Matplotlib. The environment
captured during curation is in `environment.json`. These are the versions
available for the release checks, not a recovered lockfile of the historical
board experiments. A C compiler is needed by the protocol checks.

```bash
python -m pip install -e '.[evaluation]'
python -m kernel.tests.run
python scripts/check_vectors.py
./scripts/regress.sh
```

The tests use the project's `check_*` runner. The adapter checks build a small
random model and do not require the Llama checkpoint. Icarus Verilog is needed
for simulation. Set `INSITU_DISTROBOX=ubuntu-work` to use that container, or
`KERNEL_NO_DISTROBOX=1` to require local simulation tools.

## Archived software result and Figure 1

```bash
python scripts/paper_results.py
```

The input is `results/llama32-grid/results.json`: baseline plus 25 key/value
configurations on each of two arithmetic paths. Path A reconstructs and
unrotates cached keys; path B scores the codes in the rotated representation.
The figure uses path B. It selects the lowest-perplexity split at each payload
budget and plots the nondominated points against the unmodified baseline.
The script checks all 51 entries, 12 windows each, and the relation
`ppl = exp(nll / tokens)`, before plotting.

To rerun the full software sweep, obtain access to `meta-llama/Llama-3.2-1B`
and log in to Hugging Face separately if required. Supply the model identifier
or a local checkpoint directory:

```bash
python -m kernel.experiments.wikitext_ppl \
  --model meta-llama/Llama-3.2-1B --context 2048 --windows 12 \
  --configs baseline,k2v2-B,k2v3-B,k2v4-B,k2v5-B,k2v6-B,k3v2-B,k3v3-B,k3v4-B,k3v5-B,k3v6-B,k4v2-B,k4v3-B,k4v4-B,k4v5-B,k4v6-B,k5v2-B,k5v3-B,k5v4-B,k5v5-B,k5v6-B,k6v2-B,k6v3-B,k6v4-B,k6v5-B,k6v6-B \
  --dtype float32 --device cpu --need-gb 8 \
  --dir results/rerun-llama32
```

This command reruns the baseline and all B configurations used to select the
frontier. To repeat A as well, add the corresponding `kNvM-A` names to
`--configs`. Use `--device cuda` if suitable GPU memory is available. The
archived run joined WikiText-2 test rows with blank lines, tokenized the stream,
and evaluated its first twelve non-overlapping 2,048-token windows with the
cache reset between windows. Each configuration scores 24,564 next tokens.
`--skip-layers` and `--fold-k-bias` remain empty for the paper's Llama run.

Pass a separate output path when changing the corpus or configuration; the
runner supports resuming a partially finished experiment. Rerun results may
depend on the checkpoint, tokenizer, dependency versions, and arithmetic path.
The original checkpoint revision and complete historical package lockfile
were not recorded.

## Build the ZCU104 system

Required tools: AMD Vivado and Vitis **2026.1**, the ZCU104 board files
(`xilinx.com:zcu104:part0:1.1`), and the target `xczu7ev-ffvc1156-2-e`.
The Vitis script uses its Python API and the `lwip220` standalone library.
Source the tools' settings scripts before these commands.

```bash
python -m kernel.hw.board_vectors --out sw
vivado -mode batch -source scripts/create_bd_attn_dma.tcl -tclargs 250
vivado -mode batch -source scripts/build_attn_bit.tcl -tclargs 8 250 attndma
INSITU_PYTHON="$(command -v python)" vitis -s scripts/build_vitis_attn.py
xsdb host/run_attn_server.tcl
```

Synthetic firmware vectors are reproducible from seed 0 and are generated
locally. To build firmware with real activation cases, run
`python -m kernel.hw.real_vectors --model /path/to/Llama-3.2-1B --out sw`
before the Vitis step. `--prompt` uses the included prompt instead of WikiText-2.
The real-vector helper can fall back to that prompt if the dataset is unavailable;
check its output before treating a run as a corpus experiment.

Vivado produces `build/attndma_f250.bit` and `.xsa`; Vitis produces the ELF.
The launch script locates the generated bitstream, PS initialization script,
and ELF in the Vitis workspace. The source artifact does not ship these vendor
products. A new place-and-route and physical-board run were not performed as
part of repository curation.

## Board inference and exactness

Connect the ZCU104's JTAG/UART and Ethernet interfaces. Firmware defaults to
`192.168.10.2`; configure the host's connected interface on that subnet and
keep its MTU at 1500 so IP fragmentation matches lwIP. UART defaults to
`/dev/ttyUSB1`. The UDP client does not need root. The optional raw Ethernet
diagnostic requires raw-socket privileges.

```bash
python -m kernel.experiments.fpga_infer \
  --model /path/to/Llama-3.2-1B --udp 192.168.10.2 --tokens 8 --trace
python -m kernel.experiments.fpga_ppl \
  --model /path/to/Llama-3.2-1B --udp 192.168.10.2 --tokens 1024
python -m kernel.experiments.fpga_ppl \
  --model /path/to/Llama-3.2-1B --udp 192.168.10.2 --tokens 4096 --no-verify
```

The 1,024-token command checks all 16 layers against the matching online
fixed-point reference, giving 16,384 layer steps. `--no-verify` skips this
comparison for the longer perplexity run; model outputs still come from the
FPGA. The current board runner is supplied for rerunning the experiment;
the historical board result predates the cast-boundary change described in
`evidence.md`.

`scripts/attn` wraps these runners and supports `INSITU_PYTHON`, `BOARD_IP`,
`UART`, `IFACE`, and optional `VITIS_SETTINGS`. It checks board liveness but
does not program hardware automatically: run the XSDB launcher explicitly
after each firmware build. `scripts/bringup_eth.sh` is an explicit
program-and-capture helper. The raw Ethernet implementation remains because
the firmware build includes it; UDP/lwIP is the demonstrated working transport.

## Numerical and measurement limits

- Batch size is one and custom attention masks are unsupported.
- The implemented RTL fixes 64 components, four query lanes per KV head,
  four-bit keys, two-bit values, and the matching seed-specific rotation.
- `QuantConfig()` defaults to three key bits. Pass `key_bits=4, value_bits=2`
  when constructing a paper configuration; board helpers specify these widths.
- Online and two-pass fixed-point softmax need not be bit-identical. Hardware
  goldens use the online form.
- Changing the rotation seed requires matching folded projection weights.
- The analytical cycle model in `kernel/hw/` is separate from physical-board
  timing. Consult the original logs for measured latencies.
- The 32k-context PRNG scan probe checks memory performance, not LLM outputs.
