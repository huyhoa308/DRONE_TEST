# =============================================================================
# syn_genus.tcl - Script Tong hop Logic (Synthesis) & STA tren Cadence Genus
# Nhom FPOLY UAV - Cuoc thi Thiet ke vi mach cho Do thi thong minh lan 3
#
# Huong dan chay tren server Cadence cua cuoc thi:
#   1. Dat PDK_LIB tro toi file .lib (liberty) cua PDK tren server
#   2. Chay MOT LAN CHO MOI CORNER, vi du:
#        PDK_LIB=/pdk/slow.lib    CORNER=SS genus -f ic/syn/syn_genus.tcl   (setup, worst case)
#        PDK_LIB=/pdk/typical.lib CORNER=TT genus -f ic/syn/syn_genus.tcl   (bao cao PPA chinh)
#      Hold kiem o corner FF sau CTS tren Innovus (MMMC), khong o buoc nay.
#   3. Tuy chon TOP=spi_pid_wrapper de tong hop ca vo SPI (mac dinh TOP=pid_ctrl)
#   4. Doc ket qua dien vao Bang so sanh (Slide 7) trong ic/syn/reports/<TOP>_<CORNER>_*.rpt
# =============================================================================

# --- 1. Cau hinh duong dan PDK & RTL ---
set DESIGN       [expr {[info exists ::env(TOP)]    ? $::env(TOP)    : "pid_ctrl"}]
set CORNER       [expr {[info exists ::env(CORNER)] ? $::env(CORNER) : "SS"}]
set RTL_DIR      "../rtl"
set REPORT_DIR   "./reports"
set OUTPUT_DIR   "./outputs"

file mkdir $REPORT_DIR
file mkdir $OUTPUT_DIR

# Thay duong dan .lib ben duoi bang duong dan PDK tren server Cadence (vd: gpdk045 / tsmc180 / sky130)
if {[info exists ::env(PDK_LIB)]} {
    set LIB_FILES $::env(PDK_LIB)
} else {
    puts "INFO: Hay dat bien moi truong PDK_LIB hoac sua LIB_FILES trong syn_genus.tcl"
    set LIB_FILES "/path/to/pdk/timing/slow.lib"
}

set_db init_lib_search_path [list [file dirname $LIB_FILES]]
set_db init_hdl_search_path [list $RTL_DIR]
set_db library $LIB_FILES

# --- 2. Doc RTL Verilog (pid_ctrl.v + pid_params.vh) ---
read_hdl -v2001 [list "${RTL_DIR}/pid_ctrl.v" "${RTL_DIR}/spi_pid_wrapper.v"]
elaborate $DESIGN
check_design -unresolved

# --- 3. Rang buoc Timing (Constraints) o 10 MHz (chu ky 100 ns) ---
# Co the doi PERIOD_NS xuong 10.0 (100 MHz) hoac 5.0 (200 MHz) de tim Fmax
set PERIOD_NS 100.0
create_clock -name clk -period $PERIOD_NS [get_ports clk]
set_clock_uncertainty 0.2 [get_clocks clk]
set_input_delay  -clock clk [expr {$PERIOD_NS * 0.2}] [remove_from_collection [all_inputs] [get_ports clk]]
set_output_delay -clock clk [expr {$PERIOD_NS * 0.2}] [all_outputs]

# --- 4. Tong hop Logic (Generic -> Mapped -> Incremental) ---
# Chen clock gating tu dong (ICG): FSM o S_IDLE 99.92% thoi gian
set_db lp_insert_clock_gating true
syn_generic
syn_map
syn_opt

# --- 5. Xuat bao cao PPA (Area, Power, Timing, Gate Count) cho Slide 7 ---
report_area   > "${REPORT_DIR}/${DESIGN}_${CORNER}_area.rpt"
report_power  > "${REPORT_DIR}/${DESIGN}_${CORNER}_power.rpt"
report_timing -max_paths 10 > "${REPORT_DIR}/${DESIGN}_${CORNER}_timing.rpt"
report_qor    > "${REPORT_DIR}/${DESIGN}_${CORNER}_qor.rpt"
report_gates  > "${REPORT_DIR}/${DESIGN}_${CORNER}_gates.rpt"
report_clock_gating > "${REPORT_DIR}/${DESIGN}_${CORNER}_clock_gating.rpt"

# --- 6. Xuat Netlist & SDC sang Cadence Innovus (Place & Route) ---
write_hdl > "${OUTPUT_DIR}/${DESIGN}_${CORNER}_netlist.v"
write_sdc > "${OUTPUT_DIR}/${DESIGN}.sdc"
write_sdf -timescale ns -nonegchecks -recrem split -edges check_edge > "${OUTPUT_DIR}/${DESIGN}.sdf"

puts "=================================================================="
puts " HOAN TAT SYNTHESIS CHO $DESIGN (corner $CORNER)!"
puts " Xem so lieu Area (mm2), Power (mW), Timing (Slack) tai: $REPORT_DIR"
puts "=================================================================="
exit
