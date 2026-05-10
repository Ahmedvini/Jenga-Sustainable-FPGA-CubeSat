`include "filter_rules.vh"

module packet_classifier (
    input wire [10:0] can_id,
    output wire allowed
);
    assign allowed = (can_id == `CAN_RULE_0) || (can_id == `CAN_RULE_1) || (can_id == `CAN_RULE_2);
endmodule
