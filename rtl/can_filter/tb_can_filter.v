`timescale 1ns/1ps

// Self-checking testbench: drives a mix of whitelisted and blocked CAN IDs
// and verifies the filter forwards exactly the allowed payloads, in order,
// and asserts valid_out for nothing else. Whitelist (filter_rules.vh):
// 0x100, 0x101, 0x200. Prints exactly one PASS/FAIL summary line.
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

    function model_allowed(input [10:0] id);
        model_allowed = (id == 11'h100) || (id == 11'h101) || (id == 11'h200);
    endfunction

    reg expect_valid = 0;
    reg [63:0] expect_payload = 0;

    always @(posedge clk) begin
        if (rst) begin
            expect_valid <= 0;
            expect_payload <= 0;
        end else begin
            expect_valid <= valid_in && model_allowed(can_id);
            if (valid_in && model_allowed(can_id))
                expect_payload <= payload_in;
        end
    end

    integer errors = 0;
    integer forwarded = 0;

    always @(negedge clk) begin
        if (!rst) begin
            if (valid_out !== expect_valid) begin
                errors = errors + 1;
                $display("FAIL: valid_out=%b, expected %b for id %h at t=%0t", valid_out, expect_valid, can_id, $time);
            end else if (valid_out) begin
                forwarded = forwarded + 1;
                if (payload_out !== expect_payload) begin
                    errors = errors + 1;
                    $display("FAIL: payload %h, expected %h at t=%0t", payload_out, expect_payload, $time);
                end
            end
        end
    end

    task send(input [10:0] id, input [63:0] payload);
        begin
            @(negedge clk);
            valid_in = 1;
            can_id = id;
            payload_in = payload;
        end
    endtask

    initial begin
        $dumpfile("can_filter.vcd");
        $dumpvars(0, tb_can_filter);

        repeat (2) @(negedge clk);
        rst = 0;
        send(11'h100, 64'hA1A10001);  // telemetry request  - allowed
        send(11'h555, 64'hBAD00001);  // unknown node       - blocked
        send(11'h101, 64'hA1A10002);  // housekeeping       - allowed
        send(11'h1FF, 64'hBAD00002);  // adjacent id        - blocked
        send(11'h200, 64'hA1A10003);  // payload data       - allowed
        send(11'h000, 64'hBAD00003);  // null id            - blocked
        send(11'h100, 64'hA1A10004);  // repeat allowed id  - allowed
        @(negedge clk);
        valid_in = 0;
        repeat (3) @(negedge clk);

        if (errors == 0 && forwarded == 4)
            $display("PASS: tb_can_filter, 7 packets in, 4 forwarded, 3 blocked as expected");
        else
            $display("FAIL: tb_can_filter, %0d errors, %0d forwarded (expected 4)", errors, forwarded);
        $finish;
    end
endmodule
