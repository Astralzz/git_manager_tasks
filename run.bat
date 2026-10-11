@echo off
REM Force the console to use UTF-8 so that emojis display correctly
chcp 65001 >nul
REM This batch file is used to manage Git tasks for the project.

echo Git Manager Tasks starting ⌛...

REM Open the project directory
cd /d "C:\Users\dayin\OneDrive\Documentos\1_Proyectos\git-personal\10_Scripts\python\my_projects\git_manager_tasks"

REM Check if Git is installed
git --version >nul 2>&1

REM If Git is not installed, display an error message and exit
if errorlevel 1 (
  echo Git is not installed. Please install Git and try again. 🟥
  exit /b 1
)

REM Run main.py script
python main.py

REM Check if the main.py script ran successfully
if errorlevel 1 (
  echo An error occurred while running main.py. Please check the script for issues. 🟥
  exit /b 1
)

REM If everything is successful, pause the script to allow the user to see the output
pause

echo Git Manager Tasks completed successfully ✅.
exit /b 0
