`timescale 1ns/1ps

module tb_can_filter;
    reg clk = 0;
    reg rst = 1;
    reg valid_in = 0;
    reg [10:0] can_id = 0;
    reg [63:0] payload_in = 0;
    wire valid_out;
    wire [63:0] payload_out;

    can_packet_filter dut(clk, rst, valid_in, can_id, payload_in, valid_out, payload_out);

    always #5 clk = ~clk;

    initial begin
        $dumpfile("can_filter.vcd");
        $dumpvars(0, tb_can_filter);
        #20 rst = 0;
        send(11'h100, 64'hAA);
        send(11'h555, 64'hBB);
        send(11'h200, 64'hCC);
        #40 $finish;
    end

    task send(input [10:0] id, input [63:0] payload);
        begin
            @(posedge clk);
            valid_in = 1;
            can_id = id;
            payload_in = payload;
        end
    endtask
endmodule
