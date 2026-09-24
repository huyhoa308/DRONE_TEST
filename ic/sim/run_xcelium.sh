#!/usr/bin/env sh
# Mo phong pid_ctrl bang Cadence Xcelium (server Cadence cua cuoc thi). Chay tu thu muc goc repo:
#   sh ic/sim/run_xcelium.sh
set -e
cd "$(dirname "$0")"
xrun -64bit -access +rwc -incdir ../rtl ../tb/tb_pid_ctrl.v ../rtl/pid_ctrl.v +VEC=../tb/vectors.txt
