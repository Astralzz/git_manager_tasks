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

### 1. Archivo principal (config.json)

El selector sigue este recorrido: **área → grupo → proyecto → rama nueva o flujo guardado → tipo de rama**. Los arreglos conservan el orden que aparece en el menú.

```json
{
  "repo_roots": {
    "front": "Projects/Gatherleads/frontend",
    "backend": "Projects/Gatherleads/backend"
  },
  "branch_types": {
    "hotfix": { "prefix": "hotfix/", "environment": "QA QUITO" },
    "release": { "prefix": "release/", "environment": "QA ARG" },
    "feature": { "prefix": "feature/", "environment": "DEV" }
  },
  "areas": [
    {
      "id": "back",
      "name": "Back",
      "root": "backend",
      "groups": [
        {
          "id": "principal",
          "name": "Proyectos principales",
          "projects": [
            {
              "id": "backoffice",
              "name": "Backoffice",
              "folder": "backoffice",
              "branch_base_defaults": {
                "hotfix": "main",
                "release": "main",
                "feature": "main"
              },
              "branches": [
                {
                  "id": "GL-1234",
                  "name": "GL-1234 - Ejemplo de flujo encadenado",
                  "slug": "ejemplo-de-tarea",
                  "types": {
                    "hotfix": { "base": "main" },
                    "release": { "base": "main" },
                    "feature": {
                      "base": "release",
                      "suffix": "-units"
                    }
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

- `repo_roots` guarda cada ruta compartida una sola vez. Las rutas relativas se combinan con `BASE_PATH`; también se aceptan rutas absolutas.
- Cada área o grupo puede elegir una raíz. Los proyectos guardan solo su carpeta relativa.
- `branch_base_defaults` fija la base por tipo para las ramas nuevas de ese proyecto.
- `branches` contiene atajos opcionales para flujos con nombres o bases especiales. `base` puede ser una rama real (`main`) o un tipo del mismo flujo (`release`). Cuando una rama se basa en otro tipo del flujo, hereda su nombre; `suffix` agrega un final opcional como `-units`. Define `slug` solo si esa rama necesita un nombre distinto.
- La opción **Nueva rama** siempre está disponible: escribe el sufijo, elige `feature`, `hotfix` o `release` y se aplica la base configurada. No hace falta agregar cada defecto al JSON.
- Para admitir otro prefijo, agrega su tipo en `branch_types` y configura la base correspondiente en cada proyecto que lo use.

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
````

## 🎯 Uso y Funcionalidades

### Ejecución Básica

```bash
# Ejecutar el programa principal (modo interactivo)
python main.py

# El programa te guiará a través de:
# 1. Selección de área (Front, Back u Otros)
# 2. Grupo y proyecto
# 3. Rama nueva o flujo guardado y tipo de rama
# 4. Menú de operaciones Git disponibles
```

### Flujo de Trabajo Típico

```bash
# 1. Inicia el programa
python main.py

# 2. Selecciona área, grupo y proyecto; luego una rama nueva o un flujo guardado
# 3. Elige el tipo de rama y, si es nueva, escribe su nombre
# 4. Selecciona una operación del menú Git
# [1] Ver estado del repositorio
# [2] Crear/cambiar rama
# [3] Pull rama actual
# [4] Pull rama base
# [5] Subir cambios (commit + push)
# [6] Rebase con rama base
# [7] Resetear a rama base
# [8] Guardar cambios localmente (stash)
# [9] Eliminar rama
# [0] Salir
> 3  # Pull rama actual
```

### Comandos y Operaciones Disponibles

El programa ofrece un **menú interactivo** con las siguientes operaciones:

| Opción | Comando                 | Descripción                                              |
| ------ | ----------------------- | -------------------------------------------------------- |
| **1**  | Ver estado              | Muestra el estado actual del repositorio (cambios, rama) |
| **2**  | Crear/cambiar rama      | Validación y checkout a la rama seleccionada con manejo de stash |
| **3**  | Pull rama actual        | Actualiza la rama actual desde el remoto                 |
| **4**  | Pull rama base          | Actualiza la rama base (main/develop) desde el remoto    |
| **5**  | Subir cambios           | Commit interactivo + push al remoto                      |
| **6**  | Rebase con rama base    | Integra cambios de la rama base a la rama seleccionada   |
| **7**  | Resetear a rama base    | Reset completo con opción de backup automático           |
| **8**  | Guardar cambios (stash) | Guarda cambios locales temporalmente                     |
| **9**  | Eliminar rama           | Elimina ramas locales y remotas con confirmación         |
| **0**  | Salir                   | Cierra el programa                                       |

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

## 📁 Estructura del Proyecto

```bash
git_manager_tasks/
├── 📄 main.py                      # Punto de entrada principal
├── 📄 config.json                 # Configuración de repositorios por áreas y proyectos
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
│   │       └── 📄 GitAbortManager.py     # Cancelación de operaciones en progreso
│   ├── 📁 config/                 # ⚙️ Módulo de configuración
│   │   ├── 📄 __init__.py
│   │   └── 📄 JsonConfigManager.py  # Selector de áreas, proyectos y ramas
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
  - `GitAbortManager`: Cancelación de merge, rebase y cherry-pick

#### **src/config/** - Gestión de Configuración

- **JsonConfigManager**: Navega áreas, grupos, proyectos y tipos de rama
  - Flujo: área → grupo → proyecto → rama nueva o flujo guardado → tipo de rama

#### **src/core/** - Funcionalidades Base

- **GlobalClass**: Clase base con métodos comunes (menús, confirmaciones, validaciones)
- **env.py**: Constantes y variables de entorno centralizadas

#### **src/types/** - Definiciones de Tipos

- **configTypes.py**: TypedDict para configuraciones, comandos Git y resultados

#### **src/utils/** - Utilidades

- **ConsoleColors**: Formateo de salida en consola (success, error, warning, info)

## 🔧 Personalización Avanzada

### Agregar un proyecto

1. Reutiliza una ruta de `repo_roots` o agrega una nueva.
2. Coloca el proyecto dentro de un grupo del área correspondiente.
3. Define su nombre, carpeta relativa y bases predeterminadas por tipo.

```json
{
  "id": "customer-profile",
  "name": "Customer Profile",
  "folder": "hdl-v2-customer-profile-sd",
  "branch_base_defaults": {
    "hotfix": "main",
    "release": "main",
    "feature": "main"
  },
  "branches": []
}
```

### Agregar un grupo

Agrega un objeto con `id`, `name` y `projects` dentro del área deseada. Los grupos y proyectos aparecen en el mismo orden en que están escritos.

### Guardar un flujo especial o agregar un tipo de rama

Para un defecto o issue normal, usa **Nueva rama** en el menú; no requiere editar el JSON. Guarda un elemento en `branches` solo cuando quieras un atajo con un nombre fijo o una cadena de bases especial. Un Bolt de AI-DLC puede guardarse de esa forma, pero los trabajos puntuales no necesitan ser Bolts. Para otra convención, agrega el prefijo y entorno en `branch_types` y configura su base en el proyecto.

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
````

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

1. Reutiliza las entradas de `repo_roots` para rutas compartidas.
2. Usa nombres de proyecto que distingan rápidamente cada repositorio.
3. Ordena proyectos en áreas y grupos que coincidan con tu forma de trabajo.
4. Usa `branches` solo para flujos que convenga guardar como atajos.
5. Declara las bases normales en `branch_base_defaults` y las excepciones en cada flujo guardado.

### Organización de áreas y grupos

Agrupa primero por área y luego por el propósito de cada repositorio. Por ejemplo:

- **Front**: aplicación web, móvil y librerías.
- **Back**: proyectos principales, notificaciones, webhooks, perfiles, integraciones y plataforma.
- Agrega, elimina o reordena grupos y proyectos directamente en los arreglos de `areas`.

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
