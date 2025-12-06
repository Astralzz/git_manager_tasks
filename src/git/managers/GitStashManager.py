import datetime


class GitStashManager:
    """Clase para manejar operaciones de stash en Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de stash con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger

    def save_changes_locally(self) -> None:
        """Guarda los cambios locales usando stash"""
        status = self.git.run_git_command("git status --porcelain", allow_failure=True)
        if not status["stdout"].strip():
            self.colors.warning(" No hay cambios locales para guardar.")
            return

        self.colors.info(" Cambios que se guardarán:")
        self.git.run_git_command("git status --short")

        stash_message = input(" Escribe el mensaje del stash: ").strip()
        if not stash_message:
            stash_message = (
                f"Auto-stash {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        self.git_logger.log_user_input("stash_message", stash_message)

        self.git.run_git_command(f'git stash push -m "{stash_message}"')
        self.colors.success(" Cambios guardados localmente con stash.")
        self.git_logger.log_stash_operation("save", stash_message, "SUCCESS")

    def restore_local_changes(self) -> None:
        """Restaura los cambios guardados con stash"""
        result = self.git.run_git_command("git stash list", allow_failure=True)

        if not result["stdout"].strip():
            self.colors.warning(" No hay stash para aplicar.")
            return

        self.colors.info(" Último stash:")
        self.git.run_git_command("git stash show -p stash@{0}")

        if not self.git.confirm_action("¿Deseas aplicar este stash?"):
            return

        stash_result = self.git.run_git_command("git stash pop", allow_failure=True)

        if stash_result["returncode"] == 0:
            self.colors.success("Cambios locales restaurados.")
            self.git_logger.log_stash_operation("pop", "", "SUCCESS")
        else:
            self.colors.error("Error al aplicar stash. Puede haber conflictos.")
            self.git_logger.log_stash_operation("pop", "", "ERROR")
