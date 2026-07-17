@echo off
REM Builds dist\BO2EmblemToolkit.exe - a single file with Python and all
REM dependencies bundled in. Only needed if you want to produce that exe
REM yourself instead of downloading it from the Releases page.
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller
pyinstaller --onefile --name BO2EmblemToolkit ^
  --add-data "reference_shapes;reference_shapes" ^
  --add-data "emblemtool/web/static;emblemtool/web/static" ^
  --add-data "LICENSE;." ^
  run.py
echo.
echo Built dist\BO2EmblemToolkit.exe
pause
