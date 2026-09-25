#!/usr/bin/env sh
# Chay Lab 01. Tu thu muc goc repo:  sh course/labs/01_cmos/run.sh
set -e
cd "$(dirname "$0")"
export PATH="/c/iverilog/bin:$PATH"     # Icarus cai o C:\iverilog
iverilog -g2005 -Wall -o lab01.vvp cmos_cells.v gates_from_nand.v tb_gates.v
vvp -n lab01.vvp
rm -f lab01.vvp
