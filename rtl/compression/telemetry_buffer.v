module telemetry_buffer (
    input wire clk,
    input wire rst,
    input wire wr_en,
    input wire rd_en,
    input wire [15:0] din,
    output wire [15:0] dout,
    output wire empty,
    output wire full
);
    fifo #(.WIDTH(16), .DEPTH(16)) fifo_i (
        .clk(clk),
        .rst(rst),
        .wr_en(wr_en),
        .rd_en(rd_en),
        .din(din),
        .dout(dout),
        .empty(empty),
        .full(full)
    );
endmodule
