import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la ruta del archivo de configuración y poniendo la ruta actual
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../../config.json")

# Configuración de la ruta base
BASE_PATH = os.getenv("BASE_PATH", "C:/")

# Pass para acciones sensibles
PASS_SENSITIVE = os.getenv("PASS_SENSITIVE", "1234")

# ID Para conaqyt
GIT_CONFIG_ID = os.getenv("GIT_CONFIG_ID")
