@echo off
echo ========================================
echo Instalando dependencias del proyecto...
echo ========================================

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

echo Python encontrado. Instalando dependencias...

REM Instalar dependencias desde requirements.txt
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Hubo un problema al instalar las dependencias
    pause
    exit /b 1
)

echo ========================================
echo ¡Dependencias instaladas correctamente!
echo ========================================
echo.
echo Para ejecutar el proyecto:
echo python main.py
echo.
pause 