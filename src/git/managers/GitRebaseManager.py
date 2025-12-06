from colorama import Fore


class GitRebaseManager:
    """Clase para manejar operaciones de rebase en Git"""

    def __init__(self, git_instance):
        """Inicializa el gestor de rebase con una instancia de GitClass"""
        self.git = git_instance
        self.colors = git_instance.colors
        self.git_logger = git_instance.git_logger
        self.base_branch = git_instance.base_branch
        self.feature_branch = git_instance.feature_branch

    def handle_rebase(self) -> None:
        """Integra los cambios de la rama base a la rama feature"""
        self.colors.info(
            f" REBASE: Integrando cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} → {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
        )
        
        status = self.git.run_git_command("git status --porcelain", allow_failure=True)
        has_local_changes = bool(status["stdout"].strip())
        
        stashed = False
        if has_local_changes:
            if self.git.confirm_action("¿Quieres guardar tus cambios locales antes del rebase?"):
                from src.git.managers.GitStashManager import GitStashManager
                stash_manager = GitStashManager(self.git)
                stash_manager.save_changes_locally()
                stashed = True
        
        try:
            self.colors.info(f" Actualizando {self.base_branch} desde remoto...")
            self.git.run_git_command(f"git fetch origin {self.base_branch}:{self.base_branch}")
            
            self.colors.info(f" Aplicando rebase...")
            self.git.run_git_command(f"git rebase {self.base_branch}")
            
            self.colors.success("REBASE EXITOSO: Cambios integrados")
            
        except Exception as e:
            self.colors.error(f"Error en rebase: {str(e)}")
            
        finally:
            if stashed:
                from src.git.managers.GitStashManager import GitStashManager
                stash_manager = GitStashManager(self.git)
                stash_manager.restore_local_changes()

    def get_latest_changes(self) -> None:
        """Hace rebase de la rama base a la rama feature"""
        self.colors.info(f"\n PROCESO DE REBASE:")
        self.colors.info(f" Repo: {Fore.MAGENTA}{self.git.repo_path}{Fore.RESET}")
        self.colors.info(
            f" Rama feature: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
        )
        self.colors.info(
            f" Integrando desde: {Fore.BLUE}{self.base_branch}{Fore.RESET}\n"
        )

        checkout_result = self.git.run_git_command(
            f"git checkout {self.feature_branch}", allow_failure=True
        )

        if checkout_result["returncode"] != 0:
            self.colors.error(f"No se pudo cambiar a la rama {self.feature_branch}")
            return

        self.git.run_git_command("git fetch origin")

        base_check = self.git.run_git_command(
            f"git rev-parse --verify {self.base_branch}", allow_failure=True
        )

        if base_check["returncode"] != 0:
            self.colors.warning(
                f"Descargando rama base '{self.base_branch}' desde remoto..."
            )
            fetch_result = self.git.run_git_command(
                f"git fetch origin {self.base_branch}:{self.base_branch}",
                allow_failure=True,
            )
            if fetch_result["returncode"] != 0:
                self.colors.error(f"No se pudo obtener la rama '{self.base_branch}'")
                return

        rebase_result = self.git.run_git_command(
            f"git rebase {self.base_branch}", allow_failure=True
        )

        if rebase_result["returncode"] == 0:
            self.colors.success(
                f"REBASE EXITOSO: Cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} integrados"
            )
            self.git_logger.log_rebase_operation(
                self.base_branch, self.feature_branch, "SUCCESS"
            )
        else:
            if "CONFLICT" in rebase_result.get("stdout", "") + rebase_result.get(
                "stderr", ""
            ):
                self.colors.error("Hay conflictos durante el rebase.")
                self.colors.info(" Resuelve los conflictos y ejecuta:")
                self.colors.info("   git add <archivos resueltos>")
                self.colors.info("   git rebase --continue")
                self.colors.info("   O usa la opción 9 para cancelar el rebase")
            else:
                self.colors.error(
                    f"Error durante el rebase: {rebase_result.get('stderr', '')}"
                )

            self.git_logger.log_rebase_operation(
                self.base_branch, self.feature_branch, "ERROR"
            )

    def cancel_rebase(self) -> None:
        """Cancela un rebase en progreso"""
        self.git.ask_pass()

        abort_result = self.git.run_git_command("git rebase --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("Rebase cancelado exitosamente.")
            self.git_logger.log_operation(
                "REBASE_CANCEL", "Rebase cancelado", "SUCCESS"
            )
        else:
            self.colors.warning("No hay rebase en progreso para cancelar.")

    def update_base_branch(self) -> None:
        """Actualiza la rama base con los últimos cambios del remoto"""
        self.git.ask_pass()

        try:
            current_result = self.git.run_git_command("git branch --show-current")
            current_branch = current_result["stdout"].strip()

            self.colors.info(f"\n ACTUALIZANDO RAMA BASE:")
            self.colors.info(f" Repo: {Fore.MAGENTA}{self.git.repo_path}{Fore.RESET}")
            self.colors.info(
                f" Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )
            self.colors.info(
                f" Actualizando: {Fore.BLUE}{self.base_branch}{Fore.RESET}"
            )

            status = self.git.run_git_command("git status --porcelain", allow_failure=True)
            has_local_changes = bool(status["stdout"].strip())

            if has_local_changes:
                self.colors.warning("Hay cambios locales sin commitear.")
                if self.git.confirm_action("¿Guardar cambios antes de actualizar la base?"):
                    from src.git.managers.GitStashManager import GitStashManager
                    stash_manager = GitStashManager(self.git)
                    stash_manager.save_changes_locally()

            base_check = self.git.run_git_command(
                f"git rev-parse --verify {self.base_branch}", allow_failure=True
            )

            if base_check["returncode"] != 0:
                self.colors.warning(
                    f"Descargando rama base '{self.base_branch}' desde remoto..."
                )
                self.git.run_git_command(
                    f"git fetch origin {self.base_branch}:{self.base_branch}"
                )

            self.colors.info(f" Cambiando a {self.base_branch}...")
            checkout_result = self.git.run_git_command(
                f"git checkout {self.base_branch}", allow_failure=True
            )

            if checkout_result["returncode"] != 0:
                self.colors.error(f"Error al cambiar a la rama {self.base_branch}")
                return

            self.colors.info("📡 Actualizando referencias remotas...")
            self.git.run_git_command("git fetch origin")

            self.colors.info(f" Descargando últimos cambios de {self.base_branch}...")

            ahead_result = self.git.run_git_command(
                f"git rev-list --count origin/{self.base_branch}..HEAD",
                allow_failure=True,
            )

            has_local_commits = False
            if ahead_result["returncode"] == 0:
                ahead_count = int(ahead_result["stdout"].strip() or 0)
                has_local_commits = ahead_count > 0

            if has_local_commits:
                self.colors.warning(
                    f"La rama {self.base_branch} tiene commits locales."
                )
                if self.git.confirm_action(
                    f"¿Hacer reset hard a origin/{self.base_branch}? (Se perderán los commits locales)"
                ):
                    self.git.run_git_command(f"git reset --hard origin/{self.base_branch}")
                    self.colors.success(
                        f"Rama {self.base_branch} reseteada a la versión remota."
                    )
                else:
                    merge_result = self.git.run_git_command(
                        f"git merge origin/{self.base_branch}", allow_failure=True
                    )
                    if merge_result["returncode"] == 0:
                        self.colors.success(f"Merge exitoso en {self.base_branch}.")
                    else:
                        self.colors.error(
                            "Error durante el merge. Resuelve conflictos manualmente."
                        )
                        return
            else:
                self.git.run_git_command(f"git reset --hard origin/{self.base_branch}")
                self.colors.success(
                    f"Rama {self.base_branch} actualizada exitosamente."
                )

            last_commit = self.git.run_git_command(
                "git log -1 --oneline", allow_failure=True
            )
            if last_commit["stdout"]:
                self.colors.info(f" Último commit: {last_commit['stdout'].strip()}")

            if current_branch != self.base_branch:
                self.colors.info(f" Regresando a {current_branch}...")
                return_result = self.git.run_git_command(
                    f"git checkout {current_branch}", allow_failure=True
                )

                if return_result["returncode"] == 0:
                    self.colors.success(
                        f"De vuelta en: {Fore.YELLOW}{current_branch}{Fore.RESET}"
                    )

                    if has_local_changes:
                        if self.git.confirm_action("¿Restaurar los cambios guardados?"):
                            from src.git.managers.GitStashManager import GitStashManager
                            stash_manager = GitStashManager(self.git)
                            stash_manager.restore_local_changes()
                else:
                    self.colors.error(f"Error al regresar a {current_branch}")

            self.git_logger.log_operation(
                "UPDATE_BASE_BRANCH",
                f"Rama base {self.base_branch} actualizada",
                "SUCCESS",
            )

            if current_branch == self.feature_branch:
                self.colors.info(
                    " Recomendación: Considera hacer REBASE para integrar los nuevos cambios."
                )

        except Exception as e:
            self.colors.error(f"Error al actualizar rama base: {str(e)}")
            self.git_logger.log_error(str(e), "update_base_branch")
