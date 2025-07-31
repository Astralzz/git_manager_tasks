# Git Manager - Gestor de Repositorios Git

## 📌 Contacto  

📌 **Portafolio:** [astralzz.io](https://astralzz.github.io/)  
📩 **Email:** [edain.cortez@outlook.com](mailto:edain.cortez@outlook.com)  
🔗 **LinkedIn:** [linkedin.com/in/Edain](https://www.linkedin.com/in/edain-jcc)  
😺 **GitHub:** [github.com/Astralzz](https://github.com/Astralzz)  

## 🎯 Propósito y Descripción

**Git Manager** es una herramienta de línea de comandos desarrollada en Python diseñada para simplificar y automatizar la gestión de múltiples repositorios Git. Esta herramienta está especialmente optimizada para desarrolladores que trabajan con múltiples proyectos simultáneamente, facilitando tareas comunes como:

- **Gestión centralizada** de múltiples repositorios Git
- **Automatización** de operaciones repetitivas (pull, push, commit, etc.)
- **Organización** de repositorios por proyectos, tickets y secciones
- **Monitoreo** del estado de todos los repositorios desde una interfaz unificada
- **Facilitación** del flujo de trabajo en equipos de desarrollo

### 🎯 Casos de Uso Principales

- **Desarrolladores full-stack** que manejan múltiples proyectos
- **Equipos de desarrollo** que trabajan con microservicios
- **DevOps engineers** que necesitan gestionar múltiples repositorios
- **Freelancers** que trabajan en varios proyectos simultáneamente
- **Arquitectos de software** que supervisan múltiples repositorios

## 📋 Requisitos Previos

### Software Requerido

- **Python 3.7 o superior** - [Descargar Python](https://python.org)
- **Git 2.20 o superior** - [Descargar Git](https://git-scm.com)
- **Sistema operativo**: Windows, macOS, o Linux

### Verificación de Instalación

```bash
# Verificar Python
python --version

# Verificar Git
git --version

# Verificar pip
pip --version
```

## 🚀 Instalación y Configuración

### Método 1: Instalación Automática (Recomendado)

#### Windows

```cmd
# Ejecutar el script de instalación automática
.\install_dependencies.bat
```

#### Linux/macOS

```bash
# Dar permisos de ejecución al script
chmod +x install_dependencies.sh

# Ejecutar el script de instalación automática
./install_dependencies.sh
```

### Método 2: Instalación Manual

```bash
# Clonar o descargar el proyecto
cd git_manager_tasks

# Instalar dependencias de Python
pip install -r requirements.txt

# Verificar la instalación
python main.py --help
```

## 📦 Dependencias del Proyecto

### Dependencias Principales

| Dependencia       | Versión | Propósito                                       |
| ----------------- | ------- | ----------------------------------------------- |
| **python-dotenv** | ^1.0.0  | Gestión de variables de entorno y configuración |
| **colorama**      | ^0.4.6  | Colores y formato en consola para mejor UX      |

### Dependencias del Sistema

- **Git**: Para operaciones de control de versiones
- **Python**: Runtime del lenguaje de programación

## ⚙️ Configuración Detallada

### 1. Archivo de Configuración Principal (`config.json`)

Este archivo contiene la configuración central de todos tus repositorios:

```json
{
   [
    {
      "number": 1,
      "id": "TKT-1234-5678",
      "name": "Implementación de autenticación OAuth2",
      "task": "TKT-1234",
      "section": "BACKEND",
      "project": "api-gateway",
      "repo_path": "C:/Projects/api-gateway",
      "base_branch": "main",
      "feature_branch": "feature/oauth2-auth"
    }
  ],
}
```

#### Campos de Configuración

| Campo            | Tipo    | Descripción                                    | Requerido |
| ---------------- | ------- | ---------------------------------------------- | --------- |
| `number`         | Integer | Número secuencial del repositorio              | ✅        |
| `id`             | String  | Identificador único del ticket/tarea           | ✅        |
| `name`           | String  | Descripción detallada del proyecto             | ✅        |
| `task`           | String  | Código del ticket (ej: TKT-1234)               | ✅        |
| `section`        | String  | Sección del proyecto (FRONTEND, BACKEND, etc.) | ✅        |
| `project`        | String  | Nombre del proyecto                            | ✅        |
| `repo_path`      | String  | Ruta absoluta al repositorio                   | ✅        |
| `base_branch`    | String  | Rama principal (main, master, develop)         | ✅        |
| `feature_branch` | String  | Rama de características                        | ❌        |

### 2. Variables de Entorno (`.env`)

Archivo opcional para configuraciones sensibles:

```env
# Configuración de rutas
BASE_PATH=C:/Projects
BACKUP_PATH=C:/Backups

# Configuración de seguridad
PASS_SENSITIVE=tu_contraseña_segura

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=git_manager.log

# Configuración de Git
GIT_USER_NAME=Tu Nombre
GIT_USER_EMAIL=tu.email@ejemplo.com
```

## 🎯 Uso y Funcionalidades

### Ejecución Básica

```bash
# Ejecutar el programa principal
python main.py

# Ejecutar con argumentos específicos
python main.py --repo 1 --action pull
python main.py --project api-gateway --action status
```

### Comandos Disponibles

| Comando    | Descripción                    | Ejemplo                            |
| ---------- | ------------------------------ | ---------------------------------- |
| `status`   | Mostrar estado de repositorios | `python main.py --action status`   |
| `pull`     | Actualizar repositorios        | `python main.py --action pull`     |
| `push`     | Subir cambios                  | `python main.py --action push`     |
| `commit`   | Crear commit                   | `python main.py --action commit`   |
| `checkout` | Cambiar rama                   | `python main.py --action checkout` |
| `merge`    | Fusionar ramas                 | `python main.py --action merge`    |

### Opciones de Filtrado

```bash
# Operar en un repositorio específico
python main.py --repo 1 --action pull

# Operar en todos los repositorios de un proyecto
python main.py --project api-gateway --action status

# Operar en repositorios de una sección
python main.py --section BACKEND --action pull
```

## 📁 Estructura del Proyecto

```bash
git_manager_tasks/
├── 📄 main.py                    # Punto de entrada principal
├── 📄 config.json               # Configuración de repositorios
├── 📄 requirements.txt          # Dependencias de Python
├── 📄 .env                      # Variables de entorno (opcional)
├── 📄 install_dependencies.bat  # Script de instalación Windows
├── 📄 install_dependencies.sh   # Script de instalación Unix
├── 📁 consts/
│   └── 📄 env.py               # Configuración de variables de entorno
├── 📁 classes/
│   ├── 📄 GitClass.py          # Clase principal para operaciones Git
│   ├── 📄 JsonClass.py         # Clase para manejo de archivos JSON
│   └── 📄 ConsoleColors.py     # Clase para colores en consola
├── 📁 logs/                    # Directorio de logs
│   ├── 📄 git_manager.log      # Log principal
│   └── 📄 error.log           # Log de errores
└── 📁 docs/                    # Documentación adicional
    └── 📄 examples.md          # Ejemplos de uso
```

## 🔧 Personalización Avanzada

### Agregar Nuevos Repositorios

1. **Editar `config.json`**:

```json
{
  "number": 4,
  "id": "TKT-5678-9012",
  "name": "Implementación de dashboard administrativo",
  "task": "TKT-5678",
  "section": "FRONTEND",
  "project": "admin-dashboard",
  "repo_path": "C:/Projects/admin-dashboard",
  "base_branch": "develop",
  "feature_branch": "feature/admin-dashboard"
}
```

2. **Verificar la configuración**:

```bash
python main.py --action status --repo 4
```

### Configuración de Logging

```python
# En consts/env.py
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/git_manager.log",
    "max_size": "10MB",
    "backup_count": 5
}
```

## 🐛 Solución de Problemas

### Problemas Comunes

#### Error: "Python no está instalado"

```bash
# Solución: Instalar Python
# Windows: Descargar desde python.org
# Linux: sudo apt-get install python3
# macOS: brew install python3
```

#### Error: "pip no está instalado"

```bash
# Solución: Instalar/actualizar pip
python -m ensurepip --upgrade
```

#### Error: "Módulo no encontrado"

```bash
# Solución: Instalar dependencias
pip install -r requirements.txt
```

#### Error: "Git no está instalado"

```bash
# Solución: Instalar Git
# Windows: Descargar desde git-scm.com
# Linux: sudo apt-get install git
# macOS: brew install git
```

#### Error: "Permisos denegados"

```bash
# Solución: Verificar permisos
# Windows: Ejecutar como administrador
# Linux/macOS: chmod +x install_dependencies.sh
```

### Logs y Debugging

```bash
# Ver logs en tiempo real
tail -f logs/git_manager.log

# Ver solo errores
grep "ERROR" logs/git_manager.log

# Limpiar logs
echo "" > logs/git_manager.log
```

## 📝 Mejores Prácticas

### Configuración de Repositorios

1. **Usar rutas absolutas** en `repo_path`
2. **Mantener nombres descriptivos** en el campo `name`
3. **Organizar por secciones** lógicas (FRONTEND, BACKEND, DEVOPS)
4. **Usar convenciones consistentes** para `task` y `id`

### Seguridad

1. **No incluir credenciales** en `config.json`
2. **Usar variables de entorno** para información sensible
3. **Hacer backup regular** de la configuración
4. **Revisar logs** periódicamente

### Mantenimiento

1. **Actualizar dependencias** regularmente
2. **Revisar configuración** mensualmente
3. **Limpiar logs** antiguos
4. **Documentar cambios** en la configuración

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---
