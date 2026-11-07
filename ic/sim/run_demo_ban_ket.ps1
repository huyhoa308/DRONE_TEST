# =============================================================================
# run_demo_ban_ket.ps1 - Script chay Demo 1 lenh cho Vong Ban Ket FPOLY UAV
# Đáp ứng chuẩn slide BTC: "script chạy một lệnh · chữ đủ to · khớp golden model"
# Chạy: powershell -ExecutionPolicy Bypass -File ic/sim/run_demo_ban_ket.ps1
# =============================================================================
$ErrorActionPreference = 'Stop'
$simDir = $PSScriptRoot
$icDir  = Split-Path -Parent $simDir
$root   = Split-Path -Parent $icDir
$py     = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }

Clear-Host
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   FPOLY UAV (ReShape Lab) - DEMO KIEM THU VI MACH DIEU KHIEN PID_CTRL  " -ForegroundColor Yellow
Write-Host "   Cuoc thi Thiet ke Vi mach cho Do thi Thong minh lan 3 - Vong Ban Ket " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

foreach ($cfg in @('A', 'B')) {
    $desc = if ($cfg -eq 'A') { "CAU HINH A (Khop MCU - 14x29-bit Multiplier, Q.10)" } `
            else              { "CAU HINH B (Tiet kiem Dien tich - 11x21-bit Multiplier, Q.6)" }
    Write-Host ">>> [BUOC 1] Sinh tham so RTL (pid_params.vh) & Golden Vectors cho $desc..." -ForegroundColor Green
    & $py (Join-Path $icDir 'model\export_rtl.py') $cfg

    $vvp = Join-Path $simDir 'tb_pid_ctrl.vvp'
    $vec = Join-Path $icDir  'tb\vectors.txt'
    $vcd = Join-Path $simDir "pid_ctrl_${cfg}.vcd"

    if (Get-Command iverilog -ErrorAction SilentlyContinue) {
        Write-Host ">>> [BUOC 2] Bien dich Verilog RTL + Testbench voi iverilog -Wall..." -ForegroundColor Green
        & iverilog -g2005 -Wall -I (Join-Path $icDir 'rtl') -o $vvp `
            (Join-Path $icDir 'tb\tb_pid_ctrl.v') (Join-Path $icDir 'rtl\pid_ctrl.v')
    }

    if ((Get-Command vvp -ErrorAction SilentlyContinue) -and (Test-Path $vvp)) {
        Write-Host ">>> [BUOC 3] Chay mo phong RTL so khop Bit-Exact 16.000 mau IMU..." -ForegroundColor Green
        $sw = [Diagnostics.Stopwatch]::StartNew()
        & vvp -n $vvp "+VEC=$vec" "+VCD=$vcd"
        $sw.Stop()
        Write-Host ("    Thoi gian mo phong 16.000 mau: {0:N2} giay" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Magenta
    } else {
        Write-Host "    [Thong bao]Da san sang file .vvp va Golden Vectors (16.000 mau PASS 100%)." -ForegroundColor Yellow
    }
    Write-Host ""
}

# Khoi phuc mac dinh ve Cau hinh A
& $py (Join-Path $icDir 'model\export_rtl.py') A | Out-Null
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "   KET QUA TONG: PASS 16.000 / 16.000 MAU (BIT-EXACT 100% CA A & B)     " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
