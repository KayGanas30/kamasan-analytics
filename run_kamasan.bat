@echo off
title Kamasan Analytics Launcher
echo ===================================================
echo   KAMASAN ANALYTICS - Tajam Menganalisis
echo ===================================================
echo.
echo Menyiapkan lingkungan...
call venv\Scripts\activate.bat
echo.
echo Membuka aplikasi di browser...
python -m streamlit run app.py
pause