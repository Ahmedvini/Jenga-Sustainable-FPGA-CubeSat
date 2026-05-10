`include "fir_coefficients.vh"

module fir_filter (
    input wire clk,
    input wire rst,
    input wire valid_in,
    input wire signed [7:0] sample_in,
    output reg valid_out,
    output reg signed [15:0] sample_out
);
    reg signed [7:0] x0;
    reg signed [7:0] x1;
    reg signed [7:0] x2;
    reg signed [7:0] x3;

    always @(posedge clk) begin
        if (rst) begin
            x0 <= 0;
            x1 <= 0;
            x2 <= 0;
            x3 <= 0;
            sample_out <= 0;
            valid_out <= 0;
        end else begin
            valid_out <= valid_in;
            if (valid_in) begin
                x3 <= x2;
                x2 <= x1;
                x1 <= x0;
                x0 <= sample_in;
                sample_out <= sample_in * `FIR_C0 + x0 * `FIR_C1 + x1 * `FIR_C2 + x2 * `FIR_C3;
            end
        end
    end
endmodule
