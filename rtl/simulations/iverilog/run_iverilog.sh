#!/usr/bin/env bash
set -euo pipefail

iverilog -I rtl/fir_filter -o /tmp/tb_fir rtl/fir_filter/fir_filter.v rtl/fir_filter/tb_fir_filter.v
vvp /tmp/tb_fir

iverilog -I rtl/compression -I rtl/common -o /tmp/tb_rle rtl/compression/rle_compressor.v rtl/compression/tb_rle_compressor.v
vvp /tmp/tb_rle

iverilog -I rtl/can_filter -o /tmp/tb_can rtl/can_filter/packet_classifier.v rtl/can_filter/can_packet_filter.v rtl/can_filter/tb_can_filter.v
vvp /tmp/tb_can
