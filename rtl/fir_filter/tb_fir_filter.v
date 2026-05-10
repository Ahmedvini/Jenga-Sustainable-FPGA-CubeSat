`timescale 1ns/1ps

module tb_fir_filter;
    reg clk = 0;
    reg rst = 1;
    reg valid_in = 0;
    reg signed [7:0] sample_in = 0;
    wire valid_out;
    wire signed [15:0] sample_out;

    fir_filter dut(clk, rst, valid_in, sample_in, valid_out, sample_out);

    always #5 clk = ~clk;

    initial begin
        $dumpfile("fir_filter.vcd");
        $dumpvars(0, tb_fir_filter);
        #20 rst = 0;
        repeat (8) begin
            @(posedge clk);
            valid_in = 1;
            sample_in = sample_in + 1;
        end
        @(posedge clk);
        valid_in = 0;
        #40 $finish;
    end
endmodule
