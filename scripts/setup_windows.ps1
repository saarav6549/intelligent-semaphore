# PowerShell Setup Script for Windows
# Run this on your Windows machine to set up the development environment

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Team B Setup - Windows Environment          " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}

# Check Git
Write-Host "Checking Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git not found. Please install Git from git-scm.com" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "✓ venv already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ venv created" -ForegroundColor Green
}

# Activate venv and install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "`n✓ Dependencies installed" -ForegroundColor Green

# Initialize Git if needed
Write-Host "`nChecking Git repository..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "✓ Git already initialized" -ForegroundColor Green
} else {
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
}

# Create .gitignore if it doesn't exist
if (!(Test-Path ".gitignore")) {
    Write-Host "✗ .gitignore not found (should exist)" -ForegroundColor Yellow
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!                              " -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Read START_HERE.md for complete guide"
Write-Host "2. Edit config files in config/ folder"
Write-Host "3. Push to GitHub:"
Write-Host "   git add ."
Write-Host "   git commit -m 'Initial setup'"
Write-Host "   git remote add origin https://github.com/[USERNAME]/intelligent-semaphore.git"
Write-Host "   git push -u origin main"
Write-Host ""
Write-Host "4. Deploy to RunPod: See docs/RUNPOD_SETUP.md"
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Green
