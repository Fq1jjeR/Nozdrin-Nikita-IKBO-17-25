@echo off
REM
REM
REM
REM
REM
REM
REM
REM
REM

setlocal enableextensions

if "%~1"=="" (
    echo Использование: %0 ^<выходной_файл.yaml^> 1>&2
    exit /b 2
)

python "%~dp0run.py" -o "%~1"
endlocal & exit /b %errorlevel%
