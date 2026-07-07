// Minimal 8N1 UART transmitter (LSB first, one stop bit).
// DIVIDER = clock cycles per bit; 12 MHz / 115200 baud -> 104.
module uart_tx #(
    parameter DIVIDER = 104
) (
    input  wire clk,
    input  wire rst,
    input  wire valid,       // pulse: send `data` (ignored while busy)
    input  wire [7:0] data,
    output reg  tx,
    output wire busy
);
    reg active = 1'b0;
    reg [9:0] shifter = 10'h3FF;
    reg [3:0] bits_left = 4'd0;
    reg [$clog2(DIVIDER)-1:0] baud_cnt = 0;

    assign busy = active;

    always @(posedge clk) begin
        if (rst) begin
            tx <= 1'b1;
            active <= 1'b0;
            bits_left <= 4'd0;
            baud_cnt <= 0;
        end else if (!active) begin
            tx <= 1'b1;
            if (valid) begin
                shifter <= {1'b1, data, 1'b0};  // stop, data (LSB first), start
                bits_left <= 4'd10;
                baud_cnt <= DIVIDER - 1;        // emit the start bit next cycle
                active <= 1'b1;
            end
        end else if (baud_cnt == DIVIDER - 1) begin
            baud_cnt <= 0;
            if (bits_left == 4'd0)
                active <= 1'b0;                 // stop bit has completed
            else begin
                tx <= shifter[0];
                shifter <= {1'b1, shifter[9:1]};
                bits_left <= bits_left - 4'd1;
            end
        end else begin
            baud_cnt <= baud_cnt + 1'b1;
        end
    end
endmodule
