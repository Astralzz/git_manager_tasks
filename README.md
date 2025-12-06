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

Este archivo contiene la configuración central de todos tus repositorios, **organizado por secciones** para mejor navegación:

```json
{
  "sections": {
    "URGENTES": {
      "configs": [
        {
          "number": 1,
          "id": "TKT-1234-5678",
          "name": "Implementación de autenticación OAuth2",
          "task": "TKT-1234",
          "section": "URGENTES",
          "project": "api-gateway",
          "repo_path": "C:/Projects/api-gateway",
          "base_branch": "main",
          "feature_branch": "feature/oauth2-auth"
        }
      ]
    },
    "FRONTEND": {
      "configs": [
        {
          "number": 2,
          "id": "TKT-2345-6789",
          "name": "Dashboard administrativo con React",
          "task": "TKT-2345",
          "section": "FRONTEND",
          "project": "admin-dashboard",
          "repo_path": "C:/Projects/admin-dashboard",
          "base_branch": "develop",
          "feature_branch": "feature/dashboard-ui"
        }
      ]
    },
    "BACKEND": {
      "configs": [
        {
          "number": 3,
          "id": "TKT-3456-7890",
          "name": "Microservicio de notificaciones",
          "task": "TKT-3456",
          "section": "BACKEND",
          "project": "notification-service",
          "repo_path": "C:/Projects/notification-service",
          "base_branch": "main",
          "feature_branch": "feature/email-notifications"
        }
      ]
    }
  }
}
```

#### Estructura de Secciones

El sistema usa un **flujo de selección en 2 pasos**:

1. **Paso 1**: Selecciona una sección (URGENTES, FRONTEND, BACKEND, etc.)
2. **Paso 2**: Selecciona una configuración específica dentro de esa sección

Esto permite:
- ✅ Mejor organización de proyectos por prioridad o área
- ✅ Navegación más rápida entre configuraciones relacionadas
- ✅ Agrupación lógica de repositorios similares
- ✅ Escalabilidad para múltiples proyectos
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
# Ejecutar el programa principal (modo interactivo)
python main.py

# El programa te guiará a través de:
# 1. Selección de sección (URGENTES, FRONTEND, BACKEND, etc.)
# 2. Selección de repositorio dentro de la sección
# 3. Menú de operaciones Git disponibles
```

### Flujo de Trabajo Típico

```bash
# 1. Inicia el programa
python main.py

# 2. Selecciona una sección
# Ejemplo: [1] URGENTES, [2] FRONTEND, [3] BACKEND
> 2  # Selecciona FRONTEND

# 3. Selecciona un repositorio
# Ejemplo: [1] admin-dashboard, [2] user-portal
> 1  # Selecciona admin-dashboard

# 4. Selecciona una operación del menú Git
# [1] Ver estado del repositorio
# [2] Crear/cambiar rama
# [3] Pull rama actual
# [4] Pull rama base
# [5] Subir cambios (commit + push)
# [6] Rebase con rama base
# [7] Resetear a rama base
# [8] Guardar cambios localmente (stash)
# [9] Flujo GitFlow completo
# [10] Eliminar rama
# [0] Salir
> 3  # Pull rama actual
```

### Comandos y Operaciones Disponibles

El programa ofrece un **menú interactivo** con las siguientes operaciones:

| Opción | Comando                      | Descripción                                                |
| ------ | ---------------------------- | ---------------------------------------------------------- |
| **1**  | Ver estado                   | Muestra el estado actual del repositorio (cambios, rama)  |
| **2**  | Crear/cambiar rama           | Validación y checkout a rama feature con manejo de stash   |
| **3**  | Pull rama actual             | Actualiza la rama actual desde el remoto                   |
| **4**  | Pull rama base               | Actualiza la rama base (main/develop) desde el remoto      |
| **5**  | Subir cambios                | Commit interactivo + push al remoto                        |
| **6**  | Rebase con rama base         | Integra cambios de la rama base a la feature               |
| **7**  | Resetear a rama base         | Reset completo con opción de backup automático             |
| **8**  | Guardar cambios (stash)      | Guarda cambios locales temporalmente                       |
| **9**  | Flujo GitFlow completo       | Ejecuta flujo completo: pull base + checkout + rebase      |
| **10** | Eliminar rama                | Elimina ramas locales y remotas con confirmación          |
| **0**  | Salir                        | Cierra el programa                                         |

### Características Avanzadas

#### Gestión Inteligente de Ramas
- ✅ Validación automática de configuración de ramas
- ✅ Checkout seguro con manejo de cambios pendientes
- ✅ Stash automático si hay cambios sin commit
- ✅ Creación de ramas si no existen

#### Pull con Manejo de Conflictos
- ✅ Pull de rama actual o rama base
- ✅ Detección automática de conflictos
- ✅ Instrucciones claras para resolución
- ✅ Logging de todas las operaciones

#### Push Seguro
- ✅ Verificación de cambios antes de commit
- ✅ Mensaje de commit interactivo
- ✅ Configuración de upstream automática
- ✅ Confirmación antes de push

#### Rebase Interactivo
- ✅ Pull automático de rama base primero
- ✅ Rebase con manejo de conflictos
- ✅ Opciones: continuar, abortar, saltar
- ✅ Guía paso a paso para resolución

#### Reset con Backup
- ✅ Creación de rama de backup antes del reset
- ✅ Reset hard a la rama base
- ✅ Opciones de recuperación segura
- ✅ Confirmación obligatoria

#### GitFlow Workflow
- ✅ Flujo completo automatizado
- ✅ Pull base → Checkout feature → Rebase
- ✅ Manejo de errores en cada paso
- ✅ Rollback automático si falla

## 📁 Estructura del Proyecto

```bash
git_manager_tasks/
├── 📄 main.py                      # Punto de entrada principal
├── 📄 config.json                 # Configuración de repositorios (organizado por secciones)
├── 📄 requirements.txt            # Dependencias de Python
├── 📄 .env                        # Variables de entorno (opcional)
├── 📄 install_dependencies.bat    # Script de instalación Windows
├── 📄 install_dependencies.sh     # Script de instalación Unix
├── 📁 src/                        # Código fuente organizado modularmente
│   ├── 📄 __init__.py
│   ├── 📁 git/                    # 🔧 Módulo de operaciones Git
│   │   ├── 📄 __init__.py
│   │   ├── 📄 GitClass.py        # Clase principal coordinadora de Git
│   │   ├── 📄 GitLogClass.py     # Sistema de logging de operaciones Git
│   │   └── 📁 managers/          # Gestores especializados por funcionalidad
│   │       ├── 📄 __init__.py
│   │       ├── 📄 GitBranchManager.py    # Gestión de ramas (crear, cambiar, eliminar)
│   │       ├── 📄 GitPullManager.py      # Operaciones de pull
│   │       ├── 📄 GitPushManager.py      # Operaciones de push y commit
│   │       ├── 📄 GitRebaseManager.py    # Integración de cambios (rebase)
│   │       ├── 📄 GitResetManager.py     # Operaciones de reset con backup
│   │       ├── 📄 GitStashManager.py     # Manejo de cambios temporales (stash)
│   │       └── 📄 GitWorkflowManager.py  # Flujos de trabajo GitFlow
│   ├── 📁 config/                 # ⚙️ Módulo de configuración
│   │   ├── 📄 __init__.py
│   │   └── 📄 JsonConfigManager.py  # Gestor de configuración por secciones
│   ├── 📁 core/                   # 🎯 Módulo central con utilidades base
│   │   ├── 📄 __init__.py
│   │   ├── 📄 GlobalClass.py     # Clase base con funcionalidades comunes
│   ├── 📁 consts/                # 🟡 Constantes de el programa
│   │   ├── 📄 __init__.py
│   │   └── 📄 env.py             # Configuración de variables de entorno
│   ├── 📁 types/                  # 📋 Definiciones de tipos TypedDict
│   │   ├── 📄 __init__.py
│   │   └── 📄 configTypes.py     # Tipos para configuración y comandos Git
│   └── 📁 utils/                  # 🛠️ Utilidades y herramientas
│       ├── 📄 __init__.py
│       └── 📄 ConsoleColors.py   # Formateo de salida en consola con colores
├── 📁 logs/                       # Directorio de logs de operaciones
│   └── 📄 YYYY-MM-DD_git_operations.log  # Logs diarios con timestamp
└── 📁 docs/                       # Documentación adicional
    ├── 📄 examples.md            # Ejemplos de uso
    └── 📁 logs/                  # Documentación de estructura de logs
```

### 🏗️ Arquitectura Modular

El proyecto utiliza una arquitectura modular bien organizada:

#### **src/git/** - Operaciones Git
- **GitClass.py**: Coordinador principal que delega operaciones a managers especializados
- **GitLogClass.py**: Sistema de logging con archivos diarios organizados
- **managers/**: 7 gestores especializados siguiendo el patrón Manager:
  - `GitBranchManager`: Validación y gestión completa de ramas
  - `GitPullManager`: Pull de ramas con manejo de conflictos
  - `GitPushManager`: Push, commits y actualización remota
  - `GitRebaseManager`: Rebase interactivo con resolución de conflictos
  - `GitResetManager`: Reset seguro con creación de backups
  - `GitStashManager`: Stash de cambios temporales
  - `GitWorkflowManager`: Implementación de GitFlow y flujos complejos

#### **src/config/** - Gestión de Configuración
- **JsonConfigManager**: Carga y selección de configuraciones organizadas por secciones
  - Flujo en 2 pasos: Selección de sección → Selección de configuración

#### **src/core/** - Funcionalidades Base
- **GlobalClass**: Clase base con métodos comunes (menús, confirmaciones, validaciones)
- **env.py**: Constantes y variables de entorno centralizadas

#### **src/types/** - Definiciones de Tipos
- **configTypes.py**: TypedDict para configuraciones, comandos Git y resultados

#### **src/utils/** - Utilidades
- **ConsoleColors**: Formateo de salida en consola (success, error, warning, info)

## 🔧 Personalización Avanzada

### Agregar Nuevos Repositorios

1. **Editar `config.json`** añadiendo configuración en la sección apropiada:

```json
{
  "sections": {
    "FRONTEND": {
      "configs": [
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
      ]
    }
  }
}
```

2. **Verificar la configuración**:

```bash
python main.py
# 1. Selecciona la sección "FRONTEND"
# 2. Selecciona el repositorio número 4
# 3. Ejecuta las operaciones Git necesarias
```

### Crear Nueva Sección

Para agregar una nueva categoría de proyectos:

```json
{
  "sections": {
    "DEVOPS": {
      "configs": [
        {
          "number": 5,
          "id": "TKT-6789-0123",
          "name": "Pipeline de CI/CD con Jenkins",
          "task": "TKT-6789",
          "section": "DEVOPS",
          "project": "ci-cd-pipeline",
          "repo_path": "C:/Projects/ci-cd-pipeline",
          "base_branch": "main",
          "feature_branch": "feature/jenkins-pipeline"
        }
      ]
    }
  }
}

### Configuración de Logging

El sistema usa logging diario automatizado:

```python
# En src/git/GitLogClass.py
# Los logs se generan automáticamente en formato:
# logs/YYYY-MM-DD_git_operations.log

# Ejemplo de estructura de log:
{
    "timestamp": "2025-12-06 10:30:45",
    "operation": "pull",
    "branch": "feature/oauth2-auth",
    "status": "success",
    "output": "Already up to date.",
    "repo_path": "C:/Projects/api-gateway"
}
```

#### Características del Sistema de Logging

- ✅ **Logs diarios**: Un archivo por día con timestamp automático
- ✅ **Formato estructurado**: JSON para fácil parsing
- ✅ **Información completa**: Operación, rama, status, salida, ruta
- ✅ **Rotación automática**: Logs organizados por fecha
- ✅ **Ubicación**: `logs/YYYY-MM-DD_git_operations.log`

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
# Ver logs del día actual
cat logs/2025-12-06_git_operations.log

# Ver logs en tiempo real (Windows PowerShell)
Get-Content logs/2025-12-06_git_operations.log -Wait -Tail 10

# Ver logs en tiempo real (Linux/macOS)
tail -f logs/2025-12-06_git_operations.log

# Buscar errores en logs
grep "ERROR" logs/*.log

# Listar todos los logs
ls -la logs/
```

### Estructura de Logs

Cada operación Git genera una entrada de log con:

```json
{
  "timestamp": "2025-12-06 10:30:45",
  "operation": "pull",
  "branch": "feature/oauth2-auth",
  "status": "success",
  "output": "Already up to date.",
  "repo_path": "C:/Projects/api-gateway",
  "user": "usuario@ejemplo.com"
}
```

## 📝 Mejores Prácticas

### Configuración de Repositorios

1. **Usar rutas absolutas** en `repo_path`
2. **Mantener nombres descriptivos** en el campo `name`
3. **Organizar por secciones** lógicas (URGENTES, FRONTEND, BACKEND, DEVOPS)
4. **Usar convenciones consistentes** para `task` y `id`
5. **Agrupar proyectos relacionados** en la misma sección
6. **Mantener la numeración secuencial** en el campo `number`

### Organización por Secciones

Estrategias recomendadas para organizar tus repositorios:

**Por Prioridad:**
```
- URGENTES: Tareas críticas con deadline inmediato
- ALTA: Prioridad alta pero no urgente
- MEDIA: Desarrollo regular
- BAJA: Mejoras y refactoring
```

**Por Área Técnica:**
```
- FRONTEND: Aplicaciones de usuario
- BACKEND: APIs y servicios
- DEVOPS: Infraestructura y CI/CD
- DATABASE: Migraciones y esquemas
```

**Por Proyecto:**
```
- PROYECTO_A: Todos los repos del proyecto A
- PROYECTO_B: Todos los repos del proyecto B
- LIBRARIES: Librerías compartidas
```

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
