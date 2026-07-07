# Open-source FPGA flow for the Lattice iCEstick (iCE40HX1K-TQ144).
# Tools: yosys, nextpnr-ice40, icepack, icetime (IceStorm), graphviz.
#
#   make            synthesize, place-and-route, bitstream, timing report
#   make stat-core  utilization of fpga_accelerator_top alone (no wrapper)
#   make schematic  top-level schematic SVG via yosys show
#
#   make prog       flash the bitstream to a connected iCEstick (iceprog)
#
# `prog` is not part of `all`, so the flow still runs fully without
# hardware attached.

TOP      := icestick_top
DEVICE   := hx1k
PACKAGE  := tq144
FREQ_MHZ := 12

BUILD    := build
REPORTS  := ../../synthesis_reports/icestick

RTL := ../../fir_filter/fir_filter.v \
       ../../compression/rle_compressor.v \
       ../../can_filter/packet_classifier.v \
       ../../can_filter/can_packet_filter.v \
       ../../top/orbit_controller.v \
       ../../top/scheduler.v \
       ../../top/power_controller.v \
       ../../top/fpga_accelerator_top.v

.PHONY: all timing stat-core schematic prog clean

all: $(BUILD)/$(TOP).bin timing

$(BUILD)/$(TOP).json: synth.ys icestick_top.v ../../common/uart_tx.v $(RTL)
	mkdir -p $(BUILD) $(REPORTS)
	yosys -q -l $(REPORTS)/yosys.log -s synth.ys

$(BUILD)/$(TOP).asc: $(BUILD)/$(TOP).json icestick.pcf
	nextpnr-ice40 --$(DEVICE) --package $(PACKAGE) --freq $(FREQ_MHZ) \
		--json $(BUILD)/$(TOP).json --pcf icestick.pcf --asc $@ \
		--report $(REPORTS)/nextpnr_report.json 2> $(REPORTS)/nextpnr.log \
		|| { tail -20 $(REPORTS)/nextpnr.log; exit 1; }

$(BUILD)/$(TOP).bin: $(BUILD)/$(TOP).asc
	icepack $< $@

timing: $(BUILD)/$(TOP).asc
	icetime -d $(DEVICE) -P $(PACKAGE) -p icestick.pcf -c $(FREQ_MHZ) \
		-t -r $(REPORTS)/icetime_timing.rpt $(BUILD)/$(TOP).asc

stat-core:
	mkdir -p $(REPORTS)
	yosys -q -p "read_verilog -I../../fir_filter -I../../can_filter $(RTL); \
		synth_ice40 -top fpga_accelerator_top; \
		tee -o $(REPORTS)/yosys_stat_core.rpt stat"

schematic:
	mkdir -p $(REPORTS)
	yosys -q -p "read_verilog -I../../fir_filter -I../../can_filter $(RTL); \
		hierarchy -top fpga_accelerator_top; proc; opt_clean; \
		show -format svg -prefix $(REPORTS)/schematic fpga_accelerator_top"

prog: $(BUILD)/$(TOP).bin
	iceprog $(BUILD)/$(TOP).bin

clean:
	rm -rf $(BUILD)
