@echo off
cd /d "%~dp0"
Echo Please choose between id-tag as ID [1] or ink-scape-label as ID [2]

@echo off
set /p choice= ""

"%~dp0venv\Scripts\python.exe" "%~dp0svg_to_kml.py" %choice%
ECHO DONE
pause