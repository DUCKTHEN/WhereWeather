@echo off
setlocal
cd /d "%~dp0"

python -m PyInstaller ^
  --clean ^
  --onefile ^
  --windowed ^
  --name WhereWeather ^
  --icon "assets\chick_icon.ico" ^
  --add-data "assets;assets" ^
  --add-data "fonts;fonts" ^
  "where_weather.py"

if errorlevel 1 exit /b %errorlevel%

copy /Y "RELEASE_README.md" "dist\README.md" >nul
copy /Y "config.example.json" "dist\config.example.json" >nul
copy /Y "openweather_api_key.example.bat" "dist\openweather_api_key.example.bat" >nul

echo.
echo Build complete: dist\WhereWeather.exe
