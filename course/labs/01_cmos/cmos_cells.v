// =============================================================================
// Lab 01 - Cong CMOS dung tu transistor (cho san, KHONG can sua)
//
// Verilog co san 2 "linh kien" muc transistor:
//   nmos (drain, source, gate);   dan khi gate = 1  (keo xuong GND tot)
//   pmos (drain, source, gate);   dan khi gate = 0  (keo len VDD tot)
// supply1 = nguon VDD, supply0 = GND.
// =============================================================================
`timescale 1ns / 1ps

// Cong NOT (inverter): 1 PMOS len VDD, 1 NMOS xuong GND -> 2 transistor
module inv_cmos (output y, input a);
    supply1 vdd;
    supply0 gnd;
    pmos p1 (y, vdd, a);    // a = 0 -> PMOS dan -> y = 1
    nmos n1 (y, gnd, a);    // a = 1 -> NMOS dan -> y = 0
endmodule

// Cong NAND 2 dau vao: 2 PMOS song song + 2 NMOS noi tiep -> 4 transistor
module nand2_cmos (output y, input a, input b);
    supply1 vdd;
    supply0 gnd;
    wire mid;               // diem giua 2 NMOS noi tiep
    pmos p1 (y, vdd, a);    // chi can a = 0 HOAC b = 0 la y duoc keo len 1
    pmos p2 (y, vdd, b);
    nmos n1 (y, mid, a);    // phai a = 1 VA b = 1 thi y moi bi keo xuong 0
    nmos n2 (mid, gnd, b);
endmodule
