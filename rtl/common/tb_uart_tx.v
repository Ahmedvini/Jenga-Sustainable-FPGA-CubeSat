// Self-checking testbench for uart_tx: transmits four bytes covering
// the corner patterns and decodes them back off the wire at the baud
// rate (golden software UART receiver), checking data and stop bits.
`timescale 1ns / 1ps

module tb_uart_tx;
    localparam DIVIDER = 8;                 // fast baud for simulation
    localparam BIT_NS = DIVIDER * 10;       // 10 ns clock period below

    reg clk = 0;
    always #5 clk = ~clk;

    reg rst = 1;
    reg valid = 0;
    reg [7:0] data = 8'h00;
    wire tx, busy;

    uart_tx #(.DIVIDER(DIVIDER)) dut (
        .clk(clk),
        .rst(rst),
        .valid(valid),
        .data(data),
        .tx(tx),
        .busy(busy)
    );

    reg [7:0] expected [0:3];
    reg [7:0] rx_byte;
    integer errors = 0;
    integer i, b;

    initial begin
        $dumpfile("uart_tx.vcd");
        $dumpvars(0, tb_uart_tx);
        expected[0] = "J";
        expected[1] = 8'h55;
        expected[2] = 8'h00;
        expected[3] = 8'hFF;

        repeat (4) @(negedge clk);
        rst = 0;

        for (i = 0; i < 4; i = i + 1) begin
            @(negedge clk);
            data = expected[i];
            valid = 1;
            @(negedge clk);
            valid = 0;

            @(negedge tx);                  // start-bit falling edge
            #(BIT_NS + BIT_NS / 2);         // centre of data bit 0
            for (b = 0; b < 8; b = b + 1) begin
                rx_byte[b] = tx;
                #(BIT_NS);
            end
            if (tx !== 1'b1) begin          // centre of the stop bit
                errors = errors + 1;
                $display("FAIL: missing stop bit on byte %0d", i);
            end
            if (rx_byte !== expected[i]) begin
                errors = errors + 1;
                $display("FAIL: byte %0d got 0x%02h expected 0x%02h",
                         i, rx_byte, expected[i]);
            end
            wait (!busy);
        end

        if (errors == 0)
            $display("PASS: tb_uart_tx, 4 bytes transmitted and decoded correctly");
        else
            $display("FAIL: tb_uart_tx, %0d errors", errors);
        $finish;
    end
endmodule
