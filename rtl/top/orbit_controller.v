module orbit_controller #(
    parameter SUNLIGHT_TICKS = 57,
    parameter ORBIT_TICKS = 95,
    // Clock cycles per orbit tick. 1 = one tick per clock (default,
    // identical to the original behavior). Board demos override this so
    // an orbit runs at human-visible speed.
    parameter PRESCALER = 1
) (
    input wire clk,
    input wire rst,
    output reg sunlight
);
    integer tick;
    wire tick_en;

    generate
        if (PRESCALER > 1) begin : gen_prescale
            reg [$clog2(PRESCALER)-1:0] prescale;
            assign tick_en = (prescale == PRESCALER - 1);
            always @(posedge clk) begin
                if (rst || tick_en)
                    prescale <= 0;
                else
                    prescale <= prescale + 1;
            end
        end else begin : gen_no_prescale
            assign tick_en = 1'b1;
        end
    endgenerate

    always @(posedge clk) begin
        if (rst) begin
            tick <= 0;
            sunlight <= 1'b1;
        end else if (tick_en) begin
            sunlight <= (tick < SUNLIGHT_TICKS);
            if (tick == ORBIT_TICKS - 1) begin
                tick <= 0;
            end else begin
                tick <= tick + 1;
            end
        end
    end
endmodule
