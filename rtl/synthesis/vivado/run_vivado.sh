#!/usr/bin/env bash
# Run the Vivado implementation flow for both report targets:
#   - ZCU106 (Zynq UltraScale+ ZU7EV): development/demonstration target
#   - Zynq-7010 (28 nm PL, same fabric class as the Spartan-7/Artix-7
#     flight-part family): low-power flight-class reference
# Reports land in rtl/synthesis_reports/<target>/.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SCRIPT="$REPO_ROOT/rtl/synthesis/vivado/run_vivado_synth.tcl"
VIVADO="${VIVADO:-vivado}"

WORK_DIR="${TMPDIR:-/tmp}/ecosat_vivado"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

"$VIVADO" -mode batch -nolog -nojournal -source "$SCRIPT" \
    -tclargs xczu7ev-ffvc1156-2-e "$REPO_ROOT/rtl/synthesis_reports/zcu106"

"$VIVADO" -mode batch -nolog -nojournal -source "$SCRIPT" \
    -tclargs xc7z010clg400-1 "$REPO_ROOT/rtl/synthesis_reports/zynq7010"

echo "Vivado reports written under $REPO_ROOT/rtl/synthesis_reports/"
