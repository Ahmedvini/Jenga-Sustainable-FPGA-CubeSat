module fpga_accelerator_top #(
    // Clock cycles per orbit tick; 1 = original full-speed behavior.
    // Board demos raise this so the orbit runs at human-visible speed.
    parameter ORBIT_PRESCALER = 1
) (
    input wire clk,
    input wire rst,
    input wire packet_ready,
    input wire [10:0] can_id,
    input wire [7:0] telemetry_byte,
    input wire signed [7:0] sensor_sample,
    output wire fpga_power_en,
    output wire comms_power_en,
    output wire filter_valid,
    output wire compression_valid,
    output wire fir_valid,
    output wire [63:0] filtered_payload,
    output wire [7:0] rle_value,
    output wire [7:0] rle_count,
    output wire signed [15:0] fir_sample
);
    wire sunlight;
    wire run_compression;
    wire run_filter;
    wire workload_pending;

    assign workload_pending = run_compression || run_filter || packet_ready;

    orbit_controller #(.PRESCALER(ORBIT_PRESCALER)) orbit_i(
        .clk(clk),
        .rst(rst),
        .sunlight(sunlight)
    );
    scheduler scheduler_i(
        .clk(clk),
        .rst(rst),
        .sunlight(sunlight),
        .packet_ready(packet_ready),
        .run_compression(run_compression),
        .run_filter(run_filter)
    );
    power_controller power_i(
        .clk(clk),
        .rst(rst),
        .sunlight(sunlight),
        .workload_pending(workload_pending),
        .fpga_power_en(fpga_power_en),
        .comms_power_en(comms_power_en)
    );
    can_packet_filter can_i(
        .clk(clk),
        .rst(rst),
        .valid_in(run_filter),
        .can_id(can_id),
        .payload_in({56'b0, telemetry_byte}),
        .valid_out(filter_valid),
        .payload_out(filtered_payload)
    );
    rle_compressor rle_i(
        .clk(clk),
        .rst(rst),
        .valid_in(run_compression),
        .data_in(telemetry_byte),
        .valid_out(compression_valid),
        .value_out(rle_value),
        .count_out(rle_count)
    );
    fir_filter fir_i(
        .clk(clk),
        .rst(rst),
        .valid_in(packet_ready),
        .sample_in(sensor_sample),
        .valid_out(fir_valid),
        .sample_out(fir_sample)
    );
endmodule
