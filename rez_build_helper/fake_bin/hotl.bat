@echo off
setlocal enabledelayedexpansion

set "folder=%3%"

echo Executing fake hotl command: %*
echo type nul > "%folder%\hotl.txt"

if not exist "%folder%" mkdir "%folder%"
type nul > "%folder%\hotl.txt"
