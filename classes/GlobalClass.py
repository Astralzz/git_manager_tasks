import os
import sys
from classes.ConsoleColors import ConsoleColors
from consts.env import PASS_SENSITIVE


# Clase abstracta para manejar las configuraciones globales
class GlobalClass:

    # Constructor de la clase
    def __init__(self):
        # Inicializa los colores
        self.colors = ConsoleColors()

    # Funcion para imprimir la configuracion seleccionada
    def view_selected_config(self, config: dict) -> None:
        """
        Imprime la configuracion seleccionada
        @param {dict} config: La configuracion seleccionada
        """
        self.colors.info("--------------------------------")
        self.colors.info(
            f"👉 Configuración seleccionada: {config.get('id')} - {config.get('name')}"
        )
        self.colors.info(f"👉 Número: {config.get('number')}")
        self.colors.info(f"👉 Repo: {config.get('repo_path')}")
        self.colors.info(f"👉 Rama base: {config.get('base_branch')}")
        self.colors.info(f"👉 Rama feature: {config.get('feature_branch')}\n")
        self.colors.info(f"👉 Proyecto: {config.get('project')}")
        self.colors.info(f"👉 Sección: {config.get('section')}")
        self.colors.info(f"👉 Tarea: {config.get('task')}")
        self.colors.info("--------------------------------")
        self.colors.info("\n")

    # Funcion para confirmar la accion o salir del programa
    def confirm_action(
        self,
        message: str = "¿Estás seguro de querer continuar? ",
    ) -> bool:
        """
        Pide confirmacion para continuar o salir del programa
        @param {str} message: El mensaje a mostrar
        @return {bool} True si se confirma la accion, False si se cancela
        """
        confirm_input = input(f"📝 {message}, Presiona 's/S' para continuar o cualquier otra tecla para salir: ").strip()
        
        # Registra la confirmación del usuario
        if hasattr(self, 'logger'):
            self.logger.log_user_input("confirmation", confirm_input)
        
        if confirm_input.lower() != "s":
            self.colors.error("No se ha confirmado la acción.")
            if hasattr(self, 'logger'):
                self.logger.log_warning("Acción no confirmada", "confirm_action")
            return False
        else:
            self.colors.success("Se ha confirmado la acción.")
            if hasattr(self, 'logger'):
                self.logger.log_success("Acción confirmada", "confirm_action")
            return True

    # Funcion para pedir la contraseña para acciones sensibles
    def ask_pass(self, message: str = "Escribe la contraseña: ") -> None:
        """
        Pide el pass para acciones sensibles
        """
        pass_input = input(f"📝 {message}").strip()
        
        # Registra que se pidió contraseña (sin mostrar la contraseña)
        if hasattr(self, 'logger'):
            self.logger.log_user_input("password", "***HIDDEN***")
        
        # Verifica si la contraseña es correcta
        if pass_input != PASS_SENSITIVE:
            self.colors.error("La contraseña es incorrecta.")
            if hasattr(self, 'logger'):
                self.logger.log_error("Contraseña incorrecta", "ask_pass")
                self.logger.log_program_end()
            sys.exit(1)
        else:
            if hasattr(self, 'logger'):
                self.logger.log_success("Contraseña verificada correctamente", "ask_pass")

    # Funcion para validar los campos requeridos
    def validate_required_fields(self, fields: list[str], path: str) -> None:
        """
        Valida los campos requeridos
        @param {list[str]} fields: Los campos requeridos
        @param {str} path: La ruta del repositorio
        """
        # Verifica si faltan campos en la configuracion seleccionada
        for field in fields:
            # Obtiene el valor del campo
            value = self.config.get(field)
            # Verifica si el campo esta vacio
            if not value:
                self.colors.error(f"Falta el campo '{field}' en la configuración.")
                sys.exit(1)
        # Verifica si la ruta del repositorio existe
        if not os.path.exists(path):
            self.colors.error(f"La ruta {path} no existe.")
            sys.exit(1)
        self.colors.success("Todos los campos requeridos son validos.")

    # Funcion abstracta para mostrar el menu de opciones
    def show_menu(self, options: list[dict]) -> None:
        """
        Muestra el menu de opciones
        @param {list[dict]} options: Las opciones del menu [{ function: callable, description: str }]
        """
        # Validar que las opciones tengan la estructura correcta
        for option in options:
            if not isinstance(option, dict) or 'function' not in option or 'description' not in option:
                self.colors.error("Formato de opciones inválido. Cada opción debe tener 'function' y 'description'.")
                return

        # Bucle para mostrar el menu de opciones
        while True:
            # Mostrar el menu de opciones
            self.colors.info("--------------------------------")
            self.colors.info("🔄 MENU DE OPCIONES PARA GIT:")
            for index, option in enumerate(options, start=1):
                self.colors.info(f"[{index}] {option.get('description')}")
            self.colors.info(f"[{len(options) + 1}] Salir")
            self.colors.info("--------------------------------\n")

            # Pedir la opcion seleccionada
            selected = input(
                "👉 Escribe el número de la opción que quieres usar: "
            ).strip()

            # Verificar si el usuario quiere salir
            if selected == str(len(options) + 1):
                self.colors.info("🔄 Saliendo del programa...")
                # Registra el fin del programa
                if hasattr(self, 'logger'):
                    self.logger.log_program_end()
                sys.exit(0)

            # Verificar si la opción es válida y ejecutar la función correspondiente
            try:
                selected_index = int(selected) - 1
                if 0 <= selected_index < len(options):
                    # Registra la selección del menú
                    if hasattr(self, 'logger'):
                        option_description = options[selected_index]['description']
                        self.logger.log_menu_selection(selected_index + 1, option_description)
                    
                    options[selected_index]['function']()
                else:
                    self.colors.error("Opción no válida.")
                    if hasattr(self, 'logger'):
                        self.logger.log_warning(f"Opción no válida seleccionada: {selected}", "show_menu")
            except ValueError:
                self.colors.error("Por favor, ingresa un número válido.")
                if hasattr(self, 'logger'):
                    self.logger.log_error(f"Entrada no válida en menú: {selected}", "show_menu")
