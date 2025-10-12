# Stop PPMI Dashboard PowerShell Script
Write-Host "Stopping PPMI Dashboard..." -ForegroundColor Yellow
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Write-Host "Dashboard stopped." -ForegroundColor Green