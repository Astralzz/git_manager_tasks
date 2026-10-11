import os
from datetime import datetime
from src.types.configTypes import GitCommandResult, ExtendedConfigType, LogStatus


# Clase para manejar logs diarios de las operaciones Git
class GitLogClass:

    # Constructor de la clase
    def __init__(self, repo_path: str):
        """
        Inicializa la clase de logs
        @param {str} repo_path: Ruta del repositorio
        """
        self.repo_path = repo_path
        # Obtener la ruta de este archivo
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Subir 1 nivel desde current_dir
        self.logs_dir = os.path.join(current_dir, "../logs")
        # Asegura que exista el directorio de logs
        self._ensure_logs_directory()

        # Log de información sobre la ubicación de logs
        print(f"📁 Logs se guardarán en: {self.logs_dir}")

    # Función para asegurar que exista el directorio de logs
    def _ensure_logs_directory(self) -> None:
        """
        Asegura que exista el directorio de logs
        """
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    # Función para obtener el nombre del archivo de log para hoy
    def _get_today_filename(self) -> str:
        """
        Obtiene el nombre del archivo de log para hoy
        @return {str}: Nombre del archivo (ej: 2024-01-15_git_operations.log)
        """
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{today}_git_operations.log"

    # Función para obtener la ruta completa del archivo de log de hoy
    def _get_log_file_path(self) -> str:
        """
        Obtiene la ruta completa del archivo de log de hoy
        @return {str}: Ruta completa del archivo
        """
        filename = self._get_today_filename()
        return os.path.join(self.logs_dir, filename)

    # Función para registrar una operación en el log diario
    def log_operation(
        self, operation: str, details: str = "", status: "LogStatus" = "INFO"
    ) -> None:
        """
        Registra una operación en el log diario
        @param {str} operation: Nombre de la operación
        @param {str} details: Detalles adicionales
        @param {LogStatus} status: Estado de la operación (INFO, SUCCESS, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file_path = self._get_log_file_path()

        # Crear la línea del log
        log_line = f"[{timestamp}] [{status}] {operation}"
        if details:
            log_line += f" - {details}"
        log_line += "\n"

        # Escribir en el archivo
        try:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_line)
        except Exception as e:
            # Si no se puede escribir el log, no fallar el programa
            print(f"⚠️ No se pudo escribir en el log: {e}")

    # Función para registrar un comando git ejecutado
    def log_git_command(self, command: str, result: "GitCommandResult") -> None:
        """
        Registra un comando Git ejecutado
        @param {str} command: Comando ejecutado
        @param {GitCommandResult} result: Resultado del comando
        """
        status = "SUCCESS" if result.get("returncode") == 0 else "ERROR"
        details = f"Command: {command}"

        if result.get("stderr") and result.get("returncode") != 0:
            details += f" | Error: {result.get('stderr')}"

        self.log_operation("GIT_COMMAND", details, status)

    # Función para registrar la selección de una opción del menu
    def log_menu_selection(self, option_number: int, option_description: str) -> None:
        """
        Registra la selección de una opción del menú
        @param {int} option_number: Número de la opción seleccionada
        @param {str} option_description: Descripción de la opción
        """
        details = f"Option {option_number}: {option_description}"
        self.log_operation("MENU_SELECTION", details, "INFO")

    # Función para registrar una entrada del usuario
    def log_user_input(self, input_type: str, value: str) -> None:
        """
        Registra una entrada del usuario
        @param {str} input_type: Tipo de entrada (commit_message, stash_message, etc.)
        @param {str} value: Valor ingresado
        """
        # Ocultar información sensible
        if input_type in ["password", "pass"]:
            value = "***HIDDEN***"

        details = f"{input_type}: {value}"
        self.log_operation("USER_INPUT", details, "INFO")

    # Función para registrar operaciones relacionadas con ramas
    def log_branch_operation(
        self, operation: str, branch_name: str, details: str = ""
    ) -> None:
        """
        Registra operaciones relacionadas con ramas
        @param {str} operation: Tipo de operación (checkout, create, delete, etc.)
        @param {str} branch_name: Nombre de la rama
        @param {str} details: Detalles adicionales
        """
        full_details = f"Branch: {branch_name}"
        if details:
            full_details += f" | {details}"

        self.log_operation(f"BRANCH_{operation.upper()}", full_details, "INFO")

    # Función para registrar operaciones de rebase
    def log_rebase_operation(
        self, base_branch: str, feature_branch: str, status: "LogStatus" = "INFO"
    ) -> None:
        """
        Registra operaciones de rebase
        @param {str} base_branch: Rama base
        @param {str} feature_branch: Rama feature
        @param {LogStatus} status: Estado de la operación
        """
        details = f"From: {base_branch} → To: {feature_branch}"
        self.log_operation("REBASE", details, status)

    # Función para registrar operaciones de pull
    def log_pull_operation(
        self, branch_name: str, status: "LogStatus" = "INFO"
    ) -> None:
        """
        Registra operaciones de pull
        @param {str} branch_name: Nombre de la rama
        @param {LogStatus} status: Estado de la operación
        """
        details = f"Branch: {branch_name}"
        self.log_operation("PULL", details, status)

    # Función para registrar operaciones de push
    def log_push_operation(
        self, branch_name: str, commit_message: str, status: "LogStatus" = "INFO"
    ) -> None:
        """
        Registra operaciones de push
        @param {str} branch_name: Nombre de la rama
        @param {str} commit_message: Mensaje del commit
        @param {LogStatus} status: Estado de la operación
        """
        details = f"Branch: {branch_name} | Commit: {commit_message}"
        self.log_operation("PUSH", details, status)

    # Función para registrar operaciones de stash
    def log_stash_operation(
        self, operation: str, stash_message: str = "", status: "LogStatus" = "INFO"
    ) -> None:
        """
        Registra operaciones de stash
        @param {str} operation: Tipo de operación (save, pop, list)
        @param {str} stash_message: Mensaje del stash
        @param {LogStatus} status: Estado de la operación
        """
        details = f"Operation: {operation}"
        if stash_message:
            details += f" | Message: {stash_message}"

        self.log_operation("STASH", details, status)

    # Función para registrar errores
    def log_error(self, error_message: str, context: str = "") -> None:
        """
        Registra errores
        @param {str} error_message: Mensaje de error
        @param {str} context: Contexto del error
        """
        details = error_message
        if context:
            details = f"{context} | {error_message}"

        self.log_operation("ERROR", details, "ERROR")

    # Función para registrar advertencias
    def log_warning(self, warning_message: str, context: str = "") -> None:
        """
        Registra advertencias
        @param {str} warning_message: Mensaje de advertencia
        @param {str} context: Contexto de la advertencia
        """
        details = warning_message
        if context:
            details = f"{context} | {warning_message}"

        self.log_operation("WARNING", details, "WARNING")

    # Función para registrar operaciones exitosas
    def log_success(self, success_message: str, context: str = "") -> None:
        """
        Registra operaciones exitosas
        @param {str} success_message: Mensaje de éxito
        @param {str} context: Contexto del éxito
        """
        details = success_message
        if context:
            details = f"{context} | {success_message}"

        self.log_operation("SUCCESS", details, "SUCCESS")

    # Función para registrar el inicio del programa con la configuración seleccionada
    def log_program_start(self, config: "ExtendedConfigType") -> None:
        """
        Registra el inicio del programa con la configuración seleccionada
        @param {ExtendedConfigType} config: Configuración seleccionada
        """
        # Crear una línea separadora para el inicio
        separator = "=" * 80
        start_message = f"🚀 INICIO DEL PROGRAMA GIT"

        # Información de la configuración
        config_info = f"Config: {config.get('name')}"
        project_info = f"Proyecto: {config.get('project')}"
        section_info = f"Sección: {config.get('section')}"
        task_info = f"Tarea: {config.get('task')}"
        repo_info = f"Repo: {config.get('repo_path')}"
        base_branch_info = f"Rama base: {config.get('base_branch')}"
        branch_type = config.get("branch_type_label", "destino")
        feature_branch_info = f"Rama {branch_type}: {config.get('feature_branch')}"

        # Escribir el log de inicio
        log_file_path = self._get_log_file_path()
        try:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n{separator}\n")
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] {start_message}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] CONFIG_SELECTED - {config_info}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] PROJECT_INFO - {project_info}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] SECTION_INFO - {section_info}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] TASK_INFO - {task_info}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] REPO_INFO - {repo_info}\n"
                )
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] BRANCH_INFO - {base_branch_info} | {feature_branch_info}\n"
                )
                log_file.write(f"{separator}\n")
        except Exception as e:
            print(f"⚠️ No se pudo escribir el log de inicio: {e}")

    # Función para registrar el fin del programa
    def log_program_end(self) -> None:
        """
        Registra el fin del programa
        """
        separator = "=" * 80
        end_message = f"🏁 FIN DEL PROGRAMA GIT"

        log_file_path = self._get_log_file_path()
        try:
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(
                    f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [INFO] {end_message}\n"
                )
                log_file.write(f"{separator}\n\n")
        except Exception as e:
            print(f"⚠️ No se pudo escribir el log de fin: {e}")

    # Función para obtener la ruta del archivo de log de hoy
    def get_today_log_path(self) -> str:
        """
        Obtiene la ruta del archivo de log de hoy
        @return {str}: Ruta del archivo
        """
        return self._get_log_file_path()

    # Función para leer el contenido del log de hoy
    def read_today_log(self) -> str:
        """
        Lee el contenido del log de hoy
        @return {str}: Contenido del log
        """
        log_file_path = self._get_log_file_path()

        if os.path.exists(log_file_path):
            try:
                with open(log_file_path, "r", encoding="utf-8") as log_file:
                    return log_file.read()
            except Exception as e:
                return f"Error al leer el log: {e}"
        else:
            return "No hay log para hoy."

    # Función para obtener la ruta del directorio de logs
    def get_logs_directory(self) -> str:
        """
        Obtiene la ruta del directorio de logs
        @return {str}: Ruta del directorio
        """
        return self.logs_dir
