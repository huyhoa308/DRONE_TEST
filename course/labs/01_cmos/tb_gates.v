// =============================================================================
// Testbench Lab 01 - thu moi to hop dau vao, so voi dap an, in bang chan ly
// Chay: sh course/labs/01_cmos/run.sh
// =============================================================================
`timescale 1ns / 1ps

module tb_gates;
    reg a, b;
    wire y_not, y_and, y_or, y_xor, y_nor;
    integer i, errors;

    not_n  u_not (.y(y_not), .a(a));
    and_n  u_and (.y(y_and), .a(a), .b(b));
    or_n   u_or  (.y(y_or),  .a(a), .b(b));
    xor_n  u_xor (.y(y_xor), .a(a), .b(b));
    nor_n  u_nor (.y(y_nor), .a(a), .b(b));

    task check(input [8*4-1:0] name, input got, input want);
        if (got !== want) begin
            errors = errors + 1;
            $display("  SAI %0s: a=%b b=%b -> ra %b, dung phai la %b", name, a, b, got, want);
        end
    endtask

    initial begin
        errors = 0;
        $display(" a b | NOT(a) AND OR XOR NOR");
        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #10;
            $display(" %b %b |   %b     %b   %b   %b   %b", a, b, y_not, y_and, y_or, y_xor, y_nor);
            check("NOT", y_not, ~a);
            check("AND", y_and, a & b);
            check("OR",  y_or,  a | b);
            check("XOR", y_xor, a ^ b);
            check("NOR", y_nor, ~(a | b));
        end
        if (errors == 0) $display("PASS: ca 5 cong dung voi moi to hop dau vao");
        else             $display("FAIL: %0d loi (gia tri z = chua noi day, x = hai nhanh tranh nhau)", errors);
        $finish;
    end
endmodule
