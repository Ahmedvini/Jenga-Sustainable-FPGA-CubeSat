// OBC task scheduler (Jenga FPGA-based OBC).
// Gates workloads by orbit state: compression only in sunlight (comms
// rail available for downlink), CAN filtering whenever packets arrive.
// Registered outputs; policy mirrors simulation/scheduler/.
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
