@echo off

call env\Scripts\activate
cd %~dp0bot

set TOKEN=your telegram token

python main.py

pause