#!/usr/bin/env bash
# Compile and run all RTL testbenches with Icarus Verilog. Each testbench is
# self-checking and prints exactly one "PASS: <name>" summary line; this
# script exits nonzero unless every testbench reports PASS.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$REPO_ROOT"

BUILD_DIR="${TMPDIR:-/tmp}/ecosat_rtl_build"
mkdir -p "$BUILD_DIR"

status=0

run_tb() {
    local name="$1"
    shift
    echo "== $name =="
    iverilog -o "$BUILD_DIR/$name" "$@"
    local output
    if ! output="$(cd "$BUILD_DIR" && vvp "./$name" 2>&1)"; then
        echo "$output"
        echo "ERROR: vvp execution failed for $name"
        status=1
        return 0
    fi
    echo "$output"
    if ! grep -q "^PASS: $name" <<< "$output"; then
        echo "ERROR: $name did not report PASS"
        status=1
    fi
}

run_tb tb_fir_filter -I rtl/fir_filter rtl/fir_filter/fir_filter.v rtl/fir_filter/tb_fir_filter.v
run_tb tb_rle_compressor -I rtl/compression -I rtl/common rtl/compression/rle_compressor.v rtl/compression/tb_rle_compressor.v
run_tb tb_can_filter -I rtl/can_filter rtl/can_filter/packet_classifier.v rtl/can_filter/can_packet_filter.v rtl/can_filter/tb_can_filter.v

if [ "$status" -eq 0 ]; then
    echo "All RTL testbenches PASSED. Waveforms (VCD) in $BUILD_DIR"
else
    echo "One or more RTL testbenches FAILED"
fi
exit "$status"
