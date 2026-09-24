# Doi SVG -> PNG (do phan giai x2) bang Microsoft Edge headless, cho tai lieu Word/PDF.
# Chay: powershell -ExecutionPolicy Bypass -File ic/doc/svg2png.ps1
$ErrorActionPreference = 'Continue'   # Edge in canh bao vo hai ra stderr
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$out = Join-Path $PSScriptRoot 'png'
New-Item -ItemType Directory -Force $out | Out-Null
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$svgs = @(
    'ic/doc/figs/design_flow.svg', 'ic/doc/figs/block_diagram.svg', 'ic/doc/figs/fsm_timeline.svg',
    'ic/model/out/step_roll.svg', 'docs/wiring_s3.svg', 'docs/wiring_devkit.svg', 'docs/wiring_drone.svg'
)
foreach ($rel in $svgs) {
    $svg = Join-Path $root $rel
    $head = Get-Content $svg -TotalCount 3 -Encoding UTF8 | Out-String
    if ($head -notmatch 'viewBox="0 0 (\d+(\.\d+)?) (\d+(\.\d+)?)"') { throw "khong doc duoc kich thuoc: $rel" }
    $w = [int][math]::Ceiling([double]$Matches[1]); $h = [int][math]::Ceiling([double]$Matches[3])
    $png = Join-Path $out ([IO.Path]::GetFileNameWithoutExtension($svg) + '.png')
    $uri = 'file:///' + ($svg -replace '\\', '/')
    $tmp = Join-Path $env:TEMP ('edge-svg2png-' + [guid]::NewGuid())
    & $edge --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$tmp" `
        --force-device-scale-factor=2 --window-size="$w,$h" --screenshot="$png" $uri 2>$null | Out-Null
    Start-Sleep -Milliseconds 300
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    if (-not (Test-Path $png)) { throw "Edge khong tao duoc $png" }
    "{0,-22} {1}x{2} -> {3:N0} KB" -f ([IO.Path]::GetFileName($png)), $w, $h, ((Get-Item $png).Length / 1KB)
}
