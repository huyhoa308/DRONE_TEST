# Mo phong pid_ctrl bang ModelSim/Questa. Trong thu muc ic/sim:
#   vsim -c -do run_modelsim.do
vlib work
vlog -lint +incdir+../rtl ../rtl/pid_ctrl.v ../tb/tb_pid_ctrl.v
vsim -c tb_pid_ctrl +VEC=../tb/vectors.txt
run -all
quit -f
