// =============================================================================
// Lab 01 - BAI TAP: dung CHI cong nand2_cmos de tao cac cong con lai
//
// Luat: trong moi module chi duoc dat cac instance "nand2_cmos" (hoac module ban
// da lam xong o tren). Khong dung assign, &, |, ^, ~.
// Chay thu: sh course/labs/01_cmos/run.sh   -> PASS la xong.
// Xong thi dem: moi cong cua ban ton bao nhieu transistor (moi NAND2 = 4)?
// =============================================================================
`timescale 1ns / 1ps

// Vi du da lam san: NOT(a) = NAND(a, a)  -> 1 NAND = 4 transistor
module not_n (output y, input a);
    nand2_cmos g1 (y, a, a);
endmodule

// TODO 1: AND(a, b). Goi y: AND la NAND roi dao lai.
module and_n (output y, input a, input b);
    // viet o day
endmodule

// TODO 2: OR(a, b). Goi y: dinh ly De Morgan  a OR b = NOT( NOT a AND NOT b ).
module or_n (output y, input a, input b);
    // viet o day
endmodule

// TODO 3: XOR(a, b). Lam duoc voi 4 NAND. Goi y: tinh t = NAND(a, b) truoc,
// roi dung t o ca hai nhanh.
module xor_n (output y, input a, input b);
    // viet o day
endmodule

// TODO 4: NOR(a, b). Dung lai cac module ban vua lam.
module nor_n (output y, input a, input b);
    // viet o day
endmodule
