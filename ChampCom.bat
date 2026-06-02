@echo off
REM ChampCom - Double-click to launch on Windows
REM No terminal window will appear
cd /d "%~dp0"
pythonw main.py
exit /b %ERRORLEVEL%
