# Create a Vivado GUI project for the EcoSat FPGA accelerator (ZCU106 part).
#
# From a terminal:
#   vivado -mode batch -source rtl/synthesis/vivado/create_project.tcl
# or from the Vivado GUI Tcl console (cd to the repo root first):
#   source rtl/synthesis/vivado/create_project.tcl
#
# Then open vivado_project/ecosat_accelerator.xpr in the GUI. Synthesis runs
# out-of-context (no pins), so Run Synthesis / Run Implementation work
# directly and the three self-checking testbenches are preconfigured as
# simulation sources for the xsim GUI.

set rtl_root [file normalize [file join [file dirname [info script]] .. ..]]
set repo_root [file normalize [file join $rtl_root ..]]
set proj_dir $repo_root/vivado_project

create_project -force ecosat_accelerator $proj_dir -part xczu7ev-ffvc1156-2-e

add_files [list \
    $rtl_root/fir_filter/fir_filter.v \
    $rtl_root/compression/rle_compressor.v \
    $rtl_root/can_filter/packet_classifier.v \
    $rtl_root/can_filter/can_packet_filter.v \
    $rtl_root/top/orbit_controller.v \
    $rtl_root/top/scheduler.v \
    $rtl_root/top/power_controller.v \
    $rtl_root/top/fpga_accelerator_top.v \
]
add_files -fileset constrs_1 $rtl_root/synthesis/vivado/constraints_ooc.xdc

add_files -fileset sim_1 [list \
    $rtl_root/fir_filter/tb_fir_filter.v \
    $rtl_root/compression/tb_rle_compressor.v \
    $rtl_root/can_filter/tb_can_filter.v \
]

set include_dirs [list $rtl_root/fir_filter $rtl_root/can_filter]
set_property include_dirs $include_dirs [current_fileset]
set_property include_dirs $include_dirs [get_filesets sim_1]

set_property top fpga_accelerator_top [current_fileset]
# Default simulation top; switch to tb_rle_compressor / tb_can_filter in the
# GUI (Simulation Sources -> right click -> Set as Top) to run the others.
set_property top tb_fir_filter [get_filesets sim_1]

set_property -name {STEPS.SYNTH_DESIGN.ARGS.MORE OPTIONS} \
    -value {-mode out_of_context} -objects [get_runs synth_1]

puts "Project created: $proj_dir/ecosat_accelerator.xpr"
