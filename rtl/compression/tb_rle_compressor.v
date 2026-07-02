`timescale 1ns/1ps

// Self-checking testbench: feeds a known telemetry byte stream and compares
// every emitted (value, count) pair against the expected run-length encoding,
// including a mid-stream valid gap that must not break or emit a run. The
// trailing run is intentionally held by the DUT until the next value change.
// Prints exactly one PASS/FAIL summary line.
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

    reg [7:0] exp_value [0:3];
    reg [7:0] exp_count [0:3];

    integer errors = 0;
    integer emitted = 0;

    always @(negedge clk) begin
        if (!rst && valid_out) begin
            if (emitted > 3) begin
                errors = errors + 1;
                $display("FAIL: unexpected extra emission (%h,%0d) at t=%0t", value_out, count_out, $time);
            end else if (value_out !== exp_value[emitted] || count_out !== exp_count[emitted]) begin
                errors = errors + 1;
                $display("FAIL: emission %0d was (%h,%0d), expected (%h,%0d)",
                         emitted, value_out, count_out, exp_value[emitted], exp_count[emitted]);
            end
            emitted = emitted + 1;
        end
    end

    reg [7:0] stream [0:10];
    integer i;

    initial begin
        $dumpfile("rle_compressor.vcd");
        $dumpvars(0, tb_rle_compressor);

        // Input: AA AA AA BB CC CC CC CC DD DD EE
        stream[0] = 8'hAA;
        stream[1] = 8'hAA;
        stream[2] = 8'hAA;
        stream[3] = 8'hBB;
        stream[4] = 8'hCC;
        stream[5] = 8'hCC;
        stream[6] = 8'hCC;
        stream[7] = 8'hCC;
        stream[8] = 8'hDD;
        stream[9] = 8'hDD;
        stream[10] = 8'hEE;

        exp_value[0] = 8'hAA; exp_count[0] = 8'd3;
        exp_value[1] = 8'hBB; exp_count[1] = 8'd1;
        exp_value[2] = 8'hCC; exp_count[2] = 8'd4;
        exp_value[3] = 8'hDD; exp_count[3] = 8'd2;

        repeat (2) @(negedge clk);
        rst = 0;
        for (i = 0; i <= 10; i = i + 1) begin
            @(negedge clk);
            valid_in = 1;
            data_in = stream[i];
            if (i == 6) begin
                @(negedge clk);
                valid_in = 0;
            end
        end
        @(negedge clk);
        valid_in = 0;
        repeat (3) @(negedge clk);

        if (errors == 0 && emitted == 4)
            $display("PASS: tb_rle_compressor, 11 bytes in, 4/4 runs matched (trailing run held, by design)");
        else
            $display("FAIL: tb_rle_compressor, %0d errors, %0d/4 runs emitted", errors, emitted);
        $finish;
    end
endmodule
