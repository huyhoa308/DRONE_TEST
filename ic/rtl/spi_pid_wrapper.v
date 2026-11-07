// =============================================================================
// spi_pid_wrapper - Giao tiep SPI Slave 4-day cho loi vi mach pid_ctrl
// Nhom FPOLY UAV - Cuoc thi Thiet ke vi mach cho Do thi thong minh lan 3
//
// Giai quyet bai toan "Pad-Limited" khi Tape-out ASIC hoac nhung FPGA:
//   - Loi pid_ctrl co ~160 bit dau vao/ra song song.
//   - Wrapper nay gom toan bo giao tiep voi MCU (ESP32) ve 4 chan SPI Mode 0
//     (sclk, cs_n, mosi, miso) + clk, rst_n, irq_out_valid -> Tong cong 7 chan!
//
// Khung truyen SPI (192-bit = 24 byte moi giao dich khi cs_n = 0):
//   * MOSI (ESP32 -> Chip):
//       [191]     clear         (1 bit)
//       [190]     armed         (1 bit)
//       [189:179] throttle      (11 bit, us 0..2047)
//       [178:157] sp_roll       (22 bit signed Q.FE)
//       [156:135] sp_pitch      (22 bit signed Q.FE)
//       [134:113] sp_yaw        (22 bit signed Q.FE)
//       [112:91]  roll          (22 bit signed Q.FE)
//       [90:69]   pitch         (22 bit signed Q.FE)
//       [68:47]   gz            (22 bit signed Q.FE)
//       [46:0]    reserved/CRC  (47 bit)
//   * MISO (Chip -> ESP32, tra ve ket qua cua mau lien truoc):
//       [191]     busy          (1 bit)
//       [190:180] m1            (11 bit, 1000..2000 us)
//       [179:169] m2            (11 bit, 1000..2000 us)
//       [168:158] m3            (11 bit, 1000..2000 us)
//       [157:147] m4            (11 bit, 1000..2000 us)
//       [146:137] mix_roll      (10 bit signed)
//       [136:127] mix_pitch     (10 bit signed)
//       [126:117] mix_yaw       (10 bit signed)
//       [116:0]   zero padding
// =============================================================================
`timescale 1ns / 1ps

module spi_pid_wrapper (
    clk, rst_n,
    spi_sclk, spi_cs_n, spi_mosi, spi_miso,
    irq_out_valid, busy
);
`include "pid_params.vh"

    input  clk;
    input  rst_n;
    input  spi_sclk;
    input  spi_cs_n;
    input  spi_mosi;
    output spi_miso;
    output irq_out_valid;
    output busy;

    // --- Dong bo hoa tin hieu SPI sang mien xung nhip he thong (clk) ---
    reg [2:0] sclk_sync, csn_sync;
    reg [1:0] mosi_sync;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sclk_sync <= 3'b000;
            csn_sync  <= 3'b111;
            mosi_sync <= 2'b00;
        end else begin
            sclk_sync <= {sclk_sync[1:0], spi_sclk};
            csn_sync  <= {csn_sync[1:0],  spi_cs_n};
            mosi_sync <= {mosi_sync[0],   spi_mosi};
        end
    end

    wire sclk_rise = (sclk_sync[2:1] == 2'b01);
    wire sclk_fall = (sclk_sync[2:1] == 2'b10);
    wire csn_fall  = (csn_sync[2:1]  == 2'b10);
    wire csn_rise  = (csn_sync[2:1]  == 2'b01);
    wire csn_low   = ~csn_sync[1];

    // --- Thanh ghi dich 192-bit RX / TX ---
    reg [191:0] rx_shift, tx_shift;
    reg [7:0]   bit_cnt;
    reg         frame_done;

    wire [10:0]        m1_w, m2_w, m3_w, m4_w;
    wire signed [9:0]  mix_r_w, mix_p_w, mix_y_w;
    wire               out_valid_w, busy_w;

    assign spi_miso      = csn_low ? tx_shift[191] : 1'b0;
    assign irq_out_valid = out_valid_w;
    assign busy          = busy_w;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rx_shift   <= 192'd0;
            tx_shift   <= 192'd0;
            bit_cnt    <= 8'd0;
            frame_done <= 1'b0;
        end else begin
            frame_done <= 1'b0;
            if (csn_fall) begin
                bit_cnt  <= 8'd0;
                tx_shift <= {busy_w, m1_w, m2_w, m3_w, m4_w,
                             mix_r_w, mix_p_w, mix_y_w, 117'd0};
            end else if (csn_low) begin
                if (sclk_rise) begin
                    rx_shift <= {rx_shift[190:0], mosi_sync[1]};
                    bit_cnt  <= bit_cnt + 8'd1;
                end else if (sclk_fall) begin
                    tx_shift <= {tx_shift[190:0], 1'b0};
                end
            end else if (csn_rise && (bit_cnt >= 8'd145)) begin
                frame_done <= 1'b1;
            end
        end
    end

    // --- Anh xa khung bit sang ngo vao pid_ctrl ---
    wire                   w_clear    = frame_done &  rx_shift[191];
    wire                   w_sample   = frame_done & ~rx_shift[191];
    wire                   w_armed    = rx_shift[190];
    wire [10:0]            w_throttle = rx_shift[189:179];
    wire signed [W_IN-1:0] w_sp_roll  = rx_shift[178 -: W_IN];
    wire signed [W_IN-1:0] w_sp_pitch = rx_shift[156 -: W_IN];
    wire signed [W_IN-1:0] w_sp_yaw   = rx_shift[134 -: W_IN];
    wire signed [W_IN-1:0] w_roll     = rx_shift[112 -: W_IN];
    wire signed [W_IN-1:0] w_pitch    = rx_shift[90  -: W_IN];
    wire signed [W_IN-1:0] w_gz       = rx_shift[68  -: W_IN];

    pid_ctrl u_pid_core (
        .clk          (clk),
        .rst_n        (rst_n),
        .clear        (w_clear),
        .sample_valid (w_sample),
        .armed        (w_armed),
        .throttle     (w_throttle),
        .sp_roll      (w_sp_roll),
        .sp_pitch     (w_sp_pitch),
        .sp_yaw       (w_sp_yaw),
        .roll         (w_roll),
        .pitch        (w_pitch),
        .gz           (w_gz),
        .m1           (m1_w),
        .m2           (m2_w),
        .m3           (m3_w),
        .m4           (m4_w),
        .mix_roll     (mix_r_w),
        .mix_pitch    (mix_p_w),
        .mix_yaw      (mix_y_w),
        .out_valid    (out_valid_w),
        .busy         (busy_w)
    );

endmodule
