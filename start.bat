cd /d "%~dp0"

@echo off
set /p choice= "Please choose between id-tag as ID [1] or ink-scape-label as ID [2]"

"%~dp0venv\Scripts\python.exe" "%~dp0svg_to_kml_1.py"
ECHO DONE
pause