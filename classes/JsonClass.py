import json
import os
import sys

from consts.env import BASE_PATH
from classes.GlobalClass import GlobalClass
from byTypes.configTypes import ExtendedConfigType


# Clase para manejar archivos json
class JsonClass(GlobalClass):

    # Constructor de la clase
    def __init__(self, json_file: str):
        self.json_file = json_file
        # Inicializa la clase GlobalClass
        super().__init__()

    # Función para cargar las configuraciones
    def load_configs(self) -> list[ExtendedConfigType]:
        """
        Carga las configuraciones desde un archivo json
        @return {list[ExtendedConfigType]}: Las configuraciones cargadas
        """

        # Muestra la ruta del archivo de configuración
        self.colors.info(f"📁 Archivo de configuración: {self.json_file}")

        # Verifica si el archivo de configuración existe
        self.validate_required_fields([], self.json_file)

        # Carga el archivo de configuración
        with open(self.json_file, "r") as f:
            return json.load(f)

    # Función para imprimir las configuraciones disponibles
    def view_list_configs(self, configs: list[ExtendedConfigType]) -> None:
        """
        Imprime las configuraciones disponibles
        @param {list[ExtendedConfigType]} configs: Las configuraciones disponibles
        """
        self.colors.info("📦 Configuraciones disponibles:")
        for config in configs:
            self.colors.info(
                f"{config.get('number')}. {config.get('id')} - {config.get('name')}"
            )
            self.colors.info("\n")

    # Función para seleccionar la configuración
    def select_config(self, configs: list[ExtendedConfigType]) -> ExtendedConfigType:
        """
        Selecciona una configuración de las disponibles
        @param {list[ExtendedConfigType]} configs: Las configuraciones disponibles
        @return {ExtendedConfigType}: La configuración seleccionada
        """
        # Imprime las configuraciones disponibles
        self.view_list_configs(configs)

        # Pide al usuario que seleccione una configuración
        selected = input(
            "👉 Escribe el número de la configuración que quieres usar: "
        ).strip()

        # Busca la configuración seleccionada
        for config in configs:
            if config.get("number") == int(selected):
                # Crea una nueva configuración con la ruta completa del repositorio
                repo_value = config.get("repo_path")
                if not repo_value:
                    self.colors.error("La configuración seleccionada no contiene un valor válido para 'repo'.")
                    sys.exit(1)
                config_with_path: ExtendedConfigType = {
                    **config,
                    "repo_path": os.path.join(BASE_PATH, repo_value),
                }
                # Imprime la configuración seleccionada
                self.view_selected_config(config_with_path)
                # Confirma la acción
                if not self.confirm_action(
                    "La configuración seleccionada es la correcta?"
                ):
                    sys.exit(1)
                return config_with_path

        # Si no se encuentra la configuración, imprime un mensaje de error y sale
        self.colors.error(
            f"No se encontró una configuración con el número '{selected}'"
        )
        sys.exit(1)
