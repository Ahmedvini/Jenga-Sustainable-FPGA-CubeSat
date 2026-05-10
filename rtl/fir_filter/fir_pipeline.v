module fir_pipeline (
    input wire clk,
    input wire rst,
    input wire valid_in,
    input wire signed [7:0] sample_in,
    output wire valid_out,
    output wire signed [15:0] sample_out
);
    fir_filter filter_i (
        .clk(clk),
        .rst(rst),
        .valid_in(valid_in),
        .sample_in(sample_in),
        .valid_out(valid_out),
        .sample_out(sample_out)
    );
endmodule
