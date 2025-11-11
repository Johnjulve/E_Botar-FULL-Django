$ErrorActionPreference = 'Stop'

function Ensure-Dir($path) {
    if (-not (Test-Path $path)) { New-Item -ItemType Directory -Path $path | Out-Null }
}

function Get-File($url, $dest) {
    if (Test-Path $dest) { Write-Host "Exists: $dest"; return }
    Write-Host "Downloading: $url -> $dest"
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $root
$staticRoot = Join-Path $projectRoot 'static'

$bootstrapCssDir = Join-Path $staticRoot 'vendor/bootstrap/css'
$bootstrapJsDir  = Join-Path $staticRoot 'vendor/bootstrap/js'
$faCssDir        = Join-Path $staticRoot 'vendor/fontawesome/css'
$faFontsDir      = Join-Path $staticRoot 'vendor/fontawesome/webfonts'
$chartsDir       = Join-Path $staticRoot 'vendor/chartjs'

Ensure-Dir $bootstrapCssDir
Ensure-Dir $bootstrapJsDir
Ensure-Dir $faCssDir
Ensure-Dir $faFontsDir
Ensure-Dir $chartsDir

# Bootstrap 5.3.0
$bootstrapCssUrl = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
$bootstrapJsUrl  = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
Get-File $bootstrapCssUrl (Join-Path $bootstrapCssDir 'bootstrap.min.css')
Get-File $bootstrapJsUrl  (Join-Path $bootstrapJsDir  'bootstrap.bundle.min.js')

# Font Awesome 6.0.0 (CSS + core webfonts frequently referenced)
$faCssUrl = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
Get-File $faCssUrl (Join-Path $faCssDir 'all.min.css')

$faBase = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/webfonts'
$fonts = @(
  'fa-solid-900.woff2',
  'fa-regular-400.woff2',
  'fa-brands-400.woff2'
)
foreach ($f in $fonts) {
  Get-File ("$faBase/$f") (Join-Path $faFontsDir $f)
}

# Chart.js 4.x
$chartJsUrl = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js'
Get-File $chartJsUrl (Join-Path $chartsDir 'chart.umd.min.js')

Write-Host "Offline assets prepared under: $staticRoot\vendor"

