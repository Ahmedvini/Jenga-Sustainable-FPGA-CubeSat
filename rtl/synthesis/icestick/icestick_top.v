// Deployment wrapper for the Lattice iCEstick (iCE40HX1K-TQ144).
//
// The core runs at the full 12 MHz clock, but the orbit controller is
// prescaled so one simulated 95-tick orbit takes about 10 seconds — slow
// enough to watch on the LEDs:
//
//   D5 (green) sunlight: on ~6 s (sunlight), off ~4 s (eclipse)
//   D1         fpga_power_en  (burst rail: active only in sunlight w/ work)
//   D2         comms_power_en (comms rail: shuts off in eclipse)
//   D3         processing activity (filter/compression/FIR valids, pulse-
//              stretched to visible flashes)
//   D4         datapath activity (XOR fold of payload/sample outputs)
//
// A 32-bit LFSR supplies pseudo-random CAN/telemetry/sensor stimulus, so
// every core input is driven and every output cone is observed — nothing
// can be optimized away, and utilization/timing reflect the real design.
module icestick_top (
    input  wire clk,       // 12 MHz on-board oscillator (pin 21)
    output wire [4:0] led  // D1..D5
);
    // One orbit = 95 ticks; 12 MHz / 1_250_000 ~= 9.6 Hz tick rate
    // -> orbit ~9.9 s, sunlight ~5.9 s, eclipse ~4.0 s.
    localparam ORBIT_PRESCALER = 1_250_000;

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

    // Packets arrive in visible bursts: ~0.35 s of traffic every ~1.4 s,
    // so the activity LEDs flash instead of sitting solid-on.
    reg [23:0] burst_cnt = 0;
    always @(posedge clk)
        burst_cnt <= burst_cnt + 1;
    wire burst_window = (burst_cnt[23:22] == 2'b00);
    wire packet_ready = lfsr[27] && burst_window;

    wire sunlight_demo;
    wire fpga_power_en;
    wire comms_power_en;
    wire filter_valid;
    wire compression_valid;
    wire fir_valid;
    wire [63:0] filtered_payload;
    wire [7:0] rle_value;
    wire [7:0] rle_count;
    wire signed [15:0] fir_sample;

    // Demo-rate orbit state drives the scheduler/power controller via the
    // core; a mirrored instance here exposes sunlight for the green LED.
    fpga_accelerator_top #(
        .ORBIT_PRESCALER(ORBIT_PRESCALER)
    ) core_i (
        .clk(clk),
        .rst(rst),
        .packet_ready(packet_ready),
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

    assign sunlight_demo = comms_power_en;  // comms rail tracks sunlight

    // Pulse-stretchers: turn microsecond valid blips into ~175 ms flashes
    reg [20:0] proc_stretch = 0;
    always @(posedge clk) begin
        if (filter_valid || compression_valid || fir_valid)
            proc_stretch <= {21{1'b1}};
        else if (proc_stretch != 0)
            proc_stretch <= proc_stretch - 1;
    end

    // Datapath LED triggers on output changes, not levels, so it decays
    // dark between packet bursts.
    wire data_fold = ^filtered_payload ^ ^fir_sample ^ ^rle_value ^ ^rle_count;
    reg data_fold_prev = 0;
    reg [20:0] data_stretch = 0;
    always @(posedge clk) begin
        data_fold_prev <= data_fold;
        if (data_fold != data_fold_prev)
            data_stretch <= {21{1'b1}};
        else if (data_stretch != 0)
            data_stretch <= data_stretch - 1;
    end

    assign led[0] = fpga_power_en;         // D1: FPGA burst rail
    assign led[1] = comms_power_en;        // D2: comms rail (off in eclipse)
    assign led[2] = (proc_stretch != 0);   // D3: processing activity
    assign led[3] = (data_stretch != 0);   // D4: datapath activity
    assign led[4] = sunlight_demo;         // D5 green: sunlight/eclipse
endmodule
