import json
import os
import sys

from classes.GlobalClass import GlobalClass
from consts.env import BASE_PATH

# Clase para manejar archivos json
class JsonClass(GlobalClass):

    # Constructor de la clase
    def __init__(self, json_file: str):
        self.json_file = json_file
        # Inicializa la clase GlobalClass
        super().__init__()

    # Funcion para cargar las configuraciones
    def load_configs(self) -> list[dict]:
        """
        Carga las configuraciones desde un archivo json
        @return {list[dict]}: Las configuraciones cargadas
        """

        # Muestra la ruta del archivo de configuracion
        self.colors.info(f"📁 Archivo de configuracion: {self.json_file}")

        # Verifica si el archivo de configuracion existe
        self.validate_required_fields([], self.json_file)

        # Carga el archivo de configuracion
        with open(self.json_file, "r") as f:
            return json.load(f)

    # Funcion para imprimir las configuraciones disponibles
    def view_list_configs(self, configs: list[dict]) -> None:
        """
        Imprime las configuraciones disponibles
        @param {list[dict]} configs: Las configuraciones disponibles
        """
        self.colors.info("📦 Configuraciones disponibles:")
        for idx, config in enumerate(configs):
            self.colors.info(f"{config.get('number')}. {config.get('id')} - {config.get('name')}")
            self.colors.info("\n")

    # Funcion para seleccionar la configuracion
    def select_config(self, configs: list[dict]) -> dict:
        """
        Selecciona una configuracion de las disponibles
        @param {list[dict]} configs: Las configuraciones disponibles
        @return {dict}: La configuracion seleccionada
        """
        # Imprime las configuraciones disponibles
        self.view_list_configs(configs)

        # Pide al usuario que seleccione una configuracion
        selected = input(
            "👉 Escribe el número de la configuración que quieres usar: "
        ).strip()

        # Busca la configuracion seleccionada
        for config in configs:
            if config.get("number") == int(selected):
                # Construye la ruta completa del repositorio
                config["repo_path"] = os.path.join(BASE_PATH, config["repo_path"])
                # Imprime la configuracion seleccionada
                self.view_selected_config(config)
                # Confirma la accion
                if not self.confirm_action("La configuracion seleccionada es la correcta?"):
                    sys.exit(1)
                return config

        # Si no se encuentra la configuracion, imprime un mensaje de error y sale
        self.colors.error(f"No se encontró una configuración con el número '{selected}'")
        sys.exit(1)
