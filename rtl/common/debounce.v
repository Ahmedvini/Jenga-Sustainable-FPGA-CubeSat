module debounce #(
    parameter COUNT_MAX = 8
) (
    input wire clk,
    input wire rst,
    input wire noisy_in,
    output reg clean_out
);
    integer count;
    reg last;

    always @(posedge clk) begin
        if (rst) begin
            count <= 0;
            last <= 0;
            clean_out <= 0;
        end else if (noisy_in == last) begin
            if (count < COUNT_MAX) begin
                count <= count + 1;
            end else begin
                clean_out <= noisy_in;
            end
        end else begin
            count <= 0;
            last <= noisy_in;
        end
    end
endmodule
