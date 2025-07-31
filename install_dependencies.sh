#!/bin/bash

echo "========================================"
echo "Instalando dependencias del proyecto..."
echo "========================================"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 no está instalado"
    exit 1
fi

echo "Python encontrado. Instalando dependencias..."

# Instalar dependencias desde requirements.txt
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Hubo un problema al instalar las dependencias"
    exit 1
fi

echo "========================================"
echo "¡Dependencias instaladas correctamente!"
echo "========================================"
echo ""
echo "Para ejecutar el proyecto:"
echo "python3 main.py"
echo "" 