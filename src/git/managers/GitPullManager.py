from typing import TYPE_CHECKING
from colorama import Fore

if TYPE_CHECKING:
    from src.types.configTypes import GitCommandResult


class GitPullManager:
    """Clase para manejar operaciones de pull en Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de pull con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger
        self.base_branch = git_instance.base_branch

    def pull_current_branch(self) -> None:
        """Hace pull de la rama actual"""
        self.git.ask_pass()

        try:
            branch_result = self.git.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"].strip()

            self.colors.info(
                f" Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )

            if current_branch == self.base_branch:
                self.colors.error(f"Estás en la rama base '{current_branch}'.")
                self.colors.info(" Usa REBASE para integrar cambios a tu feature.")
                return

            remote_check = self.git.run_git_command(
                f"git ls-remote --heads origin {current_branch}", allow_failure=True
            )

            if not remote_check["stdout"].strip():
                self.colors.warning(f"La rama {current_branch} no existe en remoto.")
                self.colors.info(" Creando rama en remoto...")
                self.git.run_git_command(f"git push --set-upstream origin {current_branch}")
                self.colors.success(f"Rama {current_branch} publicada.")
                return

            status = self.git.run_git_command("git status --porcelain")
            has_changes = bool(status["stdout"].strip())

            if has_changes:
                self.colors.warning("Hay cambios locales sin commitear.")
                if self.git.confirm_action("¿Guardar cambios antes del pull?"):
                    from src.git.managers.GitStashManager import GitStashManager
                    stash_manager = GitStashManager(self.git)
                    stash_manager.save_changes_locally()
                    self._do_pull(current_branch)
                    stash_manager.restore_local_changes()
                else:
                    self._do_pull(current_branch)
            else:
                self._do_pull(current_branch)

        except Exception as e:
            self.colors.error(f"Error al hacer pull: {str(e)}")
            self.git_logger.log_error(str(e), "pull_current_branch")

    def pull_base_branch(self) -> None:
        """Hace pull directo de la rama base sin importar conflictos"""
        self.git.ask_pass()

        try:
            self.colors.info(
                f"⚡ Pull directo de {Fore.BLUE}{self.base_branch}{Fore.RESET}..."
            )
            
            pull_result = self.git.run_git_command(
                f"git pull origin {self.base_branch}", allow_failure=True
            )

            if pull_result["returncode"] == 0:
                self.colors.success(
                    f"PULL EXITOSO: Cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} descargados"
                )
                self.git_logger.log_pull_operation(self.base_branch, "SUCCESS")
            else:
                error_msg = pull_result.get('stderr', '') or pull_result.get('stdout', '')
                self.colors.warning(f"Pull ejecutado con advertencias: {error_msg}")
                self.git_logger.log_pull_operation(self.base_branch, "WARNING")

        except Exception as e:
            self.colors.error(f"Error al hacer pull directo: {str(e)}")
            self.git_logger.log_error(str(e), "pull_base_branch")

    def _do_pull(self, branch: str) -> None:
        """Ejecuta el pull con rebase"""
        pull_result = self.git.run_git_command(
            f"git pull --rebase origin {branch}", allow_failure=True
        )

        if pull_result["returncode"] == 0:
            self.colors.success(
                f"PULL EXITOSO: Cambios descargados en {Fore.YELLOW}{branch}{Fore.RESET}"
            )
            self.git_logger.log_pull_operation(branch, "SUCCESS")
        else:
            if "CONFLICT" in pull_result.get("stdout", "") + pull_result.get(
                "stderr", ""
            ):
                self.colors.error("Hay conflictos durante el pull.")
                self.colors.info(
                    " Resuelve los conflictos y ejecuta: git rebase --continue"
                )
            else:
                self.colors.error(
                    f"Error durante el pull: {pull_result.get('stderr', '')}"
                )
            self.git_logger.log_pull_operation(branch, "ERROR")
