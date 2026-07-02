`timescale 1ns/1ps

// Self-checking testbench: a golden model mirrors the DUT tap pipeline
// (y[n] = x[n] + 2x[n-1] + 2x[n-2] + x[n-3]) and every output sample is
// compared against it, including full-scale positive/negative inputs and a
// mid-stream valid gap. Prints exactly one PASS/FAIL summary line.
module tb_fir_filter;
    reg clk = 0;
    reg rst = 1;
    reg valid_in = 0;
    reg signed [7:0] sample_in = 0;
    wire valid_out;
    wire signed [15:0] sample_out;

    fir_filter dut(clk, rst, valid_in, sample_in, valid_out, sample_out);

    always #5 clk = ~clk;

    reg signed [7:0] h0 = 0;
    reg signed [7:0] h1 = 0;
    reg signed [7:0] h2 = 0;
    reg signed [15:0] expected = 0;
    reg expect_valid = 0;

    always @(posedge clk) begin
        if (rst) begin
            h0 <= 0;
            h1 <= 0;
            h2 <= 0;
            expected <= 0;
            expect_valid <= 0;
        end else begin
            expect_valid <= valid_in;
            if (valid_in) begin
                h2 <= h1;
                h1 <= h0;
                h0 <= sample_in;
                expected <= sample_in + 2 * h0 + 2 * h1 + h2;
            end
        end
    end

    integer errors = 0;
    integer checked = 0;

    always @(negedge clk) begin
        if (!rst) begin
            if (valid_out !== expect_valid) begin
                errors = errors + 1;
                $display("FAIL: valid_out=%b, expected %b at t=%0t", valid_out, expect_valid, $time);
            end else if (valid_out) begin
                checked = checked + 1;
                if (sample_out !== expected) begin
                    errors = errors + 1;
                    $display("FAIL: sample_out=%0d, expected %0d at t=%0t", sample_out, expected, $time);
                end
            end
        end
    end

    reg signed [7:0] stimulus [0:11];
    integer i;

    initial begin
        $dumpfile("fir_filter.vcd");
        $dumpvars(0, tb_fir_filter);

        stimulus[0] = 8'sd1;
        stimulus[1] = 8'sd2;
        stimulus[2] = 8'sd3;
        stimulus[3] = 8'sd4;
        stimulus[4] = -8'sd5;
        stimulus[5] = 8'sd10;
        stimulus[6] = -8'sd128;
        stimulus[7] = 8'sd127;
        stimulus[8] = 8'sd0;
        stimulus[9] = 8'sd8;
        stimulus[10] = -8'sd3;
        stimulus[11] = 8'sd64;

        repeat (2) @(negedge clk);
        rst = 0;
        for (i = 0; i < 12; i = i + 1) begin
            @(negedge clk);
            valid_in = 1;
            sample_in = stimulus[i];
            if (i == 5) begin
                @(negedge clk);
                valid_in = 0;
            end
        end
        @(negedge clk);
        valid_in = 0;
        sample_in = 0;
        repeat (3) @(negedge clk);

        if (errors == 0 && checked == 12)
            $display("PASS: tb_fir_filter, 12/12 output samples matched the golden model");
        else
            $display("FAIL: tb_fir_filter, %0d errors, %0d/12 samples checked", errors, checked);
        $finish;
    end
endmodule
