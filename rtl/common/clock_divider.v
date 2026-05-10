module clock_divider #(
    parameter DIVIDE_BY = 2
) (
    input wire clk,
    input wire rst,
    output reg clk_out
);
    integer count;

    always @(posedge clk) begin
        if (rst) begin
            count <= 0;
            clk_out <= 0;
        end else if (count == (DIVIDE_BY / 2 - 1)) begin
            count <= 0;
            clk_out <= ~clk_out;
        end else begin
            count <= count + 1;
        end
    end
endmodule
