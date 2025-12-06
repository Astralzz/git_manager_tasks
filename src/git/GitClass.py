import subprocess
import sys
from colorama import Fore
from typing import Optional, List

from src.core.GlobalClass import GlobalClass
from src.git.GitLogClass import GitLogClass
from src.git.managers.GitBranchManager import GitBranchManager
from src.git.managers.GitStashManager import GitStashManager
from src.git.managers.GitPullManager import GitPullManager
from src.git.managers.GitPushManager import GitPushManager
from src.git.managers.GitRebaseManager import GitRebaseManager
from src.git.managers.GitResetManager import GitResetManager
from src.git.managers.GitWorkflowManager import GitWorkflowManager
from src.types.configTypes import ExtendedConfigType, GitCommandResult, MenuOptionType


class GitClass(GlobalClass):
    """Clase para manejar operaciones Git de forma interactiva y segura"""

    def __init__(self, config: "ExtendedConfigType"):
        """
        Inicializa la clase GitClass con la configuración proporcionada

        Args:
            config: Configuración del repositorio con tipado ExtendedConfigType
        """
        super().__init__(selected_config=config)

        self.git_config: ExtendedConfigType = config
        self.repo_path: Optional[str] = config.get("repo_path")

        if self.repo_path:
            self.git_logger: GitLogClass = GitLogClass(self.repo_path)
        else:
            raise ValueError("repo_path es requerido para GitClass")

        self.validate_required_fields(["base_branch", "feature_branch"], self.repo_path)

        self.base_branch: Optional[str] = config.get("base_branch")
        self.feature_branch: Optional[str] = config.get("feature_branch")

        # Inicializar gestores especializados
        self.branch_manager = GitBranchManager(self)
        self.stash_manager = GitStashManager(self)
        self.pull_manager = GitPullManager(self)
        self.push_manager = GitPushManager(self)
        self.rebase_manager = GitRebaseManager(self)
        self.reset_manager = GitResetManager(self)
        self.workflow_manager = GitWorkflowManager(self)

        # Validaciones de seguridad
        self.branch_manager.validate_branch_configuration()

        # Intentar cambiar automáticamente a la rama feature
        self.branch_manager.auto_checkout_to_feature_branch()

        # Registra el inicio del programa
        if hasattr(self, "git_logger"):
            self.git_logger.log_program_start(self.git_config)

    def _get_base_branch(self) -> str:
        """Retorna la rama base, lanzando error si no está configurada"""
        if not self.base_branch:
            raise ValueError("Base branch not configured")
        return self.base_branch

    def _get_feature_branch(self) -> str:
        """Retorna la rama feature, lanzando error si no está configurada"""
        if not self.feature_branch:
            raise ValueError("Feature branch not configured")
        return self.feature_branch

    def run_git_command(
        self, command: str, allow_failure: bool = False
    ) -> "GitCommandResult":
        """
        Ejecuta un comando git y retorna la salida

        Args:
            command: El comando git a ejecutar
            allow_failure: Si True, no termina el programa en caso de error

        Returns:
            GitCommandResult con returncode, stdout y stderr
        """
        try:
            self.colors.info(f"▶ Ejecutando: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            if result.returncode == 0:
                if result.stdout.strip():
                    self.colors.success(f"\n{result.stdout.strip()}\n")
            else:
                if not allow_failure:
                    if result.stderr.strip():
                        self.colors.error(f"Error: {result.stderr.strip()}")

            result_dict: "GitCommandResult" = {
                "returncode": result.returncode,
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
            }

            self.git_logger.log_git_command(command, result_dict)

            if result.returncode != 0 and not allow_failure:
                self.git_logger.log_error(
                    f"Error al ejecutar comando: {result.stderr}", "run_git_command"
                )
                sys.exit(1)

            return result_dict

        except Exception as e:
            self.colors.error(f"Error inesperado: {str(e)}")

            error_result: "GitCommandResult" = {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

            self.git_logger.log_git_command(command, error_result)
            self.git_logger.log_error(f"Error inesperado: {str(e)}", "run_git_command")

            if not allow_failure:
                sys.exit(1)

            return error_result

    def display_git_menu(self) -> None:
        """Muestra el menú de opciones de forma persistente"""
        options: List["MenuOptionType"] = [
            {
                "function": self.get_repo_status,
                "description": "📊 Obtener el estado del repositorio",
            },
            {
                "function": self.get_current_branch,
                "description": "🌿 Mostrar mi rama actual",
            },
            {
                "function": self.pull_current_branch,
                "description": f"📥 PULL: Obtener cambios de mi equipo en mi rama actual",
            },
            {
                "function": self.pull_base_branch,
                "description": f"⚡ PULL DIRECTO: Traer cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} (sin importar conflictos)",
            },
            {
                "function": self._handle_rebase,
                "description": f"🔄 REBASE: Integrar cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} a {Fore.YELLOW}{self.feature_branch}{Fore.RESET}",
            },
            {
                "function": self.upload_changes,
                "description": "📤 Subir mis cambios al repositorio remoto",
            },
            {
                "function": self.create_branch_feature,
                "description": f"🌱 Crear la rama feature: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}",
            },
            {
                "function": self.reset_to_base_with_backup,
                "description": f"🔄 RESET COMPLETO: Empezar desde {Fore.BLUE}{self.base_branch}{Fore.RESET} (con backup)",
            },
            {
                "function": self.update_base_branch,
                "description": f"🔄 ACTUALIZAR RAMA BASE: Traer últimos cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET}",
            },
            {
                "function": self.delete_branch,
                "description": "🗑️ Eliminar una rama por nombre",
            },
            {
                "function": self.cancel_rebase,
                "description": "🟥 Cancelar rebase en progreso",
            },
            {
                "function": self.feature_branch_workflow,
                "description": "🌟 Flujo completo de feature branch (GitFlow CONACYT), ESPECIFICO",
            },
            {
                "function": self.restore_local_changes,
                "description": "📦 Restaurar cambios guardados (stash)",
            },
            {"function": self.view_today_logs, "description": "📋 Ver logs de hoy"},
        ]
        self.show_menu(options)

    # ===== Métodos simples que delegan a los gestores =====
    
    def get_repo_status(self) -> None:
        """Obtiene el estado del repositorio"""
        self.run_git_command("git status")

    def get_current_branch(self) -> None:
        """Muestra todas las ramas y marca la actual"""
        self.branch_manager.get_current_branch()

    def create_branch_feature(self) -> None:
        """Crea una nueva rama feature"""
        self.branch_manager.create_branch_feature()

    def delete_branch(self) -> None:
        """Elimina una rama específica"""
        self.branch_manager.delete_branch()

    def save_changes_locally(self) -> None:
        """Guarda los cambios locales usando stash"""
        self.stash_manager.save_changes_locally()

    def restore_local_changes(self) -> None:
        """Restaura los cambios guardados con stash"""
        self.stash_manager.restore_local_changes()

    def pull_current_branch(self) -> None:
        """Hace pull de la rama actual"""
        self.pull_manager.pull_current_branch()

    def pull_base_branch(self) -> None:
        """Hace pull directo de la rama base"""
        self.pull_manager.pull_base_branch()

    def upload_changes(self) -> None:
        """Sube los cambios al repositorio remoto"""
        self.push_manager.upload_changes()

    def _handle_rebase(self) -> None:
        """Integra los cambios de la rama base a la rama feature"""
        self.rebase_manager.handle_rebase()

    def get_latest_changes(self) -> None:
        """Hace rebase de la rama base a la rama feature"""
        self.rebase_manager.get_latest_changes()

    def cancel_rebase(self) -> None:
        """Cancela un rebase en progreso"""
        self.rebase_manager.cancel_rebase()

    def update_base_branch(self) -> None:
        """Actualiza la rama base con los últimos cambios del remoto"""
        self.rebase_manager.update_base_branch()

    def reset_to_base_with_backup(self) -> None:
        """Hace reset completo a la rama base con backup opcional"""
        self.reset_manager.reset_to_base_with_backup()

    def feature_branch_workflow(self):
        """Flujo completo de feature branch según GitFlow CONACYT"""
        self.workflow_manager.feature_branch_workflow()

    def view_today_logs(self) -> None:
        """Muestra los logs del día actual"""
        try:
            log_content = self.git_logger.read_today_log()
            log_path = self.git_logger.get_today_log_path()

            self.colors.info(f"📋 LOGS DE HOY: {log_path}")
            self.colors.info("=" * 80)

            if log_content == "No hay log para hoy.":
                self.colors.warning("📝 No hay logs registrados para hoy.")
            else:
                lines = log_content.strip().split("\n")
                for line in lines:
                    if line.strip():
                        if "[ERROR]" in line:
                            self.colors.error(line)
                        elif "[WARNING]" in line:
                            self.colors.warning(line)
                        elif "[SUCCESS]" in line:
                            self.colors.success(line)
                        else:
                            self.colors.info(line)

            self.colors.info("=" * 80)
            self.git_logger.log_operation("VIEW_LOGS", "Logs consultados", "INFO")

        except Exception as e:
            self.colors.error(f"Error al leer logs: {str(e)}")
            self.git_logger.log_error(str(e), "view_today_logs")
