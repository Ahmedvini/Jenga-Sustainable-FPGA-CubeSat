module orbit_controller #(
    parameter SUNLIGHT_TICKS = 57,
    parameter ORBIT_TICKS = 95
) (
    input wire clk,
    input wire rst,
    output reg sunlight
);
    integer tick;

    always @(posedge clk) begin
        if (rst) begin
            tick <= 0;
            sunlight <= 1'b1;
        end else begin
            sunlight <= (tick < SUNLIGHT_TICKS);
            if (tick == ORBIT_TICKS - 1) begin
                tick <= 0;
            end else begin
                tick <= tick + 1;
            end
        end
    end
endmodule
