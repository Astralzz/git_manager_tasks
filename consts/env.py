import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuracion de la ruta del archivo de configuracion y poniendo la ruta actual
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../config.json")

# Configuracion de la ruta base
BASE_PATH = os.getenv("BASE_PATH", "C:/")

# Pass para acciones sensibles
PASS_SENSITIVE = os.getenv("PASS_SENSITIVE", "1234")
