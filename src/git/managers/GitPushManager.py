from typing import TYPE_CHECKING
from colorama import Fore

if TYPE_CHECKING:
    from src.types.configTypes import GitCommandResult


class GitPushManager:
    """Clase para manejar operaciones de push y commit en Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de push con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger

    def upload_changes(self) -> None:
        """Sube los cambios al repositorio remoto"""
        self.git.ask_pass()

        try:
            branch_result = self.git.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"].strip()

            status = self.git.run_git_command("git status --porcelain")
            has_uncommitted_changes = bool(status["stdout"].strip())

            upstream_result = self.git.run_git_command(
                f"git config branch.{current_branch}.remote", allow_failure=True
            )
            has_upstream = upstream_result["returncode"] == 0 and bool(
                upstream_result["stdout"].strip()
            )

            commits_to_push = self._count_pending_commits(current_branch, has_upstream)

            if not has_uncommitted_changes and commits_to_push == 0:
                self.colors.warning(
                    " No hay cambios para subir. Todo está sincronizado."
                )
                return

            if has_uncommitted_changes:
                if not self._commit_changes():
                    return
                commits_to_push += 1

            if commits_to_push > 0:
                self._push_changes(current_branch, has_upstream, commits_to_push)

        except Exception as e:
            self.colors.error(f"Error al subir cambios: {str(e)}")
            self.git_logger.log_error(str(e), "upload_changes")

    def _count_pending_commits(self, branch: str, has_upstream: bool) -> int:
        """Cuenta los commits pendientes de push"""
        if has_upstream:
            ahead_result = self.git.run_git_command(
                f"git rev-list --count origin/{branch}..HEAD", allow_failure=True
            )
            if ahead_result["returncode"] == 0:
                return int(ahead_result["stdout"].strip() or 0)
        else:
            commit_count = self.git.run_git_command(
                "git rev-list --count HEAD", allow_failure=True
            )
            if commit_count["returncode"] == 0:
                return int(commit_count["stdout"].strip() or 0)
        return 0

    def _commit_changes(self) -> bool:
        """Realiza commit de los cambios pendientes"""
        self.colors.info(" Cambios detectados sin commitear:")
        self.git.run_git_command("git status --short")

        commit_message = input(" Mensaje del commit: ").strip()
        if not commit_message:
            self.colors.warning(" No se escribió mensaje de commit.")
            self.git_logger.log_warning(
                "No se escribió mensaje de commit", "upload_changes"
            )
            return False

        self.git_logger.log_user_input("commit_message", commit_message)

        self.git.run_git_command("git add .")
        self.git.run_git_command(f'git commit -m "{commit_message}"')
        self.colors.success("Commit realizado exitosamente.")
        return True

    def _push_changes(
        self, branch: str, has_upstream: bool, commits_count: int
    ) -> None:
        """Sube los cambios al remoto"""
        self.colors.info(f" Subiendo {commits_count} commit(s) en '{branch}'")

        self._show_pending_commits(branch, has_upstream, commits_count)

        if not has_upstream:
            self._setup_upstream(branch)
        else:
            if not self._check_sync_before_push(branch):
                return

        push_result = self.git.run_git_command("git push", allow_failure=True)

        if push_result["returncode"] == 0:
            self._handle_push_success(branch)
        else:
            self._handle_push_error(branch, push_result)

    def _show_pending_commits(
        self, branch: str, has_upstream: bool, count: int
    ) -> None:
        """Muestra los commits pendientes de push"""
        if has_upstream:
            commits = self.git.run_git_command(
                f"git log origin/{branch}..HEAD --oneline", allow_failure=True
            )
        else:
            commits = self.git.run_git_command(
                f"git log --oneline -n {min(count, 5)}", allow_failure=True
            )

        if commits["returncode"] == 0 and commits["stdout"]:
            self.colors.info(" Commits pendientes:")
            print(commits["stdout"])

    def _setup_upstream(self, branch: str) -> None:
        """Configura el upstream para una rama"""
        self.colors.info(f"📡 Configurando upstream para '{branch}'...")

        self.git.run_git_command("git fetch origin")

        remote_check = self.git.run_git_command(
            f"git ls-remote --heads origin {branch}", allow_failure=True
        )

        if remote_check["stdout"].strip():
            self.colors.info(f"🔗 La rama existe en remoto. Configurando...")
            self.git.run_git_command(
                f"git branch --set-upstream-to=origin/{branch} {branch}"
            )
        else:
            self.colors.info(f"🆕 Creando rama en remoto...")
            self.git.run_git_command(f"git push --set-upstream origin {branch}")

    def _check_sync_before_push(self, branch: str) -> bool:
        """Verifica sincronización antes de hacer push"""
        self.colors.info(f" Verificando sincronización de '{branch}'...")

        self.git.run_git_command("git fetch origin")

        behind = self.git.run_git_command(
            f"git rev-list --count HEAD..origin/{branch}", allow_failure=True
        )

        if behind["returncode"] == 0:
            behind_count = int(behind["stdout"].strip() or 0)
            if behind_count > 0:
                self.colors.warning(
                    f" Tu rama está {behind_count} commit(s) detrás del remoto."
                )

                if self.git.confirm_action("¿Hacer pull primero?"):
                    pull_result = self.git.run_git_command("git pull", allow_failure=True)

                    if "CONFLICT" in pull_result.get("stdout", "") + pull_result.get(
                        "stderr", ""
                    ):
                        self.colors.error("Hay conflictos. Resuélvelos manualmente.")
                        self.git_logger.log_error(
                            "Conflictos durante pull", "upload_changes"
                        )
                        return False

        return True

    def _handle_push_success(self, branch: str) -> None:
        """Maneja el éxito del push"""
        self.colors.success("Cambios subidos exitosamente.")

        last_commit = self.git.run_git_command("git log -1 --oneline", allow_failure=True)
        commit_msg = (
            last_commit["stdout"].strip() if last_commit["stdout"] else "Unknown"
        )

        self.git_logger.log_push_operation(branch, commit_msg, "SUCCESS")

        self.colors.info(f"📊 Rama: {branch}")
        self.colors.info(f" Último commit: {commit_msg}")

    def _handle_push_error(self, branch: str, result: "GitCommandResult") -> None:
        """Maneja errores de push"""
        error_msg = result.get("stderr", "")

        if "rejected" in error_msg:
            self.colors.error("Push rechazado. Necesitas hacer pull primero.")
            self.colors.info(f" Intenta: git pull --rebase origin {branch}")
            self.git_logger.log_push_operation(branch, "Push rejected", "WARNING")
        elif "Everything up-to-date" in result.get("stdout", ""):
            self.colors.info("Todo está actualizado.")
        else:
            self.colors.error(f"Error al hacer push: {error_msg}")
            self.git_logger.log_error(error_msg, "upload_changes")
