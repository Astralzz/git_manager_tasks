import datetime
from colorama import Fore
from src.consts.env import GIT_CONFIG_ID


class GitResetManager:
    """Clase para manejar operaciones de reset en Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de reset con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger
        self.base_branch = git_instance.base_branch
        self.feature_branch = git_instance.feature_branch

    def reset_to_base_with_backup(self) -> None:
        """Hace reset completo a la rama base con backup opcional"""
        self.git.ask_pass()

        try:
            current = self.git.run_git_command("git branch --show-current")
            current_branch = current["stdout"].strip()

            self.colors.info(f"\n RESET COMPLETO A RAMA BASE:")
            self.colors.info(f" Repo: {Fore.MAGENTA}{self.git.repo_path}{Fore.RESET}")
            self.colors.info(
                f" Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )
            self.colors.info(
                f" Resetear a: {Fore.BLUE}{self.base_branch}{Fore.RESET}"
            )

            status = self.git.run_git_command("git status --porcelain")
            has_changes = bool(status["stdout"].strip())

            if has_changes:
                self.colors.info(" Cambios detectados:")
                self.git.run_git_command("git status --short")

            if not self.git.confirm_action(
                f"ADVERTENCIA: Esta operación borrará TODOS tus cambios actuales.\n"
                f"Tu rama será una copia EXACTA de '{self.base_branch}'.\n"
                f"¿Continuar?"
            ):
                self.colors.info("Operación cancelada.")
                return

            backup_branch = "N/A"
            if self.git.confirm_action("¿Crear backup de los cambios actuales?"):
                backup_branch = self._create_backup_branch(has_changes)

            self._reset_to_base()

            self.colors.success("OPERACIÓN COMPLETADA")
            self.colors.success(
                f"📄 Rama actual: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
            )
            if backup_branch != "N/A":
                self.colors.success(
                    f"💾 Backup en: {Fore.GREEN}{backup_branch}{Fore.RESET}"
                )
                self.colors.info(f" Para recuperar: git checkout {backup_branch}")

            self.git_logger.log_operation(
                "RESET_TO_BASE",
                f"Reset a {self.base_branch}, backup: {backup_branch}",
                "SUCCESS",
            )

            self.colors.info("\n📊 Estado final:")
            self.git.run_git_command("git status")

        except Exception as e:
            self.colors.error(f"Error durante reset: {str(e)}")
            self.git_logger.log_error(str(e), "reset_to_base_with_backup")

    def _create_backup_branch(self, has_changes: bool) -> str:
        """Crea una rama de backup con los cambios actuales"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_branch = f"{self.feature_branch}_backup_{timestamp}"

        if has_changes:
            self.colors.info("💾 Guardando cambios no commiteados...")
            stash_msg = f"Backup antes de reset - {timestamp}"
            self.git.run_git_command(f'git stash push -m "{stash_msg}"')

        self.colors.info(f" Creando rama de backup: {backup_branch}")
        self.git.run_git_command(f"git checkout -b {backup_branch}")

        if has_changes:
            self.colors.info(" Aplicando cambios guardados...")
            self.git.run_git_command("git stash pop")
            self.git.run_git_command("git add .")
            commit_msg = f"Backup de cambios antes de reset - {timestamp}"
            self.git.run_git_command(f'git commit -m "{commit_msg}"')

        self.colors.warning(f"El backup '{backup_branch}' es solo local.")
        return backup_branch

    def _reset_to_base(self) -> None:
        """Resetea la rama feature a la rama base de forma forzada"""
        base_check = self.git.run_git_command(
            f"git rev-parse --verify {self.base_branch}", allow_failure=True
        )

        if base_check["returncode"] != 0:
            self.colors.warning(f"Descargando rama base '{self.base_branch}'...")
            self.git.run_git_command(
                f"git fetch origin {self.base_branch}:{self.base_branch}"
            )

        self.colors.info(f" Actualizando {self.base_branch}...")
        self.git.run_git_command(f"git checkout {self.base_branch}")
        self.git.run_git_command("git fetch origin")
        self.git.run_git_command(f"git reset --hard origin/{self.base_branch}")

        self.colors.info(f" Reseteando {self.feature_branch}...")

        feature_exists = self.git.run_git_command(
            f"git rev-parse --verify {self.feature_branch}", allow_failure=True
        )

        if feature_exists["returncode"] == 0:
            self.colors.info("🗑️ Descartando TODOS los cambios locales...")
            
            self.git.run_git_command("git clean -fd")
            self.git.run_git_command("git reset --hard HEAD")
            self.git.run_git_command("git stash clear", allow_failure=True)
            
            checkout_result = self.git.run_git_command(f"git checkout -f {self.feature_branch}", allow_failure=True)
            
            if checkout_result["returncode"] != 0:
                self.colors.warning("Recreando rama feature desde cero...")
                self.git.run_git_command(f"git branch -D {self.feature_branch}", allow_failure=True)
                self.git.run_git_command(f"git checkout -b {self.feature_branch}")
            else:
                self.git.run_git_command(f"git reset --hard {self.base_branch}")
        else:
            self.git.run_git_command(f"git checkout -b {self.feature_branch}")
        
        self.colors.info("🧹 Limpieza final...")
        self.git.run_git_command("git clean -fd")
