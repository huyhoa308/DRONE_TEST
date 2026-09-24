#!/usr/bin/env sh
# Mo phong pid_ctrl bang Icarus Verilog (mien phi). Chay tu thu muc goc repo:
#   sh ic/sim/run_iverilog.sh
set -e
cd "$(dirname "$0")"
iverilog -g2005 -Wall -I ../rtl -o tb_pid_ctrl.vvp ../tb/tb_pid_ctrl.v ../rtl/pid_ctrl.v
vvp -n tb_pid_ctrl.vvp +VEC=../tb/vectors.txt
