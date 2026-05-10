module scheduler (
    input wire clk,
    input wire rst,
    input wire sunlight,
    input wire packet_ready,
    output reg run_compression,
    output reg run_filter
);
    always @(posedge clk) begin
        if (rst) begin
            run_compression <= 1'b0;
            run_filter <= 1'b0;
        end else begin
            run_compression <= sunlight && packet_ready;
            run_filter <= packet_ready;
        end
    end
endmodule
