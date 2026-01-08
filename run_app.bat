@echo off
TITLE Miso SMS System
ECHO Starting Miso SMS Application...
ECHO.

:: Change directory to the script location to ensure relative paths work
cd /d "%~dp0"

:: Run the Python application
python MISOPROJ\MISOPROJ.py

:: Pause so the window doesn't close immediately if it crashes
PAUSE
