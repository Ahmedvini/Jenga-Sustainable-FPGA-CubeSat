module edge_detector (
    input wire clk,
    input wire rst,
    input wire signal_in,
    output wire rising_edge
);
    reg signal_d;

    assign rising_edge = signal_in & ~signal_d;

    always @(posedge clk) begin
        if (rst) begin
            signal_d <= 1'b0;
        end else begin
            signal_d <= signal_in;
        end
    end
endmodule
