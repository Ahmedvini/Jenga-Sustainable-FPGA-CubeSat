module packet_encoder (
    input wire [7:0] value,
    input wire [7:0] count,
    output wire [15:0] packet
);
    assign packet = {value, count};
endmodule
