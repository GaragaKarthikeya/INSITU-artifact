#!/usr/bin/env bash
# Run every self-checking testbench in kernel/tb.
#
# Icarus lives in the ubuntu-work distrobox, not on the RHEL host. Vivado and
# Vitis are the other way round -- host only. Set KERNEL_NO_DISTROBOX=1 if you
# are already inside the container.
#
#   ./scripts/regress.sh            # all benches
#   ./scripts/regress.sh ddr        # only benches whose name contains "ddr"
set -uo pipefail
WORK=$(mktemp -d "${TMPDIR:-/tmp}/insitu-rtl.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
cd "$(dirname "$0")/.."
FILTER="${1:-}"

run() {   # run <name> <extra sources...>
    local name=$1; shift
    local vvp="$WORK/${name}.vvp"
    local cmd="iverilog -g2012 -o ${vvp} -s ${name} tb/${name}.sv $* && vvp ${vvp}"
    if command -v iverilog >/dev/null && command -v vvp >/dev/null; then
        bash -lc "$cmd"
    elif [ "${KERNEL_NO_DISTROBOX:-0}" != "1" ] && command -v distrobox >/dev/null; then
        distrobox enter "${INSITU_DISTROBOX:-ubuntu-work}" -- bash -lc "cd '$(pwd)' && $cmd"
    else
        echo "Install Icarus Verilog (iverilog and vvp)." >&2
        return 127
    fi
}

declare -a NAMES=(tb_ddr_probe tb_rot tb_rot_norm tb_rot_encode tb_qtab_build tb_score_lane tb_exp_lut tb_softmax_accum tb_finalize tb_kv_store tb_attn tb_attn_ctrl)
declare -a SRCS=("rtl/ddr_probe.sv rtl/axi_rd_engine.sv" "rtl/rot_fwht.sv" \
                 "rtl/rot_norm.sv" "rtl/rot_encode.sv" "rtl/qtab_build.sv" \
                 "rtl/score_lane.sv rtl/qtab_build.sv" "rtl/exp_lut.sv" \
                 "rtl/softmax_online.sv rtl/accum.sv rtl/exp_lut.sv" "rtl/finalize.sv" \
                 "rtl/kv_store_ddr.sv rtl/kv_plane_rd.sv rtl/kv_write.sv" \
                 "rtl/attn_top.sv rtl/attn_ingress.sv rtl/rot_fwht.sv rtl/rot_norm.sv rtl/rot_encode.sv rtl/score_lane.sv rtl/qtab_build.sv rtl/softmax_online.sv rtl/exp_lut.sv rtl/accum.sv rtl/finalize.sv rtl/kv_store_ddr.sv rtl/kv_plane_rd.sv rtl/kv_write.sv" \
                 "rtl/attn_ctrl.sv rtl/attn_top.sv rtl/attn_ingress.sv rtl/rot_fwht.sv rtl/rot_norm.sv rtl/rot_encode.sv rtl/score_lane.sv rtl/qtab_build.sv rtl/softmax_online.sv rtl/exp_lut.sv rtl/accum.sv rtl/finalize.sv rtl/kv_store_ddr.sv rtl/kv_plane_rd.sv rtl/kv_write.sv")

fail=0
ran=0
for i in "${!NAMES[@]}"; do
    name="${NAMES[$i]}"
    [ -n "$FILTER" ] && [[ "$name" != *"$FILTER"* ]] && continue
    ran=$((ran + 1))
    echo "--- $name"
    rc=0
    out=$(run "$name" ${SRCS[$i]} 2>&1) || rc=$?
    echo "$out" | sed 's/^/    /'
    # A bench that compiles but never reaches its verdict is a failure, so the
    # PASS banner must be present -- absence of "FAIL" is not enough.
    if [ "$rc" -ne 0 ] || ! echo "$out" | grep -q "ALL TESTS PASSED"; then
        echo "    ^^ $name FAILED"
        fail=1
    fi
done

if [ "$ran" -eq 0 ]; then echo "No bench matched: $FILTER" >&2; exit 2; fi
if [ $fail -eq 0 ]; then echo "=== regress: all benches passed"; else echo "=== regress: FAILURES"; fi
exit $fail
