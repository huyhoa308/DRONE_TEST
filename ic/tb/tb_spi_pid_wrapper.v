// =============================================================================
// tb_spi_pid_wrapper - kiem thu giao tiep SPI Mode 0 (khung 192 bit) cua
// spi_pid_wrapper voi N mau dau tien (mac dinh 100) trong vectors.txt.
//
// Testbench dong vai ESP32 (SPI master, CPOL=0 CPHA=0, MSB truoc):
//   - Master doi MOSI khi SCLK xuong (va truoc canh len dau tien),
//     lay mau MISO khi SCLK len.
//   - SCLK = 1 MHz (nua chu ky 500 ns = 5 chu ky clk 10 MHz). Wrapper lay mau
//     SCLK bang clk qua 3 flip-flop, nen f_sclk phai <= ~f_clk/4.
//
// Kiem tra bit-exact hai chieu:
//   * MOSI: moi khung mau tao dung 1 xung w_sample (khong co w_clear) va cac
//     day noi vao loi pid_ctrl (armed, throttle, sp_*, roll, pitch, gz) bang
//     dung gia tri trong vectors.txt. Khung clear tao dung 1 xung w_clear.
//   * MISO: khung NGAY SAU moi khung mau tra ve {busy, m1..m4, mix_r/p/y} cua
//     mau do; so voi dau ra mong doi trong vectors.txt (busy phai = 0).
//     Sau mau cuoi gui them 1 khung chi doc 80 bit (< 145 bit nen wrapper
//     khong coi la khung du lieu) de lay ket qua mau cuoi.
//
// Dong vector co clear = 1: gui 1 khung clear (bit 191 = 1) roi moi gui khung mau.
//
// Chay tu thu muc goc repo (Icarus Verilog):
//   cd ic/sim
//   iverilog -g2005 -Wall -I ../rtl -o tb_spi_pid_wrapper.vvp ../tb/tb_spi_pid_wrapper.v ../rtl/spi_pid_wrapper.v ../rtl/pid_ctrl.v
//   vvp -n tb_spi_pid_wrapper.vvp +VEC=../tb/vectors.txt
// Tuy chon: +N=<so mau> (mac dinh 100), +VCD=<file.vcd>
// =============================================================================
`timescale 1ns / 1ps

module tb_spi_pid_wrapper;
`include "pid_params.vh"

    localparam integer T_HALF_SCLK = 500;     // ns -> SCLK 1 MHz
    localparam integer FRAME_BITS  = 192;
    localparam integer READ_BITS   = 80;      // khung chi doc: < 145 bit

    reg clk = 1'b0;
    always #50 clk = ~clk;                    // 10 MHz

    reg  rst_n    = 1'b0;
    reg  spi_sclk = 1'b0;
    reg  spi_cs_n = 1'b1;
    reg  spi_mosi = 1'b0;
    wire spi_miso, irq_out_valid, busy;

    spi_pid_wrapper dut (
        .clk(clk), .rst_n(rst_n),
        .spi_sclk(spi_sclk), .spi_cs_n(spi_cs_n),
        .spi_mosi(spi_mosi), .spi_miso(spi_miso),
        .irq_out_valid(irq_out_valid), .busy(busy)
    );

    // ------------------------------------------------ dem xung trong wrapper ----
    integer n_sample_pulse = 0, n_clear_pulse = 0, n_irq = 0;
    integer mosi_err = 0;

    // Gia tri MOSI mong doi cho khung mau dang gui
    reg                   exp_armed;
    reg [10:0]            exp_thr;
    reg signed [W_IN-1:0] exp_spr, exp_spp, exp_spy, exp_r, exp_p, exp_gz;

    always @(posedge clk) begin
        if (dut.w_clear)       n_clear_pulse <= n_clear_pulse + 1;
        if (irq_out_valid)     n_irq         <= n_irq + 1;
        if (dut.w_sample) begin
            n_sample_pulse <= n_sample_pulse + 1;
            // Kiem tra day noi vao loi dung tai chu ky loi chot dau vao
            if (dut.w_armed    !== exp_armed || dut.w_throttle !== exp_thr   ||
                dut.w_sp_roll  !== exp_spr   || dut.w_sp_pitch !== exp_spp   ||
                dut.w_sp_yaw   !== exp_spy   || dut.w_roll     !== exp_r     ||
                dut.w_pitch    !== exp_p     || dut.w_gz       !== exp_gz) begin
                mosi_err <= mosi_err + 1;
                $display("LECH MOSI: armed=%0d thr=%0d sp=%0d,%0d,%0d mea=%0d,%0d,%0d | mong doi armed=%0d thr=%0d sp=%0d,%0d,%0d mea=%0d,%0d,%0d",
                         dut.w_armed, dut.w_throttle, dut.w_sp_roll, dut.w_sp_pitch, dut.w_sp_yaw,
                         dut.w_roll, dut.w_pitch, dut.w_gz,
                         exp_armed, exp_thr, exp_spr, exp_spp, exp_spy, exp_r, exp_p, exp_gz);
            end
        end
    end

    // ------------------------------------------------------ SPI master ----
    reg [FRAME_BITS-1:0] tx_frame, rx_frame;

    // Gui nbits dau tien (MSB truoc) cua tx_frame, thu MISO vao rx_frame[191 -: nbits]
    task spi_xfer;
        input integer nbits;
        integer i;
        begin
            rx_frame = {FRAME_BITS{1'b0}};
            spi_sclk = 1'b0;
            spi_mosi = tx_frame[FRAME_BITS-1];
            spi_cs_n = 1'b0;
            #(T_HALF_SCLK);                       // cho wrapper thay csn_fall, nap tx_shift
            for (i = 0; i < nbits; i = i + 1) begin
                spi_sclk = 1'b1;                  // canh len: ca hai ben lay mau
                rx_frame[FRAME_BITS-1-i] = spi_miso;
                #(T_HALF_SCLK);
                spi_sclk = 1'b0;                  // canh xuong: master dat bit ke tiep
                if (i + 1 < nbits)
                    spi_mosi = tx_frame[FRAME_BITS-2-i];
                #(T_HALF_SCLK);
            end
            spi_cs_n = 1'b1;
            spi_mosi = 1'b0;
            #(T_HALF_SCLK);
            // cho dong bo csn_rise + frame_done + 20 chu ky tinh PID
            repeat (40) @(posedge clk);
        end
    endtask

    // ------------------------------------------------- kiem tra MISO ----
    integer miso_err = 0, miso_checked = 0;
    reg     have_pending = 1'b0;
    integer p_idx, p_mr, p_mp, p_my, p_m1, p_m2, p_m3, p_m4;

    task check_miso;
        reg [10:0] r_m1, r_m2, r_m3, r_m4;
        reg [9:0]  r_mr, r_mp, r_my;
        reg        r_busy;
        begin
            if (have_pending) begin
                r_busy = rx_frame[191];
                r_m1   = rx_frame[190:180];
                r_m2   = rx_frame[179:169];
                r_m3   = rx_frame[168:158];
                r_m4   = rx_frame[157:147];
                r_mr   = rx_frame[146:137];
                r_mp   = rx_frame[136:127];
                r_my   = rx_frame[126:117];
                miso_checked = miso_checked + 1;
                if (r_busy !== 1'b0 ||
                    r_m1 !== p_m1[10:0] || r_m2 !== p_m2[10:0] ||
                    r_m3 !== p_m3[10:0] || r_m4 !== p_m4[10:0] ||
                    r_mr !== p_mr[9:0]  || r_mp !== p_mp[9:0]  || r_my !== p_my[9:0]) begin
                    miso_err = miso_err + 1;
                    if (miso_err <= 10)
                        $display("LECH MISO mau %0d: busy=%0d m=%0d,%0d,%0d,%0d mix=%0d,%0d,%0d | mong doi m=%0d,%0d,%0d,%0d mix=%0d,%0d,%0d",
                                 p_idx, r_busy, r_m1, r_m2, r_m3, r_m4,
                                 $signed(r_mr), $signed(r_mp), $signed(r_my),
                                 p_m1, p_m2, p_m3, p_m4, p_mr, p_mp, p_my);
                end
                have_pending = 1'b0;
            end
        end
    endtask

    // ------------------------------------------------------------ chinh ----
    reg [8*512-1:0] vec_file;
    reg [8*512-1:0] vcd_file;
    integer fd, n, n_max, samples, clears, pulses_before, clears_before, frame_err;
    integer v_clear, v_armed, v_thr, v_spr, v_spp, v_spy, v_r, v_p, v_gz;
    integer x_mr, x_mp, x_my, x_m1, x_m2, x_m3, x_m4;
    reg signed [W_IN-1:0] f_spr, f_spp, f_spy, f_r, f_p, f_gz;

    initial begin
        if ($value$plusargs("VCD=%s", vcd_file)) begin
            $dumpfile(vcd_file);
            $dumpvars(0, tb_spi_pid_wrapper);
        end
        if (!$value$plusargs("VEC=%s", vec_file)) vec_file = "vectors.txt";
        if (!$value$plusargs("N=%d", n_max)) n_max = 100;
        fd = $fopen(vec_file, "r");
        if (fd == 0) begin
            $display("FATAL: khong mo duoc %0s", vec_file);
            $finish;
        end
        samples = 0; clears = 0; frame_err = 0;

        repeat (3) @(negedge clk);
        rst_n = 1'b1;
        repeat (5) @(negedge clk);

        while (!$feof(fd) && samples < n_max) begin
            n = $fscanf(fd, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                        v_clear, v_armed, v_thr, v_spr, v_spp, v_spy, v_r, v_p, v_gz,
                        x_mr, x_mp, x_my, x_m1, x_m2, x_m3, x_m4);
            if (n == 16) begin
                // ---- khung clear (bit 191 = 1) ----
                if (v_clear) begin
                    tx_frame       = {FRAME_BITS{1'b0}};
                    tx_frame[191]  = 1'b1;
                    pulses_before  = n_sample_pulse;
                    clears_before  = n_clear_pulse;
                    spi_xfer(FRAME_BITS);
                    check_miso;
                    clears = clears + 1;
                    if (n_clear_pulse != clears_before + 1 || n_sample_pulse != pulses_before) begin
                        frame_err = frame_err + 1;
                        $display("LOI khung clear %0d: %0d xung clear, %0d xung sample",
                                 clears, n_clear_pulse - clears_before, n_sample_pulse - pulses_before);
                    end
                end

                // ---- khung mau ----
                f_spr = v_spr; f_spp = v_spp; f_spy = v_spy;
                f_r   = v_r;   f_p   = v_p;   f_gz  = v_gz;
                exp_armed = v_armed[0]; exp_thr = v_thr[10:0];
                exp_spr = f_spr; exp_spp = f_spp; exp_spy = f_spy;
                exp_r   = f_r;   exp_p   = f_p;   exp_gz  = f_gz;

                tx_frame = {FRAME_BITS{1'b0}};
                tx_frame[191]     = 1'b0;
                tx_frame[190]     = v_armed[0];
                tx_frame[189:179] = v_thr[10:0];
                tx_frame[178 -: W_IN] = f_spr;
                tx_frame[156 -: W_IN] = f_spp;
                tx_frame[134 -: W_IN] = f_spy;
                tx_frame[112 -: W_IN] = f_r;
                tx_frame[90  -: W_IN] = f_p;
                tx_frame[68  -: W_IN] = f_gz;

                pulses_before = n_sample_pulse;
                clears_before = n_clear_pulse;
                spi_xfer(FRAME_BITS);
                check_miso;                       // ket qua cua mau truoc (neu co)
                if (n_sample_pulse != pulses_before + 1 || n_clear_pulse != clears_before) begin
                    frame_err = frame_err + 1;
                    $display("LOI khung mau %0d: %0d xung sample, %0d xung clear",
                             samples, n_sample_pulse - pulses_before, n_clear_pulse - clears_before);
                end
                if (busy !== 1'b0) begin
                    frame_err = frame_err + 1;
                    $display("LOI mau %0d: loi van busy sau 40 chu ky", samples);
                end

                have_pending = 1'b1;
                p_idx = samples;
                p_mr = x_mr; p_mp = x_mp; p_my = x_my;
                p_m1 = x_m1; p_m2 = x_m2; p_m3 = x_m3; p_m4 = x_m4;
                samples = samples + 1;
            end
        end
        $fclose(fd);

        // ---- khung chi doc de lay ket qua mau cuoi ----
        tx_frame      = {FRAME_BITS{1'b0}};
        pulses_before = n_sample_pulse;
        clears_before = n_clear_pulse;
        spi_xfer(READ_BITS);
        check_miso;
        if (n_sample_pulse != pulses_before || n_clear_pulse != clears_before) begin
            frame_err = frame_err + 1;
            $display("LOI: khung doc %0d bit lai kich hoat loi PID", READ_BITS);
        end

        $display("----------------------------------------------------------------");
        $display("SPI Mode 0, khung %0d bit, SCLK %0d kHz: %0d mau, %0d khung clear, %0d xung irq_out_valid",
                 FRAME_BITS, 1000000 / (2 * T_HALF_SCLK), samples, clears, n_irq);
        $display("MOSI: %0d/%0d mau dung | MISO: %0d/%0d mau dung | loi khung: %0d",
                 samples - mosi_err, samples, miso_checked - miso_err, miso_checked, frame_err);
        if (samples == 0)
            $display("FAIL: khong doc duoc mau nao");
        else if (mosi_err == 0 && miso_err == 0 && frame_err == 0 &&
                 miso_checked == samples && n_irq == samples)
            $display("PASS: %0d/%0d mau khop bit-exact qua SPI (MOSI va MISO)", samples, samples);
        else
            $display("FAIL: MOSI lech %0d, MISO lech %0d, loi khung %0d, irq %0d/%0d",
                     mosi_err, miso_err, frame_err, n_irq, samples);
        $display("----------------------------------------------------------------");
        $finish;
    end

endmodule
