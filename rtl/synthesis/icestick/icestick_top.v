// Evaluation wrapper for the Lattice iCEstick (iCE40HX1K-TQ144).
//
// fpga_accelerator_top exposes 132 bits of ports, more I/O than the HX1K
// package provides, so this wrapper keeps the full core on-chip: a 32-bit
// LFSR drives the inputs with pseudo-random stimulus and every output cone
// is XOR-folded onto the five iCEstick LEDs. Nothing in the core can be
// optimized away, so utilization and timing reflect the real design.
// No external peripherals are used; this build only evaluates fit/timing.
module icestick_top (
    input  wire clk,       // 12 MHz on-board oscillator (pin 21)
    output wire [4:0] led  // D1..D5
);
    // Power-on reset: hold rst high for the first 8 clocks
    reg [3:0] por = 4'd0;
    wire rst = ~por[3];
    always @(posedge clk) begin
        if (!por[3])
            por <= por + 4'd1;
    end

    // Pseudo-random stimulus generator
    reg [31:0] lfsr = 32'h1;
    always @(posedge clk)
        lfsr <= {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};

    wire fpga_power_en;
    wire comms_power_en;
    wire filter_valid;
    wire compression_valid;
    wire fir_valid;
    wire [63:0] filtered_payload;
    wire [7:0] rle_value;
    wire [7:0] rle_count;
    wire signed [15:0] fir_sample;

    fpga_accelerator_top core_i (
        .clk(clk),
        .rst(rst),
        .packet_ready(lfsr[27]),
        .can_id(lfsr[10:0]),
        .telemetry_byte(lfsr[18:11]),
        .sensor_sample(lfsr[26:19]),
        .fpga_power_en(fpga_power_en),
        .comms_power_en(comms_power_en),
        .filter_valid(filter_valid),
        .compression_valid(compression_valid),
        .fir_valid(fir_valid),
        .filtered_payload(filtered_payload),
        .rle_value(rle_value),
        .rle_count(rle_count),
        .fir_sample(fir_sample)
    );

    assign led[0] = fpga_power_en;
    assign led[1] = comms_power_en;
    assign led[2] = filter_valid ^ compression_valid ^ fir_valid;
    assign led[3] = ^filtered_payload ^ ^fir_sample;
    assign led[4] = ^rle_value ^ ^rle_count;
endmodule
