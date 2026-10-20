INSITU v1.0.0 packages the FPGA attention engine and its matching fixed-point
reference for “INSITU: Reconstruction-Free Attention over a Compressed KV Cache
on FPGA.”

The release includes the four-bit-key/two-bit-value RTL, A53 firmware and host
clients, twelve RTL testbenches and golden vectors, the completed 12-window
Llama-3.2-1B bit-width sweep, original board logs, and implementation reports.
Model weights and generated vendor projects are excluded. Code is MIT licensed.

Reproduction commands, recorded validation, and measurement limitations are in
`docs/`. The archived 4,096-token board perplexity result predates a change to
the host cast boundary; it has not been remeasured with the current host path.
