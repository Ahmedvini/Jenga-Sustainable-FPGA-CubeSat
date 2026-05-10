module can_packet_filter (
    input wire clk,
    input wire rst,
    input wire valid_in,
    input wire [10:0] can_id,
    input wire [63:0] payload_in,
    output reg valid_out,
    output reg [63:0] payload_out
);
    wire allowed;
    packet_classifier classifier_i(.can_id(can_id), .allowed(allowed));

    always @(posedge clk) begin
        if (rst) begin
            valid_out <= 0;
            payload_out <= 0;
        end else begin
            valid_out <= valid_in && allowed;
            if (valid_in && allowed) begin
                payload_out <= payload_in;
            end
        end
    end
endmodule
