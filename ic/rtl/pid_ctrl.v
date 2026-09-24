// =============================================================================
// pid_ctrl - Bo dieu khien bay PID 3 truc + mixer X-frame cho quadcopter
// Nhom FPOLY UAV - Cuoc thi Thiet ke vi mach cho Do thi thong minh lan 3
//
// Chuc nang giong het UpdatePid() + mixer trong src/Flight/Flight.cpp (STM32), da
// chuyen sang fixed-point theo mo hinh ic/model/pid_model.py (FixedController).
// Mo hinh do la "dap an" bit-exact: testbench ic/tb/tb_pid_ctrl.v so tung chu ky.
//
// Kien truc: MOT bo nhan dung chung, chay tuan tu 3 truc (roll -> pitch -> yaw).
// Moi mau IMU (400 Hz) can 6 chu ky/truc x 3 + 2 = 20 chu ky clock; o clock 10 MHz
// chi mat 2 us trong 2500 us chu ky dieu khien -> tiet kiem dien tich toi da.
//
// Moi truc, voi e = setpoint - do dac:
//   A_raw = A + e                                   (tich phan, don vi e)
//   Df'   = Df + round(((e - e_prev) << FD - Df) * ALPHA >> FA)   (dao ham da loc)
//   u'    = round(KP'*e) + round(KI'*A_raw) + round(KD'*Df')      (Q.FU, u' = 3u)
//   sat   = clamp(u', +/-U_LIM); neu u' khong bao hoa: A = clamp(A_raw, +/-ACC_LIM)
//   mix   = clamp(cat_ve_0(sat >> FU), +/-MIX_LIM)                (us)
// Mixer X-frame: M1 truoc-trai, M2 truoc-phai, M3 sau-phai, M4 sau-trai.
// Chua arm hoac ga <= 1000: 4 motor = 1000, trang thai PID dung yen.
//
// Moi do rong bit / he so nam trong pid_params.vh (sinh boi ic/model/export_rtl.py).
// =============================================================================
`timescale 1ns / 1ps

module pid_ctrl (
    clk, rst_n, clear, sample_valid,
    armed, throttle, sp_roll, sp_pitch, sp_yaw, roll, pitch, gz,
    m1, m2, m3, m4, mix_roll, mix_pitch, mix_yaw, out_valid, busy
);
`include "pid_params.vh"

    input                     clk;
    input                     rst_n;         // reset bat dong bo, muc thap
    input                     clear;         // xoa trang thai PID (dong bo), chi khi !busy
    input                     sample_valid;  // xung 1 chu ky: co mau moi, chot toan bo dau vao
    input                     armed;
    input      [10:0]         throttle;      // us, 0..2047
    input  signed [W_IN-1:0]  sp_roll;       // Q.FE do
    input  signed [W_IN-1:0]  sp_pitch;      // Q.FE do
    input  signed [W_IN-1:0]  sp_yaw;        // Q.FE do/s
    input  signed [W_IN-1:0]  roll;          // Q.FE do
    input  signed [W_IN-1:0]  pitch;         // Q.FE do
    input  signed [W_IN-1:0]  gz;            // Q.FE do/s
    output reg [10:0]         m1, m2, m3, m4;               // us, 1000..2000
    output signed [9:0]       mix_roll, mix_pitch, mix_yaw; // us, lenh sau PID
    output reg                out_valid;     // xung 1 chu ky: m1..m4 va mix_* moi
    output                    busy;

    // ---------------------------------------------------------------- FSM ----
    localparam [2:0] S_IDLE = 3'd0,
                     S_LOAD = 3'd1,   // tinh e, A_raw, (de - Df); nap nhan ALPHA*(de-Df)
                     S_FILT = 3'd2,   // Df' = Df + round(tich);  nap nhan KP'*e
                     S_P    = 3'd3,   // P;                       nap nhan KI'*A_raw
                     S_I    = 3'd4,   // I;                       nap nhan KD'*Df'
                     S_D    = 3'd5,   // u' = P + I + D
                     S_SAT  = 3'd6,   // bao hoa, anti-windup, ghi trang thai, mix truc nay
                     S_MIX  = 3'd7;   // mixer 4 motor, out_valid

    reg [2:0] state;
    reg [1:0] axis;                   // 0 roll, 1 pitch, 2 yaw
    assign busy = (state != S_IDLE);

    // ---------------------------------------------------- dau vao da chot ----
    reg                     in_armed;
    reg [10:0]              in_thr;
    reg signed [W_IN-1:0]   in_sp  [0:2];
    reg signed [W_IN-1:0]   in_mea [0:2];

    // ------------------------------------------------ trang thai moi truc ----
    reg signed [W_ACC-1:0]  acc_r   [0:2];   // A: tong sai so (tich phan / dt)
    reg signed [W_E-1:0]    prev_r  [0:2];   // e chu ky truoc
    reg signed [W_DF-1:0]   dfilt_r [0:2];   // Df: hieu sai so da loc, Q.(FE+FD)
    reg signed [9:0]        mix_r   [0:2];

    assign mix_roll  = mix_r[0];
    assign mix_pitch = mix_r[1];
    assign mix_yaw   = mix_r[2];

    // ------------------------------------------------------ thanh ghi lam viec ----
    reg signed [W_E-1:0]    e_w;
    reg signed [W_ACC-1:0]  accraw_w;
    reg signed [W_DF-1:0]   dfnew_w;
    reg signed [W_U-1:0]    p_w, i_w, u_w;

    // ----------------------------------------------- bo nhan dung chung ----
    reg  signed [W_MA-1:0]  mul_a;
    reg  signed [W_MB-1:0]  mul_b;
    wire signed [W_P-1:0]   prod = mul_a * mul_b;

    // Dich phai so hoc n bit, lam tron 1/2 LSB neu ROUND: (x + 2^(n-1)) >>> n
    localparam signed [W_P-1:0] ONE = 1;
    function signed [W_P-1:0] shr;
        input signed [W_P-1:0] x;
        input [5:0]            n;
        begin
            if (n == 0)
                shr = x;
            else if (ROUND != 0)
                shr = (x + (ONE <<< (n - 1))) >>> n;
            else
                shr = x >>> n;
        end
    endfunction

    // --------------------------------------------- he so theo truc (hang so) ----
    function signed [W_MA-1:0] kp_m; input [1:0] a;
        case (a) 2'd0: kp_m = KP_M0; 2'd1: kp_m = KP_M1; default: kp_m = KP_M2; endcase
    endfunction
    function signed [W_MA-1:0] ki_m; input [1:0] a;
        case (a) 2'd0: ki_m = KI_M0; 2'd1: ki_m = KI_M1; default: ki_m = KI_M2; endcase
    endfunction
    function signed [W_MA-1:0] kd_m; input [1:0] a;
        case (a) 2'd0: kd_m = KD_M0; 2'd1: kd_m = KD_M1; default: kd_m = KD_M2; endcase
    endfunction
    function [5:0] sh_p; input [1:0] a;
        case (a) 2'd0: sh_p = SH_P0; 2'd1: sh_p = SH_P1; default: sh_p = SH_P2; endcase
    endfunction
    function [5:0] sh_i; input [1:0] a;
        case (a) 2'd0: sh_i = SH_I0; 2'd1: sh_i = SH_I1; default: sh_i = SH_I2; endcase
    endfunction
    function [5:0] sh_d; input [1:0] a;
        case (a) 2'd0: sh_d = SH_D0; 2'd1: sh_d = SH_D1; default: sh_d = SH_D2; endcase
    endfunction
    function signed [9:0] mix_lim; input [1:0] a;
        case (a) 2'd0: mix_lim = MIX_LIM0; 2'd1: mix_lim = MIX_LIM1; default: mix_lim = MIX_LIM2; endcase
    endfunction

    // ------------------------------------------ to hop: buoc S_LOAD ----
    wire signed [W_E-1:0]    e_cur      = in_sp[axis] - in_mea[axis];
    wire signed [W_ACC-1:0]  accraw_cur = acc_r[axis] + e_cur;
    wire signed [W_DE-1:0]   de_cur     = (e_cur - prev_r[axis]) <<< FD;
    wire signed [W_DIFF-1:0] diff_cur   = de_cur - dfilt_r[axis];

    // ------------------------------------------ to hop: buoc S_SAT ----
    localparam signed [W_U-1:0]   U_LIM_S   = U_LIM;
    localparam signed [W_ACC-1:0] ACC_LIM_S = ACC_LIM;
    wire              u_hi  = (u_w >  U_LIM_S);
    wire              u_lo  = (u_w < -U_LIM_S);
    wire signed [W_U-1:0] sat_w = u_hi ? U_LIM_S : (u_lo ? -U_LIM_S : u_w);
    // cat ve phia 0 nhu static_cast<int32_t>: so am thi dich tren tri tuyet doi
    wire signed [W_U-1:0] sat_abs  = sat_w[W_U-1] ? -sat_w : sat_w;
    wire signed [W_U-1:0] mag      = sat_abs >>> FU;
    wire signed [W_U-1:0] mix_raw  = sat_w[W_U-1] ? -mag : mag;
    wire signed [9:0]     lim      = mix_lim(axis);
    wire signed [9:0]     mix_new  = (mix_raw > lim) ? lim : ((mix_raw < -lim) ? -lim : mix_raw[9:0]);
    wire signed [W_ACC-1:0] acc_clamped = (accraw_w > ACC_LIM_S) ? ACC_LIM_S :
                                          ((accraw_w < -ACC_LIM_S) ? -ACC_LIM_S : accraw_w);

    // ------------------------------------------ to hop: mixer X-frame ----
    wire [10:0] thr_c = (in_thr < 11'd1000) ? 11'd1000 : ((in_thr > 11'd2000) ? 11'd2000 : in_thr);
    wire signed [12:0] t_s = {2'b00, thr_c};
    wire signed [12:0] r_s = mix_r[0];
    wire signed [12:0] p_s = mix_r[1];
    wire signed [12:0] y_s = mix_r[2];

    function [10:0] motor_clamp;
        input signed [12:0] v;
        begin
            if (v < 13'sd1000)      motor_clamp = 11'd1000;
            else if (v > 13'sd2000) motor_clamp = 11'd2000;
            else                    motor_clamp = v[10:0];
        end
    endfunction

    wire gated_in = !armed || (throttle <= 11'd1000);

    // ------------------------------------------------------------ tuan tu ----
    integer k;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state     <= S_IDLE;
            axis      <= 2'd0;
            out_valid <= 1'b0;
            m1 <= 11'd1000; m2 <= 11'd1000; m3 <= 11'd1000; m4 <= 11'd1000;
            in_armed  <= 1'b0;
            in_thr    <= 11'd0;
            e_w <= 0; accraw_w <= 0; dfnew_w <= 0; p_w <= 0; i_w <= 0; u_w <= 0;
            mul_a <= 0; mul_b <= 0;
            for (k = 0; k < 3; k = k + 1) begin
                in_sp[k] <= 0; in_mea[k] <= 0;
                acc_r[k] <= 0; prev_r[k] <= 0; dfilt_r[k] <= 0; mix_r[k] <= 0;
            end
        end else begin
            out_valid <= 1'b0;
            case (state)
            S_IDLE: begin
                if (clear) begin
                    for (k = 0; k < 3; k = k + 1) begin
                        acc_r[k] <= 0; prev_r[k] <= 0; dfilt_r[k] <= 0; mix_r[k] <= 0;
                    end
                end else if (sample_valid) begin
                    in_armed  <= armed;
                    in_thr    <= throttle;
                    in_sp[0]  <= sp_roll;  in_mea[0] <= roll;
                    in_sp[1]  <= sp_pitch; in_mea[1] <= pitch;
                    in_sp[2]  <= sp_yaw;   in_mea[2] <= gz;
                    if (gated_in) begin
                        // chua arm / ga thap: motor ve 1000, PID giu nguyen trang thai
                        m1 <= 11'd1000; m2 <= 11'd1000; m3 <= 11'd1000; m4 <= 11'd1000;
                        out_valid <= 1'b1;
                    end else begin
                        axis  <= 2'd0;
                        state <= S_LOAD;
                    end
                end
            end
            S_LOAD: begin
                e_w      <= e_cur;
                accraw_w <= accraw_cur;
                mul_a    <= ALPHA;
                mul_b    <= diff_cur;
                state    <= S_FILT;
            end
            S_FILT: begin
                dfnew_w <= dfilt_r[axis] + shr(prod, FA);
                mul_a   <= kp_m(axis);
                mul_b   <= e_w;
                state   <= S_P;
            end
            S_P: begin
                p_w   <= shr(prod, sh_p(axis));
                mul_a <= ki_m(axis);
                mul_b <= accraw_w;
                state <= S_I;
            end
            S_I: begin
                i_w   <= shr(prod, sh_i(axis));
                mul_a <= kd_m(axis);
                mul_b <= dfnew_w;
                state <= S_D;
            end
            S_D: begin
                u_w   <= p_w + i_w + shr(prod, sh_d(axis));
                state <= S_SAT;
            end
            S_SAT: begin
                if (!u_hi && !u_lo)
                    acc_r[axis] <= acc_clamped;      // anti-windup: chi tich phan khi khong bao hoa
                prev_r[axis]  <= e_w;
                dfilt_r[axis] <= dfnew_w;
                mix_r[axis]   <= mix_new;
                if (axis == 2'd2) begin
                    state <= S_MIX;
                end else begin
                    axis  <= axis + 2'd1;
                    state <= S_LOAD;
                end
            end
            S_MIX: begin
                m1 <= motor_clamp(t_s + p_s + r_s - y_s);
                m2 <= motor_clamp(t_s + p_s - r_s + y_s);
                m3 <= motor_clamp(t_s - p_s - r_s - y_s);
                m4 <= motor_clamp(t_s - p_s + r_s + y_s);
                out_valid <= 1'b1;
                state     <= S_IDLE;
            end
            default: state <= S_IDLE;
            endcase
        end
    end

endmodule
