# Release validation

Checked on 2026-10-21. The captured package versions are in `environment.json`.
All commands were run from the extracted repository, independently of the
development package's import path.

| Check | Result |
|---|---|
| `python -m kernel.tests.run` | **178 passed, 0 failed**; includes the localhost protocol test and C header compilation |
| `python scripts/check_vectors.py` | **67 golden files** regenerate byte-for-byte |
| `scripts/regress.sh` using Icarus in `ubuntu-work` | **All 12 benches passed**, using the refreshed vectors |
| `python scripts/paper_results.py` | Validated 51 configurations and 12 windows each; regenerated Figure 1 and its frontier CSV |
| Wheel build with `pip wheel --no-deps --no-build-isolation` | Built `insitu_attention-1.0.0-py3-none-any.whl` |
| Install wheel to a temporary directory, import from outside the source tree | Imported the packaged `kernel` and constructed the 4b/2b configuration successfully |
| Compile all Python sources and check modified shell entrypoints with `bash -n` | Passed |
| Compare core source hashes to the development checkout | Arithmetic, RTL, firmware, and original measurements unchanged |

Detailed host and RTL logs are in `results/release-host-tests.log` and
`results/release-rtl-tests.log`. The result-validation output is
`results/release-paper-results.log`.

The first sandboxed protocol run could not open a localhost socket; the final
178-check run was executed with socket access. RTL simulations ran in the
existing development container because Icarus is installed there.

## Corrections made during extraction

The source-search test originally pointed outside the development checkout and
therefore did not inspect its intended files. The relocated test now searches
the actual `kernel/` package. This exposed a legacy demo using a direct
`Rotation.from_seed` call; that unrelated demo was excluded.

Forty-five committed golden files differed from regeneration under the current
reference. The release refreshes those vectors and passes the full RTL suite
against them. The original vector hashes remain in `source-manifest.json`.
No numerical implementation changes were needed.

The extraction also replaces personal absolute paths with configurable
entrypoints and adjusts test/header/tool paths for the new package layout.
The numerical model, RTL, firmware, and archived result files retain their
original bytes.

No physical-board run, synthesis rebuild, or Llama corpus rerun was performed
during curation. The historical limits in `evidence.md` still apply.
