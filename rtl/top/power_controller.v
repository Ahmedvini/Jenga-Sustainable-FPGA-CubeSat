// OBC power controller (Jenga FPGA-based OBC).
// Drives switched-rail enables: comms rail follows sunlight; the FPGA
// burst rail is raised only in sunlight with pending work. On the bench
// these enables drive the IRLZ44N payload switch / rail gating.
module power_controller (
    input wire clk,
    input wire rst,
    input wire sunlight,
    input wire workload_pending,
    output reg fpga_power_en,
    output reg comms_power_en
);
    always @(posedge clk) begin
        if (rst) begin
            fpga_power_en <= 1'b0;
            comms_power_en <= 1'b0;
        end else begin
            fpga_power_en <= sunlight && workload_pending;
            comms_power_en <= sunlight;
        end
    end
endmodule
