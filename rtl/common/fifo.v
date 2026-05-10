module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
) (
    input wire clk,
    input wire rst,
    input wire wr_en,
    input wire rd_en,
    input wire [WIDTH-1:0] din,
    output reg [WIDTH-1:0] dout,
    output wire empty,
    output wire full
);
    localparam ADDR_W = 4;
    reg [WIDTH-1:0] mem [0:DEPTH-1];
    reg [ADDR_W:0] wr_ptr;
    reg [ADDR_W:0] rd_ptr;

    assign empty = (wr_ptr == rd_ptr);
    assign full = ((wr_ptr[ADDR_W] != rd_ptr[ADDR_W]) && (wr_ptr[ADDR_W-1:0] == rd_ptr[ADDR_W-1:0]));

    always @(posedge clk) begin
        if (rst) begin
            wr_ptr <= 0;
            rd_ptr <= 0;
            dout <= 0;
        end else begin
            if (wr_en && !full) begin
                mem[wr_ptr[ADDR_W-1:0]] <= din;
                wr_ptr <= wr_ptr + 1'b1;
            end
            if (rd_en && !empty) begin
                dout <= mem[rd_ptr[ADDR_W-1:0]];
                rd_ptr <= rd_ptr + 1'b1;
            end
        end
    end
endmodule
