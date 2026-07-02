# Non-project Vivado flow: synthesize, implement, and report the
# fpga_accelerator_top design out-of-context for a given part.
#
# Batch usage:
#   vivado -mode batch -source run_vivado_synth.tcl -tclargs <part> <report_dir>
#
# GUI Tcl-console usage (defaults to the ZCU106 target):
#   source rtl/synthesis/vivado/run_vivado_synth.tcl
# or pick another target first:
#   set argv {xc7z010clg400-1 rtl/synthesis_reports/zynq7010}; set argc 2
#   source rtl/synthesis/vivado/run_vivado_synth.tcl
# After it finishes, the routed design stays open, so Reports/Schematic/
# Device views in the GUI all work on the result.
#
# Report targets:
#   xczu7ev-ffvc1156-2-e   ZCU106 evaluation board (Zynq UltraScale+ ZU7EV)
#   xc7z010clg400-1        28 nm Zynq-7000; its PL is the same fabric class
#                          as the Spartan-7/Artix-7 flight-part family

if {$argc >= 2} {
    set part [lindex $argv 0]
    set report_dir [file normalize [lindex $argv 1]]
} else {
    set part xczu7ev-ffvc1156-2-e
    set report_dir [file normalize [file join [file dirname [info script]] .. .. synthesis_reports zcu106]]
    puts "No -tclargs given; defaulting to part=$part, reports=$report_dir"
}
file mkdir $report_dir

set rtl_root [file normalize [file join [file dirname [info script]] .. ..]]

read_verilog [list \
    $rtl_root/fir_filter/fir_filter.v \
    $rtl_root/compression/rle_compressor.v \
    $rtl_root/can_filter/packet_classifier.v \
    $rtl_root/can_filter/can_packet_filter.v \
    $rtl_root/top/orbit_controller.v \
    $rtl_root/top/scheduler.v \
    $rtl_root/top/power_controller.v \
    $rtl_root/top/fpga_accelerator_top.v \
]

synth_design \
    -top fpga_accelerator_top \
    -part $part \
    -mode out_of_context \
    -include_dirs [list $rtl_root/fir_filter $rtl_root/can_filter]

# 100 MHz reference clock for timing-driven implementation
create_clock -period 10.000 -name clk [get_ports clk]

opt_design
place_design
route_design

report_utilization -file $report_dir/utilization.rpt
report_timing_summary -file $report_dir/timing_summary.rpt
report_power -file $report_dir/power.rpt

set wns [get_property SLACK [get_timing_paths -max_paths 1 -nworst 1 -setup]]
puts "RESULT part=$part wns_ns=$wns reports=$report_dir"
