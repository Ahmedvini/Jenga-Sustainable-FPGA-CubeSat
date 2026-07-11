// Deployment wrapper for the Lattice iCEstick (iCE40HX1K-TQ144).
//
// The core runs at the full 12 MHz clock, but the orbit controller is
// prescaled so one simulated 95-tick orbit takes about 10 seconds — slow
// enough to watch on the LEDs:
//
//   D5 (green) sunlight: on ~6 s (sunlight), off ~4 s (eclipse)
//   D1         fpga_power_en  (burst rail: active only in sunlight w/ work)
//   D2         comms_power_en (comms rail: shuts off in eclipse)
//   D3         processing activity (filter/compression/FIR valids, pulse-
//              stretched to visible flashes)
//   D4         datapath activity (XOR fold of payload/sample outputs)
//
//   uart_txd   live telemetry: ASCII frames at 115200 8N1 through the
//              on-board FTDI (iCE40 pin 8), ~3 frames/s:
//              "JGA n=<frame> s=<sun> b=<burst> p=<pkts> z=<rle> f=<fir>"
//              (all multi-bit fields hex; counters are cumulative)
//
// A 32-bit LFSR supplies pseudo-random CAN/telemetry/sensor stimulus, so
// every core input is driven and every output cone is observed — nothing
// can be optimized away, and utilization/timing reflect the real design.
module icestick_top (
    input  wire clk,        // 12 MHz on-board oscillator (pin 21)
    output wire [4:0] led,  // D1..D5
    output wire uart_txd    // telemetry -> on-board FTDI ch B (pin 8)
);
    // One orbit = 95 ticks; 12 MHz / 1_250_000 ~= 9.6 Hz tick rate
    // -> orbit ~9.9 s, sunlight ~5.9 s, eclipse ~4.0 s.
    localparam ORBIT_PRESCALER = 1_250_000;

    // Power-on reset: hold rst high for the first 8 clocks
    reg [3:0] por = 4'd0;
    wire rst = ~por[3];
    always @(posedge clk) begin
        if (!por[3])
            por <= por + 4'd1;
    end

    // Pseudo-random stimulus generator
    reg [31:0] lfsr = 32'h1;
    always @(posedge clk)
        lfsr <= {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};

    // Packets arrive in visible bursts: ~0.35 s of traffic every ~1.4 s,
    // so the activity LEDs flash instead of sitting solid-on.
    reg [23:0] burst_cnt = 0;
    always @(posedge clk)
        burst_cnt <= burst_cnt + 1;
    wire burst_window = (burst_cnt[23:22] == 2'b00);
    wire packet_ready = lfsr[27] && burst_window;

    wire sunlight_demo;
    wire fpga_power_en;
    wire comms_power_en;
    wire filter_valid;
    wire compression_valid;
    wire fir_valid;
    wire [63:0] filtered_payload;
    wire [7:0] rle_value;
    wire [7:0] rle_count;
    wire signed [15:0] fir_sample;

    // Demo-rate orbit state drives the scheduler/power controller via the
    // core; a mirrored instance here exposes sunlight for the green LED.
    fpga_accelerator_top #(
        .ORBIT_PRESCALER(ORBIT_PRESCALER)
    ) core_i (
        .clk(clk),
        .rst(rst),
        .packet_ready(packet_ready),
        .can_id(lfsr[10:0]),
        .telemetry_byte(lfsr[18:11]),
        .sensor_sample(lfsr[26:19]),
        .fpga_power_en(fpga_power_en),
        .comms_power_en(comms_power_en),
        .filter_valid(filter_valid),
        .compression_valid(compression_valid),
        .fir_valid(fir_valid),
        .filtered_payload(filtered_payload),
        .rle_value(rle_value),
        .rle_count(rle_count),
        .fir_sample(fir_sample)
    );

    assign sunlight_demo = comms_power_en;  // comms rail tracks sunlight

    // Pulse-stretchers: turn microsecond valid blips into ~175 ms flashes
    reg [20:0] proc_stretch = 0;
    always @(posedge clk) begin
        if (filter_valid || compression_valid || fir_valid)
            proc_stretch <= {21{1'b1}};
        else if (proc_stretch != 0)
            proc_stretch <= proc_stretch - 1;
    end

    // Datapath LED triggers on output changes, not levels, so it decays
    // dark between packet bursts.
    wire data_fold = ^filtered_payload ^ ^fir_sample ^ ^rle_value ^ ^rle_count;
    reg data_fold_prev = 0;
    reg [20:0] data_stretch = 0;
    always @(posedge clk) begin
        data_fold_prev <= data_fold;
        if (data_fold != data_fold_prev)
            data_stretch <= {21{1'b1}};
        else if (data_stretch != 0)
            data_stretch <= data_stretch - 1;
    end

    assign led[0] = fpga_power_en;         // D1: FPGA burst rail
    assign led[1] = comms_power_en;        // D2: comms rail (off in eclipse)
    assign led[2] = (proc_stretch != 0);   // D3: processing activity
    assign led[3] = (data_stretch != 0);   // D4: datapath activity
    assign led[4] = sunlight_demo;         // D5 green: sunlight/eclipse

    // ------------------------------------------------------------------
    // UART telemetry: snapshot the OBC state ~2.9x/s and stream it as a
    // 41-char ASCII frame. The counters accumulate datapath results.
    // ------------------------------------------------------------------
    reg [15:0] pkt_cnt = 0, rle_cnt = 0, fir_cnt = 0, frame_no = 0;
    always @(posedge clk) begin
        if (filter_valid)      pkt_cnt <= pkt_cnt + 1'b1;
        if (compression_valid) rle_cnt <= rle_cnt + 1'b1;
        if (fir_valid)         fir_cnt <= fir_cnt + 1'b1;
    end

    reg [21:0] tele_cnt = 0;               // 2^22 / 12 MHz ~= 0.35 s
    always @(posedge clk)
        tele_cnt <= tele_cnt + 1'b1;
    wire frame_tick = (tele_cnt == 22'd0);

    reg s_sun = 0, s_burst = 0;
    reg [15:0] s_frame = 0, s_pkt = 0, s_rle = 0, s_fir = 0;

    function [7:0] hexdigit;
        input [3:0] n;
        hexdigit = (n < 4'd10) ? (8'h30 + n) : (8'h37 + n);
    endfunction

    // "JGA n=XXXX s=X b=X p=XXXX z=XXXX f=XXXX\r\n" (41 chars)
    function [7:0] frame_char;
        input [5:0] i;
        case (i)
            6'd0: frame_char = "J";
            6'd1: frame_char = "G";
            6'd2: frame_char = "A";
            6'd4: frame_char = "n";
            6'd11: frame_char = "s";
            6'd15: frame_char = "b";
            6'd19: frame_char = "p";
            6'd26: frame_char = "z";
            6'd33: frame_char = "f";
            6'd5, 6'd12, 6'd16, 6'd20, 6'd27, 6'd34: frame_char = "=";
            6'd6: frame_char = hexdigit(s_frame[15:12]);
            6'd7: frame_char = hexdigit(s_frame[11:8]);
            6'd8: frame_char = hexdigit(s_frame[7:4]);
            6'd9: frame_char = hexdigit(s_frame[3:0]);
            6'd13: frame_char = s_sun ? "1" : "0";
            6'd17: frame_char = s_burst ? "1" : "0";
            6'd21: frame_char = hexdigit(s_pkt[15:12]);
            6'd22: frame_char = hexdigit(s_pkt[11:8]);
            6'd23: frame_char = hexdigit(s_pkt[7:4]);
            6'd24: frame_char = hexdigit(s_pkt[3:0]);
            6'd28: frame_char = hexdigit(s_rle[15:12]);
            6'd29: frame_char = hexdigit(s_rle[11:8]);
            6'd30: frame_char = hexdigit(s_rle[7:4]);
            6'd31: frame_char = hexdigit(s_rle[3:0]);
            6'd35: frame_char = hexdigit(s_fir[15:12]);
            6'd36: frame_char = hexdigit(s_fir[11:8]);
            6'd37: frame_char = hexdigit(s_fir[7:4]);
            6'd38: frame_char = hexdigit(s_fir[3:0]);
            6'd39: frame_char = 8'h0D;
            6'd40: frame_char = 8'h0A;
            default: frame_char = " ";
        endcase
    endfunction

    localparam LAST_CHAR = 6'd40;
    reg sending = 0;
    reg [5:0] ci = 0;
    reg tx_valid = 0;
    reg [7:0] tx_data = 8'h00;
    wire tx_busy;

    always @(posedge clk) begin
        tx_valid <= 1'b0;
        if (rst) begin
            sending <= 1'b0;
            ci <= 6'd0;
        end else if (!sending) begin
            if (frame_tick) begin
                s_frame <= frame_no;
                s_sun <= sunlight_demo;
                s_burst <= fpga_power_en;
                s_pkt <= pkt_cnt;
                s_rle <= rle_cnt;
                s_fir <= fir_cnt;
                frame_no <= frame_no + 1'b1;
                sending <= 1'b1;
                ci <= 6'd0;
            end
        end else if (!tx_busy && !tx_valid) begin
            tx_data <= frame_char(ci);
            tx_valid <= 1'b1;
            if (ci == LAST_CHAR)
                sending <= 1'b0;
            else
                ci <= ci + 6'd1;
        end
    end

    uart_tx #(.DIVIDER(104)) uart_i (  // 12 MHz / 115200 baud
        .clk(clk),
        .rst(rst),
        .valid(tx_valid),
        .data(tx_data),
        .tx(uart_txd),
        .busy(tx_busy)
    );
endmodule
