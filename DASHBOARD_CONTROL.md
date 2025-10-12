# PPMI Dashboard Control Guide

## 🚀 How to Start/Stop the Dashboard

### Method 1: VS Code Tasks (Recommended)
1. **Start**: Press `Ctrl+Shift+P` → Type "Run Task" → Select "Start PPMI Dashboard"
2. **Stop**: Press `Ctrl+Shift+P` → Type "Run Task" → Select "Stop PPMI Dashboard"
3. **Restart**: Press `Ctrl+Shift+P` → Type "Run Task" → Select "Restart PPMI Dashboard"

### Method 2: Batch Scripts (Windows)
- **Start**: Double-click `start_dashboard.bat`
- **Stop**: Double-click `stop_dashboard.bat`

### Method 3: PowerShell Scripts
- **Start**: Right-click `start_dashboard.ps1` → "Run with PowerShell"
- **Stop**: Right-click `stop_dashboard.ps1` → "Run with PowerShell"

### Method 4: Manual Terminal Commands
```powershell
# Start Dashboard
cd "G:\Train\Parkinson PPMI\curated data dashboard"
py -3.11 -m streamlit run src/ppmi_dashboard.py

# Stop Dashboard (in another terminal or Ctrl+C)
Stop-Process -Name "python" -Force
```

## 📍 Dashboard Access
- **Local URL**: http://localhost:8501
- **Browser**: Opens automatically when started

## 🔧 Quick Controls
- **Keyboard**: `Ctrl+C` in the terminal to stop
- **Browser**: Close the browser tab (dashboard keeps running in background)
- **Force Stop**: Use the stop scripts above

## 📝 Notes
- Dashboard runs in background - close terminal won't stop it
- Use stop scripts to properly terminate the process
- Restart if you make code changes to see updates