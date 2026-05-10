module uart_debug (
    input wire clk,
    input wire rst,
    input wire valid,
    input wire [7:0] data,
    output reg tx
);
    always @(posedge clk) begin
        if (rst) begin
            tx <= 1'b1;
        end else if (valid) begin
            tx <= data[0];
        end
    end
endmodule
