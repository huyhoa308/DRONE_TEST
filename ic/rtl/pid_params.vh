// Tu dong sinh boi ic/model/export_rtl.py - KHONG sua tay, sua mo hinh roi chay lai.
// Cau hinh A: fe=10 wk=13 fa=13 fd=4 fu=9 rnd=1, dt = 2.5 ms
// Dau vao sp_*/roll/pitch/gz: so nguyen co dau Q.FE (do, do/s). Dau ra motor: us.

localparam integer FE     = 10;
localparam integer FD     = 4;
localparam integer FA     = 13;
localparam integer FU     = 9;
localparam integer ROUND  = 1;

localparam integer W_IN   = 22;
localparam integer W_E    = 23;
localparam integer W_ACC  = 27;
localparam integer W_DE   = 28;
localparam integer W_DF   = 28;
localparam integer W_DIFF = 29;
localparam integer W_MA   = 14;
localparam integer W_MB   = 29;
localparam integer W_P    = 43;
localparam integer W_U    = 28;

localparam integer ALPHA   = 1638;       // 0.2 * 2^FA
localparam integer ACC_LIM = 40960000;  // 100.0/dt * 2^FE
localparam integer U_LIM   = 128000;     // 250 * 2^FU

localparam integer KP_M0  = 7373;  localparam integer SH_P0 = 13;  // roll KP' = 1.8
localparam integer KI_M0  = 5033;  localparam integer SH_I0 = 25;  // roll KI' = 0.0003
localparam integer KD_M0  = 4608;  localparam integer SH_D0 = 12;  // roll KD' = 36
localparam integer MIX_LIM0 = 250;
localparam integer KP_M1  = 7496;  localparam integer SH_P1 = 13;  // pitch KP' = 1.83
localparam integer KI_M1  = 5159;  localparam integer SH_I1 = 25;  // pitch KI' = 0.0003075
localparam integer KD_M1  = 4608;  localparam integer SH_D1 = 12;  // pitch KD' = 36
localparam integer MIX_LIM1 = 250;
localparam integer KP_M2  = 7987;  localparam integer SH_P2 = 12;  // yaw KP' = 3.9
localparam integer KI_M2  = 0;  localparam integer SH_I2 = 1;  // yaw KI' = 0
localparam integer KD_M2  = 0;  localparam integer SH_D2 = 5;  // yaw KD' = 0
localparam integer MIX_LIM2 = 80;
