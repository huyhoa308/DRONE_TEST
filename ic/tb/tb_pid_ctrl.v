// =============================================================================
// tb_pid_ctrl - so sanh bit-exact pid_ctrl voi mo hinh fixed-point Python
//
// Doc vectors.txt (sinh boi ic/model/export_rtl.py), moi dong 1 mau IMU:
//   clear armed throttle sp_roll sp_pitch sp_yaw roll pitch gz  mix_r mix_p mix_y m1 m2 m3 m4
//   |------------------------ dau vao -----------------------|  |------ dau ra mong doi ----|
// clear = 1 o dau moi kich ban -> xoa trang thai PID nhu khi tao controller moi trong Python.
// Duong dan file: +VEC=<duong_dan> (mac dinh vectors.txt).
// =============================================================================
`timescale 1ns / 1ps

module tb_pid_ctrl;
`include "pid_params.vh"

    reg clk = 1'b0;
    always #50 clk = ~clk;                    // 10 MHz

    reg                    rst_n = 1'b0, clear = 1'b0, sample_valid = 1'b0, armed = 1'b0;
    reg  [10:0]            throttle = 11'd0;
    reg  signed [W_IN-1:0] sp_roll = 0, sp_pitch = 0, sp_yaw = 0, roll = 0, pitch = 0, gz = 0;
    wire [10:0]            m1, m2, m3, m4;
    wire signed [9:0]      mix_roll, mix_pitch, mix_yaw;
    wire                   out_valid, busy;

    pid_ctrl dut (
        .clk(clk), .rst_n(rst_n), .clear(clear), .sample_valid(sample_valid),
        .armed(armed), .throttle(throttle),
        .sp_roll(sp_roll), .sp_pitch(sp_pitch), .sp_yaw(sp_yaw),
        .roll(roll), .pitch(pitch), .gz(gz),
        .m1(m1), .m2(m2), .m3(m3), .m4(m4),
        .mix_roll(mix_roll), .mix_pitch(mix_pitch), .mix_yaw(mix_yaw),
        .out_valid(out_valid), .busy(busy)
    );

    reg [8*512-1:0] vec_file;
    integer fd, n, samples, errors, lat, max_lat, scenario;
    integer v_clear, v_armed, v_thr, v_spr, v_spp, v_spy, v_r, v_p, v_gz;
    integer x_mr, x_mp, x_my, x_m1, x_m2, x_m3, x_m4;

    initial begin
        if (!$value$plusargs("VEC=%s", vec_file)) vec_file = "vectors.txt";
        fd = $fopen(vec_file, "r");
        if (fd == 0) begin
            $display("FATAL: khong mo duoc %0s", vec_file);
            $finish;
        end
        samples = 0; errors = 0; max_lat = 0; scenario = 0;

        repeat (3) @(negedge clk);
        rst_n = 1'b1;
        @(negedge clk);

        while (!$feof(fd)) begin
            n = $fscanf(fd, "%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d\n",
                        v_clear, v_armed, v_thr, v_spr, v_spp, v_spy, v_r, v_p, v_gz,
                        x_mr, x_mp, x_my, x_m1, x_m2, x_m3, x_m4);
            if (n == 16) begin
                if (v_clear) begin
                    scenario = scenario + 1;
                    clear = 1'b1; @(negedge clk); clear = 1'b0;
                end
                armed = v_armed; throttle = v_thr;
                sp_roll = v_spr; sp_pitch = v_spp; sp_yaw = v_spy;
                roll = v_r; pitch = v_p; gz = v_gz;
                sample_valid = 1'b1;
                @(negedge clk);
                sample_valid = 1'b0;
                lat = 1;
                while (out_valid !== 1'b1) begin
                    @(negedge clk);
                    lat = lat + 1;
                    if (lat > 100) begin
                        $display("FATAL: mau %0d khong co out_valid sau 100 chu ky", samples);
                        $finish;
                    end
                end
                if (lat > max_lat) max_lat = lat;
                if (m1 !== x_m1 || m2 !== x_m2 || m3 !== x_m3 || m4 !== x_m4 ||
                    mix_roll !== x_mr || mix_pitch !== x_mp || mix_yaw !== x_my) begin
                    errors = errors + 1;
                    if (errors <= 10)
                        $display("LECH kich ban %0d mau %0d: RTL mix=%0d,%0d,%0d m=%0d,%0d,%0d,%0d | mong doi mix=%0d,%0d,%0d m=%0d,%0d,%0d,%0d",
                                 scenario, samples, mix_roll, mix_pitch, mix_yaw, m1, m2, m3, m4,
                                 x_mr, x_mp, x_my, x_m1, x_m2, x_m3, x_m4);
                end
                samples = samples + 1;
                @(negedge clk);
            end
        end
        $fclose(fd);

        $display("----------------------------------------------------------------");
        $display("%0d kich ban, %0d mau, do tre toi da %0d chu ky clock / mau", scenario, samples, max_lat);
        if (samples == 0)
            $display("FAIL: khong doc duoc mau nao");
        else if (errors == 0)
            $display("PASS: %0d/%0d mau khop bit-exact voi mo hinh Python", samples, samples);
        else
            $display("FAIL: %0d/%0d mau lech", errors, samples);
        $display("----------------------------------------------------------------");
        $finish;
    end

endmodule
