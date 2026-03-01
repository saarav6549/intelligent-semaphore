# Build Docker image locally on Windows
# This is a PowerShell wrapper for build_local.sh

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Building CARLA Vision System Docker Image   " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  WARNING: This will download ~15GB base image!" -ForegroundColor Yellow
Write-Host "    Make sure you have:" -ForegroundColor Yellow
Write-Host "    - 30GB free disk space" -ForegroundColor Yellow
Write-Host "    - Good internet connection" -ForegroundColor Yellow
Write-Host "    - Docker Desktop running" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Continue? (y/n)"
if ($confirmation -ne 'y') {
    exit
}

# Check Docker is running
try {
    docker info | Out-Null
} catch {
    Write-Host "❌ Docker is not running!" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 1/3: Pulling base image (carlasim/carla:0.9.15)..." -ForegroundColor Green
Write-Host "         This will take 10-20 minutes..." -ForegroundColor Yellow
docker pull carlasim/carla:0.9.15

Write-Host ""
Write-Host "Step 2/3: Building our custom image..." -ForegroundColor Green
Write-Host "         This will take 5-10 minutes..." -ForegroundColor Yellow
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
docker build -t intelligent-traffic-teamb:latest -f docker/Dockerfile .
Pop-Location

Write-Host ""
Write-Host "Step 3/3: Verifying image..." -ForegroundColor Green
docker images | Select-String "intelligent-traffic-teamb"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   ✅ Build Complete!                           " -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Image size:"
docker images intelligent-traffic-teamb:latest --format "{{.Size}}"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test locally:" -ForegroundColor Yellow
Write-Host "   .\scripts\test_local.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Push to Docker Hub:" -ForegroundColor Yellow
Write-Host "   .\scripts\push_image.ps1" -ForegroundColor Cyan
Write-Host ""
