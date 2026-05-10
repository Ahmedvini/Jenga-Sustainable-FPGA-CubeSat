module rle_compressor (
    input wire clk,
    input wire rst,
    input wire valid_in,
    input wire [7:0] data_in,
    output reg valid_out,
    output reg [7:0] value_out,
    output reg [7:0] count_out
);
    reg [7:0] current;
    reg [7:0] count;
    reg initialized;

    always @(posedge clk) begin
        if (rst) begin
            current <= 0;
            count <= 0;
            initialized <= 0;
            valid_out <= 0;
            value_out <= 0;
            count_out <= 0;
        end else begin
            valid_out <= 0;
            if (valid_in) begin
                if (!initialized) begin
                    current <= data_in;
                    count <= 1;
                    initialized <= 1;
                end else if (data_in == current && count != 8'hFF) begin
                    count <= count + 1'b1;
                end else begin
                    value_out <= current;
                    count_out <= count;
                    valid_out <= 1;
                    current <= data_in;
                    count <= 1;
                end
            end
        end
    end
endmodule
