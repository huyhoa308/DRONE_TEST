# =============================================================================
# run_demo_ban_ket.ps1 - Script chay Demo 1 lenh cho Vong Ban Ket FPOLY UAV
# Đáp ứng chuẩn slide BTC: "script chạy một lệnh · chữ đủ to · khớp golden model"
# Chạy: powershell -ExecutionPolicy Bypass -File ic/sim/run_demo_ban_ket.ps1
#
# Ket qua tong chi bao PASS khi TAT CA cac lan mo phong thuc su in dong "PASS:".
# Thieu iverilog/vvp hoac co bat ky lan nao FAIL -> bao FAIL va thoat ma 1.
# =============================================================================
$ErrorActionPreference = 'Stop'
$simDir = $PSScriptRoot
$icDir  = Split-Path -Parent $simDir
$root   = Split-Path -Parent $icDir
$rtl    = Join-Path $icDir 'rtl'
$tbDir  = Join-Path $icDir 'tb'
$py     = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) { $py = 'python' }

# Tim Icarus Verilog: PATH truoc, roi thu muc cai dat mac dinh
if (-not (Get-Command iverilog -ErrorAction SilentlyContinue)) {
    if (Test-Path 'C:\iverilog\bin\iverilog.exe') { $env:Path = "C:\iverilog\bin;$env:Path" }
}
if (-not (Get-Command iverilog -ErrorAction SilentlyContinue) -or
    -not (Get-Command vvp -ErrorAction SilentlyContinue)) {
    Write-Host "LOI: khong tim thay iverilog/vvp. Cai Icarus Verilog (winget install Icarus.Verilog) roi chay lai." -ForegroundColor Red
    exit 1
}

function Invoke-Sim([string]$title, [string[]]$srcs, [string]$vvp, [string[]]$simArgs) {
    Write-Host ">>> Bien dich $title voi iverilog -Wall..." -ForegroundColor Green
    & iverilog -g2005 -Wall -I $rtl -o $vvp @srcs 2>&1 | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    if ($LASTEXITCODE -ne 0) { Write-Host "    LOI bien dich" -ForegroundColor Red; return $false }
    Write-Host ">>> Chay mo phong $title..." -ForegroundColor Green
    $sw  = [Diagnostics.Stopwatch]::StartNew()
    $out = & vvp -n $vvp @simArgs
    $sw.Stop()
    $out | ForEach-Object {
        if ($_ -match '^PASS:')    { Write-Host "    $_" -ForegroundColor Green }
        elseif ($_ -match 'FAIL|LECH|LOI|FATAL') { Write-Host "    $_" -ForegroundColor Red }
        elseif ($_ -notmatch '\$finish') { Write-Host "    $_" }
    }
    Write-Host ("    Thoi gian mo phong: {0:N2} giay" -f $sw.Elapsed.TotalSeconds) -ForegroundColor Magenta
    return [bool]($out | Where-Object { $_ -match '^PASS:' })
}

Clear-Host
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "   FPOLY UAV (ReShape Lab) - DEMO KIEM THU VI MACH DIEU KHIEN PID_CTRL  " -ForegroundColor Yellow
Write-Host "   Cuoc thi Thiet ke Vi mach cho Do thi Thong minh lan 3 - Vong Ban Ket " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

$results = [ordered]@{}
$vec = Join-Path $tbDir 'vectors.txt'
$coreSrc = @((Join-Path $tbDir 'tb_pid_ctrl.v'), (Join-Path $rtl 'pid_ctrl.v'))

foreach ($cfg in @('B', 'A')) {
    $desc = if ($cfg -eq 'A') { "CAU HINH A (Khop MCU - 14x29-bit Multiplier, Q.10)" } `
            else              { "CAU HINH B (Tiet kiem Dien tich - 11x21-bit Multiplier, Q.6)" }
    Write-Host "=== $desc ===" -ForegroundColor Yellow
    Write-Host ">>> Sinh tham so RTL (pid_params.vh) & Golden Vectors..." -ForegroundColor Green
    & $py (Join-Path $icDir 'model\export_rtl.py') $cfg | Out-Null
    if ($LASTEXITCODE -ne 0) { Write-Host "    LOI sinh tham so" -ForegroundColor Red; $results["Cau hinh $cfg"] = $false; continue }
    $vcd = Join-Path $simDir "pid_ctrl_${cfg}.vcd"
    $results["Cau hinh $cfg (16.000 mau)"] = Invoke-Sim "pid_ctrl cau hinh $cfg" $coreSrc `
        (Join-Path $simDir 'tb_pid_ctrl.vvp') @("+VEC=$vec", "+VCD=$vcd")
    Write-Host ""
}

# Cau hinh A dang duoc nap (vong lap ket thuc o A): kiem thu giao tiep SPI 192 bit
Write-Host "=== GIAO TIEP SPI MODE 0 (spi_pid_wrapper, 100 mau dau, cau hinh A) ===" -ForegroundColor Yellow
$spiSrc = @((Join-Path $tbDir 'tb_spi_pid_wrapper.v'), (Join-Path $rtl 'spi_pid_wrapper.v'), (Join-Path $rtl 'pid_ctrl.v'))
$results["SPI wrapper (100 mau)"] = Invoke-Sim "spi_pid_wrapper" $spiSrc `
    (Join-Path $simDir 'tb_spi_pid_wrapper.vvp') @("+VEC=$vec", "+N=100")
Write-Host ""

$allPass = -not ($results.Values -contains $false)
$color = if ($allPass) { 'Green' } else { 'Red' }
Write-Host "========================================================================" -ForegroundColor $color
foreach ($k in $results.Keys) {
    $tag = if ($results[$k]) { 'PASS' } else { 'FAIL' }
    Write-Host ("   {0,-32} : {1}" -f $k, $tag) -ForegroundColor $color
}
if ($allPass) {
    Write-Host "   KET QUA TONG: PASS - BIT-EXACT 100% (A, B va SPI)" -ForegroundColor Green
} else {
    Write-Host "   KET QUA TONG: FAIL - xem dong mau do o tren" -ForegroundColor Red
}
Write-Host "========================================================================" -ForegroundColor $color
if (-not $allPass) { exit 1 }
