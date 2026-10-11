import os
import sys
from typing import List, Optional

from src.consts.env import PASS_SENSITIVE
from src.utils.ConsoleColors import ConsoleColors
from src.utils.ExceptionsClass import RestartProgramException
from src.types.configTypes import MenuOptionType, ExtendedConfigType, LoggerProtocol


# Clase abstracta para manejar las configuraciones globales
class GlobalClass:
    
    # Atributos opcionales que pueden ser agregados por clases hijas
    logger: Optional["LoggerProtocol"]
    config: ExtendedConfigType | None

    # Constructor de la clase
    def __init__(self, selected_config: Optional["ExtendedConfigType"] = None) -> None:
        # Inicializa los colores
        self.colors = ConsoleColors()
        # Inicializa config como None por defecto
        self.config  = selected_config

    # Función para imprimir la configuración seleccionada
    def view_selected_config(self, config: "ExtendedConfigType") -> None:
        """
        Imprime la configuración seleccionada
        @param {ExtendedConfigType} config: La configuración seleccionada
        """
        self.colors.info("--------------------------------")
        self.colors.info(
            f"👉 Flujo de rama: {config.get('name')}"
        )
        self.colors.info(f"👉 Repo: {config.get('repo_path')}")
        self.colors.info(f"👉 Rama base: {config.get('base_branch')}")
        self.colors.info(
            f"👉 Rama {config.get('branch_type_label', 'destino')}: "
            f"{config.get('feature_branch')}"
        )
        if config.get("branch_environment"):
            self.colors.info(f"👉 Entorno: {config.get('branch_environment')}")
        self.colors.info(f"👉 Proyecto: {config.get('project')}")
        self.colors.info(f"👉 Área / grupo: {config.get('section')}")
        self.colors.info("--------------------------------")
        self.colors.info("\n")

    # Confirma o cancela una acción.
    def confirm_action(
        self,
        message: str = "¿Estás seguro de querer continuar?",
    ) -> bool:
        confirm_input = input(
            f"📝 {message}, presiona 's/S' para continuar o cualquier otra tecla para cancelar: "
        ).strip()

        if hasattr(self, "logger") and self.logger is not None:
            self.logger.log_user_input("confirmation", confirm_input)

        if confirm_input.lower() != "s":
            self.colors.error("Acción cancelada.")
            if hasattr(self, "logger") and self.logger is not None:
                self.logger.log_warning("Acción no confirmada", "confirm_action")
            return False

        self.colors.success("Acción confirmada.")
        if hasattr(self, "logger") and self.logger is not None:
            self.logger.log_success("Acción confirmada", "confirm_action")
        return True

    def ask_pass(self, message: str = "Escribe la contraseña: ") -> bool:
        pass_input = input(f"📝 {message}").strip()

        if hasattr(self, "logger") and self.logger is not None:
            self.logger.log_user_input("password", "***HIDDEN***")

        if pass_input != PASS_SENSITIVE:
            self.colors.error("La contraseña es incorrecta.")
            if hasattr(self, "logger") and self.logger is not None:
                self.logger.log_error("Contraseña incorrecta", "ask_pass")
            return False

        if hasattr(self, "logger") and self.logger is not None:
            self.logger.log_success("Contraseña verificada correctamente", "ask_pass")
        return True

    def validate_required_fields(self, fields: list[str], path: str) -> None:
        """
        Valida los campos requeridos
        @param {list[str]} fields: Los campos requeridos
        @param {str} path: La ruta del repositorio
        """
        # Verifica si faltan campos en la configuración seleccionada
        for field in fields:
            # Obtiene el valor del campo
            value = self.config.get(field) if isinstance(self.config, dict) else None
            # Verifica si el campo esta vació
            if not value:
                self.colors.error(f"Falta el campo '{field}' en la configuración.")
                sys.exit(1)
        # Verifica si la ruta del repositorio existe
        if not os.path.exists(path):
            self.colors.error(f"La ruta {path} no existe.")
            sys.exit(1)
        self.colors.success("Todos los campos requeridos son validos.")

    # Función abstracta para mostrar el menu de opciones
    def show_menu(self, options: List["MenuOptionType"], is_submenu: bool = False) -> None:
        for option in options:
            if "function" not in option or "description" not in option:
                raise ValueError("Cada opción requiere 'function' y 'description'.")

        while True:
            self.colors.info("--------------------------------")
            title = "SUBMENÚ DE OPCIONES" if is_submenu else "MENÚ DE OPCIONES PARA GIT"
            self.colors.info(title)
            for index, option in enumerate(options, start=1):
                self.colors.info(f"[{index}] {option.get('description')}")

            exit_text = "Volver" if is_submenu else "Salir"
            self.colors.info(f"[{len(options) + 1}] {exit_text}")
            self.colors.info("--------------------------------")
            self.colors.info("")

            selected = input("Escribe el número de la opción que quieres usar: ").strip()
            if selected == str(len(options) + 1):
                if is_submenu:
                    self.colors.info("Volviendo al menú anterior...")
                    return

                self.colors.info("Saliendo del programa...")
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_program_end()
                sys.exit(0)

            try:
                selected_index = int(selected) - 1
            except ValueError:
                self.colors.error("Introduce un número válido.")
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_error(f"Entrada no válida en menú: {selected}", "show_menu")
                continue

            if not 0 <= selected_index < len(options):
                self.colors.error("Opción no válida.")
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_warning(
                        f"Opción no válida seleccionada: {selected}", "show_menu"
                    )
                continue

            option = options[selected_index]
            try:
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_menu_selection(
                        selected_index + 1, option["description"]
                    )
                option["function"]()
            except (KeyboardInterrupt, RestartProgramException):
                raise
            except SystemExit as error:
                self.colors.error(
                    f"La operación terminó inesperadamente (código {error.code})."
                )
                self.colors.info("El programa sigue abierto; regresando al menú.")
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_error(
                        f"SystemExit({error.code}) durante una operación", "show_menu"
                    )
            except Exception as error:
                self.colors.error(
                    f"Error durante la operación ({type(error).__name__}): {error}"
                )
                self.colors.info("El programa sigue abierto; regresando al menú.")
                if hasattr(self, "logger") and self.logger is not None:
                    self.logger.log_error(str(error), "show_menu")
