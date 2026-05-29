@echo off
if exist "%~dp0openweather_api_key.bat" call "%~dp0openweather_api_key.bat"
start "" pythonw "%~dp0where_weather.py"
