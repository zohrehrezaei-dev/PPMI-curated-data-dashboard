@echo off
echo Starting PPMI Dashboard...
cd /d "G:\Train\Parkinson PPMI\curated data dashboard"
py -3.11 -m streamlit run src/ppmi_dashboard.py
pause