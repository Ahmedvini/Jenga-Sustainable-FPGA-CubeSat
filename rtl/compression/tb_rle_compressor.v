`timescale 1ns/1ps

module tb_rle_compressor;
    reg clk = 0;
    reg rst = 1;
    reg valid_in = 0;
    reg [7:0] data_in = 0;
    wire valid_out;
    wire [7:0] value_out;
    wire [7:0] count_out;

    rle_compressor dut(clk, rst, valid_in, data_in, valid_out, value_out, count_out);

    always #5 clk = ~clk;

    initial begin
        $dumpfile("rle_compressor.vcd");
        $dumpvars(0, tb_rle_compressor);
        #20 rst = 0;
        send(8'h11);
        send(8'h11);
        send(8'h22);
        send(8'h22);
        send(8'h33);
        #50 $finish;
    end

    task send(input [7:0] value);
        begin
            @(posedge clk);
            valid_in = 1;
            data_in = value;
        end
    endtask
endmodule
