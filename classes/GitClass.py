import os
import subprocess
import sys
import datetime
from colorama import Fore
from typing import Dict, Optional, List

from classes.GlobalClass import GlobalClass
from classes.GitLogClass import GitLogClass


class GitClass(GlobalClass):
    """Clase para manejar operaciones Git de forma interactiva y segura"""

    def __init__(self, config: dict):
        """
        Inicializa la clase GitClass con la configuración proporcionada

        Args:
            config: Diccionario con la configuración del repositorio
        """
        self.config = config
        self.repo_path = config.get("repo_path")

        # Inicializa la clase padre
        super().__init__()

        # Inicializa el sistema de logs
        self.logger = GitLogClass(self.repo_path)

        # Valida los campos requeridos
        self.validate_required_fields(["base_branch", "feature_branch"], self.repo_path)

        # Obtiene las ramas del repositorio
        self.base_branch = config.get("base_branch")
        self.feature_branch = config.get("feature_branch")

        # Validaciones de seguridad
        self._validate_branch_configuration()

        # Intentar cambiar automáticamente a la rama feature
        self._auto_checkout_to_feature_branch()

        # Registra el inicio del programa
        self.logger.log_program_start(self.config)

    def _validate_branch_configuration(self) -> None:
        """Valida que la configuración de ramas sea correcta"""
        # La rama feature nunca debe ser main o master
        if self.feature_branch.lower() in ["main", "master"]:
            self.colors.error(
                f"❌ La rama feature no puede ser '{self.feature_branch}'."
            )
            self.logger.log_error(
                f"Configuración inválida: feature_branch = {self.feature_branch}",
                "_validate_branch_configuration",
            )
            sys.exit(1)

        # Las ramas no pueden ser iguales
        if self.base_branch == self.feature_branch:
            self.colors.error(
                "❌ La rama base y la rama feature no pueden ser iguales."
            )
            self.logger.log_error(
                "Configuración inválida: base_branch == feature_branch",
                "_validate_branch_configuration",
            )
            sys.exit(1)

    def run_git_command(
        self, command: str, allow_failure: bool = False
    ) -> Dict[str, any]:
        """
        Ejecuta un comando git y retorna la salida

        Args:
            command: El comando git a ejecutar
            allow_failure: Si True, no termina el programa en caso de error

        Returns:
            Diccionario con returncode, stdout y stderr
        """
        try:
            # Muestra el comando a ejecutar
            self.colors.info(f"▶ Ejecutando: {command}")

            # Ejecuta el comando
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )

            # Maneja la salida según el resultado
            if result.returncode == 0:
                if result.stdout.strip():
                    self.colors.success(f"✅ {result.stdout.strip()}")
            else:
                # Solo muestra error si no se permite fallo
                if not allow_failure:
                    if result.stderr.strip():
                        self.colors.error(f"❌ Error: {result.stderr.strip()}")

            # Prepara el resultado
            result_dict = {
                "returncode": result.returncode,
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
            }

            # Registra el comando en el log
            self.logger.log_git_command(command, result_dict)

            # Si hubo error y no se permite fallo, termina el programa
            if result.returncode != 0 and not allow_failure:
                self.logger.log_error(
                    f"Error al ejecutar comando: {result.stderr}", "run_git_command"
                )
                sys.exit(1)

            return result_dict

        except Exception as e:
            # Maneja excepciones inesperadas
            self.colors.error(f"❌ Error inesperado: {str(e)}")

            error_result = {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
            }

            self.logger.log_git_command(command, error_result)
            self.logger.log_error(f"Error inesperado: {str(e)}", "run_git_command")

            if not allow_failure:
                sys.exit(1)

            return error_result

    def _auto_checkout_to_feature_branch(self) -> None:
        """
        Intenta cambiar automáticamente a la rama feature configurada.
        Si no existe, muestra información útil pero no falla.
        """
        try:
            # Obtener la rama actual
            result = self.run_git_command(
                "git branch --show-current", allow_failure=True
            )
            current_branch = result["stdout"].strip()

            # Si ya estamos en la rama feature, no hacer nada
            if current_branch == self.feature_branch:
                self.colors.success(
                    f"✅ Ya estás en la rama feature: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                )
                return

            # Verificar si la rama feature existe localmente
            check_local = self.run_git_command(
                f"git rev-parse --verify --quiet {self.feature_branch}",
                allow_failure=True,
            )

            if check_local["returncode"] == 0:
                # La rama existe localmente, hacer checkout
                self.colors.info(
                    f"🔄 Cambiando a la rama feature: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                )
                checkout_result = self.run_git_command(
                    f"git checkout {self.feature_branch}", allow_failure=True
                )

                if checkout_result["returncode"] == 0:
                    self.colors.success(
                        f"✅ Posicionado en la rama: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                    )
                    self.logger.log_operation(
                        "AUTO_CHECKOUT",
                        f"Cambio automático a {self.feature_branch}",
                        "SUCCESS",
                    )
                else:
                    self.colors.warning(
                        f"⚠️ No se pudo cambiar a la rama {self.feature_branch}"
                    )
                    self.colors.info(
                        f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}"
                    )
            else:
                # Verificar en remoto
                self._check_remote_branch(current_branch)

        except Exception as e:
            self.colors.warning(f"⚠️ Error al verificar rama: {str(e)}")
            self.colors.info("💡 El programa continuará normalmente.")

    def _check_remote_branch(self, current_branch: str) -> None:
        """Verifica si la rama existe en remoto y la descarga si es posible"""
        check_remote = self.run_git_command(
            f"git ls-remote --heads origin {self.feature_branch}", allow_failure=True
        )

        if check_remote["stdout"].strip():
            # Existe en remoto, intentar descargar
            self.colors.info(
                f"📥 La rama {Fore.YELLOW}{self.feature_branch}{Fore.RESET} existe en remoto. Descargando..."
            )

            checkout_remote = self.run_git_command(
                f"git checkout -b {self.feature_branch} origin/{self.feature_branch}",
                allow_failure=True,
            )

            if checkout_remote["returncode"] == 0:
                self.colors.success(
                    f"✅ Rama descargada y posicionado en: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                )
                self.logger.log_operation(
                    "AUTO_CHECKOUT_REMOTE",
                    f"Descarga y cambio a {self.feature_branch} desde remoto",
                    "SUCCESS",
                )
            else:
                # Intentar con --track
                track_result = self.run_git_command(
                    f"git checkout --track origin/{self.feature_branch}",
                    allow_failure=True,
                )
                if track_result["returncode"] == 0:
                    self.colors.success(
                        f"✅ Rama rastreada: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                    )
                else:
                    self.colors.warning(f"⚠️ No se pudo descargar la rama remota")
                    self.colors.info(
                        f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}"
                    )
        else:
            # Nueva tarea detectada
            self._show_new_task_info(current_branch)

    def _show_new_task_info(self, current_branch: str) -> None:
        """Muestra información cuando se detecta una nueva tarea"""
        self.colors.info("━" * 60)
        self.colors.warning("📝 NUEVA TAREA DETECTADA")
        self.colors.info(
            f"   La rama {Fore.YELLOW}{self.feature_branch}{Fore.RESET} no existe aún."
        )
        self.colors.info(
            f"   Actualmente estás en: {Fore.CYAN}{current_branch}{Fore.RESET}"
        )
        self.colors.info(
            "   Usa la opción 6 del menú para crear la rama cuando estés listo."
        )
        self.colors.info("━" * 60)
        self.logger.log_operation(
            "NEW_TASK_DETECTED",
            f"Nueva tarea detectada: {self.feature_branch} no existe",
            "INFO",
        )

    def display_git_menu(self) -> None:
        """Muestra el menú de opciones de forma persistente"""
        options = [
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
                "function": self.delete_branch,
                "description": "🗑️ Eliminar una rama por nombre",
            },
            {
                "function": self.cancel_rebase,
                "description": "❌ Cancelar rebase en progreso",
            },
            {"function": self.view_today_logs, "description": "📋 Ver logs de hoy"},
        ]
        self.show_menu(options)

    def _handle_rebase(self) -> None:
        """Integra los cambios de la rama base a la rama feature"""
        self.colors.info(
            f"🔄 REBASE: Integrando cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} → {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
        )

        # Verificar cambios locales
        status = self.run_git_command("git status --porcelain", allow_failure=True)
        has_local_changes = bool(status["stdout"].strip())

        if has_local_changes:
            if self.confirm_action(
                "¿Quieres guardar tus cambios locales antes del rebase?"
            ):
                self.save_changes_locally()
                self.get_latest_changes()
                self.restore_local_changes()
            else:
                self.get_latest_changes()
        else:
            self.colors.info(
                "✅ No hay cambios locales pendientes. Procediendo con el rebase..."
            )
            self.get_latest_changes()

    def get_repo_status(self) -> None:
        """Obtiene el estado del repositorio"""
        self.run_git_command("git status")

    def get_current_branch(self) -> None:
        """Muestra todas las ramas y marca la actual"""
        self.run_git_command("git branch")

    def restore_local_changes(self) -> None:
        """Restaura los cambios guardados con stash"""
        # Verificar si hay stash
        result = self.run_git_command("git stash list", allow_failure=True)

        if not result["stdout"].strip():
            self.colors.warning("⚠ No hay stash para aplicar.")
            return

        # Mostrar el último stash
        self.colors.info("📦 Último stash:")
        self.run_git_command("git stash show -p stash@{0}")

        if not self.confirm_action("¿Deseas aplicar este stash?"):
            return

        # Aplicar el stash
        stash_result = self.run_git_command("git stash pop", allow_failure=True)

        if stash_result["returncode"] == 0:
            self.colors.success("✅ Cambios locales restaurados.")
            self.logger.log_stash_operation("pop", "", "SUCCESS")
        else:
            self.colors.error("❌ Error al aplicar stash. Puede haber conflictos.")
            self.logger.log_stash_operation("pop", "", "ERROR")

    def save_changes_locally(self) -> None:
        """Guarda los cambios locales usando stash"""
        # Verificar si hay cambios
        status = self.run_git_command("git status --porcelain", allow_failure=True)
        if not status["stdout"].strip():
            self.colors.warning("⚠ No hay cambios locales para guardar.")
            return

        # Mostrar cambios
        self.colors.info("📋 Cambios que se guardarán:")
        self.run_git_command("git status --short")

        # Pedir mensaje
        stash_message = input("📝 Escribe el mensaje del stash: ").strip()
        if not stash_message:
            stash_message = (
                f"Auto-stash {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        self.logger.log_user_input("stash_message", stash_message)

        # Guardar cambios
        self.run_git_command(f'git stash push -m "{stash_message}"')
        self.colors.success("📦 Cambios guardados localmente con stash.")
        self.logger.log_stash_operation("save", stash_message, "SUCCESS")

    def get_latest_changes(self) -> None:
        """Hace rebase de la rama base a la rama feature"""
        self.colors.info(f"\n🔄 PROCESO DE REBASE:")
        self.colors.info(f"📁 Repo: {Fore.MAGENTA}{self.repo_path}{Fore.RESET}")
        self.colors.info(
            f"🌿 Rama feature: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
        )
        self.colors.info(
            f"📥 Integrando desde: {Fore.BLUE}{self.base_branch}{Fore.RESET}\n"
        )

        # Cambiar a la rama feature
        checkout_result = self.run_git_command(
            f"git checkout {self.feature_branch}", allow_failure=True
        )

        if checkout_result["returncode"] != 0:
            self.colors.error(f"❌ No se pudo cambiar a la rama {self.feature_branch}")
            return

        # Actualizar referencias remotas
        self.run_git_command("git fetch origin")

        # Verificar si la rama base existe localmente
        base_check = self.run_git_command(
            f"git rev-parse --verify {self.base_branch}", allow_failure=True
        )

        if base_check["returncode"] != 0:
            self.colors.warning(
                f"⚠️ Descargando rama base '{self.base_branch}' desde remoto..."
            )
            fetch_result = self.run_git_command(
                f"git fetch origin {self.base_branch}:{self.base_branch}",
                allow_failure=True,
            )
            if fetch_result["returncode"] != 0:
                self.colors.error(f"❌ No se pudo obtener la rama '{self.base_branch}'")
                return

        # Ejecutar rebase
        rebase_result = self.run_git_command(
            f"git rebase {self.base_branch}", allow_failure=True
        )

        if rebase_result["returncode"] == 0:
            self.colors.success(
                f"✅ REBASE EXITOSO: Cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} integrados"
            )
            self.logger.log_rebase_operation(
                self.base_branch, self.feature_branch, "SUCCESS"
            )
        else:
            if "CONFLICT" in rebase_result.get("stdout", "") + rebase_result.get(
                "stderr", ""
            ):
                self.colors.error("❌ Hay conflictos durante el rebase.")
                self.colors.info("💡 Resuelve los conflictos y ejecuta:")
                self.colors.info("   git add <archivos resueltos>")
                self.colors.info("   git rebase --continue")
                self.colors.info("   O usa la opción 9 para cancelar el rebase")
            else:
                self.colors.error(
                    f"❌ Error durante el rebase: {rebase_result.get('stderr', '')}"
                )

            self.logger.log_rebase_operation(
                self.base_branch, self.feature_branch, "ERROR"
            )

    def create_branch_feature(self) -> None:
        """Crea una nueva rama feature desde la rama actual"""
        self.ask_pass()

        # Verificar si ya existe localmente
        local_check = self.run_git_command(
            f"git rev-parse --verify --quiet {self.feature_branch}", allow_failure=True
        )

        if local_check["returncode"] == 0:
            self.colors.warning(
                f"⚠️ La rama '{self.feature_branch}' ya existe localmente."
            )
            return

        # Verificar si existe en remoto
        remote_check = self.run_git_command(
            f"git ls-remote --heads origin {self.feature_branch}", allow_failure=True
        )

        if remote_check["stdout"].strip():
            self.colors.warning(
                f"⚠️ La rama '{self.feature_branch}' ya existe en remoto."
            )
            self.colors.info("💡 Usa git checkout para cambiar a ella.")
            return

        # Crear la rama
        self.colors.info(f"🌿 Creando nueva rama: {self.feature_branch}")
        create_result = self.run_git_command(
            f"git checkout -b {self.feature_branch}", allow_failure=True
        )

        if create_result["returncode"] == 0:
            self.colors.success(f"✅ Rama '{self.feature_branch}' creada exitosamente.")
            self.logger.log_branch_operation("create", self.feature_branch, "SUCCESS")
        else:
            self.colors.error(
                f"❌ Error al crear la rama: {create_result.get('stderr', '')}"
            )
            self.logger.log_branch_operation("create", self.feature_branch, "ERROR")

    def delete_branch(self) -> None:
        """Elimina una rama específica"""
        self.ask_pass()

        branch_name = input("📝 Nombre de la rama a eliminar: ").strip()
        if not branch_name:
            self.colors.warning("⚠ No se especificó ninguna rama.")
            return

        # Verificar que no sea la rama actual
        current = self.run_git_command("git branch --show-current", allow_failure=True)
        if current["stdout"].strip() == branch_name:
            self.colors.error("❌ No puedes eliminar la rama en la que estás.")
            return

        # Verificar que no sea una rama protegida
        if branch_name.lower() in ["main", "master", "develop", "development"]:
            if not self.confirm_action(
                f"⚠️ '{branch_name}' es una rama protegida. ¿Seguro que deseas eliminarla?"
            ):
                return

        # Eliminar la rama
        delete_result = self.run_git_command(
            f"git branch -D {branch_name}", allow_failure=True
        )

        if delete_result["returncode"] == 0:
            self.colors.success(f"✅ Rama '{branch_name}' eliminada localmente.")
            self.logger.log_branch_operation("delete", branch_name, "SUCCESS")

            # Preguntar si eliminar del remoto también
            if self.confirm_action("¿Eliminar también del remoto?"):
                remote_delete = self.run_git_command(
                    f"git push origin --delete {branch_name}", allow_failure=True
                )
                if remote_delete["returncode"] == 0:
                    self.colors.success(f"✅ Rama eliminada del remoto.")
                else:
                    self.colors.warning("⚠️ No se pudo eliminar del remoto.")
        else:
            self.colors.error(
                f"❌ Error al eliminar la rama: {delete_result.get('stderr', '')}"
            )
            self.logger.log_branch_operation("delete", branch_name, "ERROR")

    def upload_changes(self) -> None:
        """Sube los cambios al repositorio remoto"""
        self.ask_pass()

        try:
            # Obtener rama actual
            branch_result = self.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"].strip()

            # Verificar cambios sin commitear
            status = self.run_git_command("git status --porcelain")
            has_uncommitted_changes = bool(status["stdout"].strip())

            # Verificar upstream
            upstream_result = self.run_git_command(
                f"git config branch.{current_branch}.remote", allow_failure=True
            )
            has_upstream = upstream_result["returncode"] == 0 and bool(
                upstream_result["stdout"].strip()
            )

            # Contar commits pendientes
            commits_to_push = self._count_pending_commits(current_branch, has_upstream)

            # Verificar si hay algo que subir
            if not has_uncommitted_changes and commits_to_push == 0:
                self.colors.warning(
                    "⚠ No hay cambios para subir. Todo está sincronizado."
                )
                return

            # Hacer commit si hay cambios
            if has_uncommitted_changes:
                if not self._commit_changes():
                    return
                commits_to_push += 1

            # Subir cambios
            if commits_to_push > 0:
                self._push_changes(current_branch, has_upstream, commits_to_push)

        except Exception as e:
            self.colors.error(f"❌ Error al subir cambios: {str(e)}")
            self.logger.log_error(str(e), "upload_changes")

    def _count_pending_commits(self, branch: str, has_upstream: bool) -> int:
        """Cuenta los commits pendientes de push"""
        if has_upstream:
            ahead_result = self.run_git_command(
                f"git rev-list --count origin/{branch}..HEAD", allow_failure=True
            )
            if ahead_result["returncode"] == 0:
                return int(ahead_result["stdout"].strip() or 0)
        else:
            commit_count = self.run_git_command(
                "git rev-list --count HEAD", allow_failure=True
            )
            if commit_count["returncode"] == 0:
                return int(commit_count["stdout"].strip() or 0)
        return 0

    def _commit_changes(self) -> bool:
        """Realiza commit de los cambios pendientes"""
        self.colors.info("📋 Cambios detectados sin commitear:")
        self.run_git_command("git status --short")

        commit_message = input("📝 Mensaje del commit: ").strip()
        if not commit_message:
            self.colors.warning("⚠ No se escribió mensaje de commit.")
            self.logger.log_warning(
                "No se escribió mensaje de commit", "upload_changes"
            )
            return False

        self.logger.log_user_input("commit_message", commit_message)

        self.run_git_command("git add .")
        self.run_git_command(f'git commit -m "{commit_message}"')
        self.colors.success("✅ Commit realizado exitosamente.")
        return True

    def _push_changes(
        self, branch: str, has_upstream: bool, commits_count: int
    ) -> None:
        """Sube los cambios al remoto"""
        self.colors.info(f"📤 Subiendo {commits_count} commit(s) en '{branch}'")

        # Mostrar commits pendientes
        self._show_pending_commits(branch, has_upstream, commits_count)

        if not has_upstream:
            # Configurar upstream si no existe
            self._setup_upstream(branch)
        else:
            # Verificar sincronización antes de push
            if not self._check_sync_before_push(branch):
                return

        # Hacer push
        push_result = self.run_git_command("git push", allow_failure=True)

        if push_result["returncode"] == 0:
            self._handle_push_success(branch)
        else:
            self._handle_push_error(branch, push_result)

    def _show_pending_commits(
        self, branch: str, has_upstream: bool, count: int
    ) -> None:
        """Muestra los commits pendientes de push"""
        if has_upstream:
            commits = self.run_git_command(
                f"git log origin/{branch}..HEAD --oneline", allow_failure=True
            )
        else:
            commits = self.run_git_command(
                f"git log --oneline -n {min(count, 5)}", allow_failure=True
            )

        if commits["returncode"] == 0 and commits["stdout"]:
            self.colors.info("📝 Commits pendientes:")
            print(commits["stdout"])

    def _setup_upstream(self, branch: str) -> None:
        """Configura el upstream para una rama"""
        self.colors.info(f"📡 Configurando upstream para '{branch}'...")

        # Actualizar referencias
        self.run_git_command("git fetch origin")

        # Verificar si existe en remoto
        remote_check = self.run_git_command(
            f"git ls-remote --heads origin {branch}", allow_failure=True
        )

        if remote_check["stdout"].strip():
            self.colors.info(f"🔗 La rama existe en remoto. Configurando...")
            self.run_git_command(
                f"git branch --set-upstream-to=origin/{branch} {branch}"
            )
        else:
            self.colors.info(f"🆕 Creando rama en remoto...")
            self.run_git_command(f"git push --set-upstream origin {branch}")

    def _check_sync_before_push(self, branch: str) -> bool:
        """Verifica sincronización antes de hacer push"""
        self.colors.info(f"📤 Verificando sincronización de '{branch}'...")

        # Actualizar referencias
        self.run_git_command("git fetch origin")

        # Verificar si estamos detrás
        behind = self.run_git_command(
            f"git rev-list --count HEAD..origin/{branch}", allow_failure=True
        )

        if behind["returncode"] == 0:
            behind_count = int(behind["stdout"].strip() or 0)
            if behind_count > 0:
                self.colors.warning(
                    f"⚠ Tu rama está {behind_count} commit(s) detrás del remoto."
                )

                if self.confirm_action("¿Hacer pull primero?"):
                    pull_result = self.run_git_command("git pull", allow_failure=True)

                    if "CONFLICT" in pull_result.get("stdout", "") + pull_result.get(
                        "stderr", ""
                    ):
                        self.colors.error("❌ Hay conflictos. Resuélvelos manualmente.")
                        self.logger.log_error(
                            "Conflictos durante pull", "upload_changes"
                        )
                        return False

        return True

    def _handle_push_success(self, branch: str) -> None:
        """Maneja el éxito del push"""
        self.colors.success("✅ Cambios subidos exitosamente.")

        # Obtener último commit
        last_commit = self.run_git_command("git log -1 --oneline", allow_failure=True)
        commit_msg = (
            last_commit["stdout"].strip() if last_commit["stdout"] else "Unknown"
        )

        self.logger.log_push_operation(branch, commit_msg, "SUCCESS")

        self.colors.info(f"📊 Rama: {branch}")
        self.colors.info(f"📝 Último commit: {commit_msg}")

    def _handle_push_error(self, branch: str, result: dict) -> None:
        """Maneja errores de push"""
        error_msg = result.get("stderr", "")

        if "rejected" in error_msg:
            self.colors.error("❌ Push rechazado. Necesitas hacer pull primero.")
            self.colors.info(f"💡 Intenta: git pull --rebase origin {branch}")
            self.logger.log_push_operation(branch, "Push rejected", "REJECTED")
        elif "Everything up-to-date" in result.get("stdout", ""):
            self.colors.info("ℹ️ Todo está actualizado.")
        else:
            self.colors.error(f"❌ Error al hacer push: {error_msg}")
            self.logger.log_error(error_msg, "upload_changes")

    def cancel_rebase(self) -> None:
        """Cancela un rebase en progreso"""
        self.ask_pass()

        abort_result = self.run_git_command("git rebase --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("✅ Rebase cancelado exitosamente.")
            self.logger.log_operation("REBASE_CANCEL", "Rebase cancelado", "SUCCESS")
        else:
            self.colors.warning("⚠️ No hay rebase en progreso para cancelar.")

    def pull_current_branch(self) -> None:
        """Hace pull de la rama actual"""
        self.ask_pass()

        try:
            # Obtener rama actual
            branch_result = self.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"].strip()

            self.colors.info(
                f"🌿 Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )

            # Verificar que no sea la rama base
            if current_branch == self.base_branch:
                self.colors.error(f"❌ Estás en la rama base '{current_branch}'.")
                self.colors.info("💡 Usa REBASE para integrar cambios a tu feature.")
                return

            # Verificar si existe en remoto
            remote_check = self.run_git_command(
                f"git ls-remote --heads origin {current_branch}", allow_failure=True
            )

            if not remote_check["stdout"].strip():
                self.colors.warning(f"⚠️ La rama {current_branch} no existe en remoto.")
                self.colors.info("📤 Creando rama en remoto...")
                self.run_git_command(f"git push --set-upstream origin {current_branch}")
                self.colors.success(f"✅ Rama {current_branch} publicada.")
                return

            # Verificar cambios locales
            status = self.run_git_command("git status --porcelain")
            has_changes = bool(status["stdout"].strip())

            if has_changes:
                self.colors.warning("⚠️ Hay cambios locales sin commitear.")
                if self.confirm_action("¿Guardar cambios antes del pull?"):
                    self.save_changes_locally()
                    self._do_pull(current_branch)
                    self.restore_local_changes()
                else:
                    self._do_pull(current_branch)
            else:
                self._do_pull(current_branch)

        except Exception as e:
            self.colors.error(f"❌ Error al hacer pull: {str(e)}")
            self.logger.log_error(str(e), "pull_current_branch")

    def _do_pull(self, branch: str) -> None:
        """Ejecuta el pull con rebase"""
        pull_result = self.run_git_command(
            f"git pull --rebase origin {branch}", allow_failure=True
        )

        if pull_result["returncode"] == 0:
            self.colors.success(
                f"✅ PULL EXITOSO: Cambios descargados en {Fore.YELLOW}{branch}{Fore.RESET}"
            )
            self.logger.log_pull_operation(branch, "SUCCESS")
        else:
            if "CONFLICT" in pull_result.get("stdout", "") + pull_result.get(
                "stderr", ""
            ):
                self.colors.error("❌ Hay conflictos durante el pull.")
                self.colors.info(
                    "💡 Resuelve los conflictos y ejecuta: git rebase --continue"
                )
            else:
                self.colors.error(
                    f"❌ Error durante el pull: {pull_result.get('stderr', '')}"
                )
            self.logger.log_pull_operation(branch, "ERROR")

    def view_today_logs(self) -> None:
        """Muestra los logs del día actual"""
        try:
            log_content = self.logger.read_today_log()
            log_path = self.logger.get_today_log_path()

            self.colors.info(f"📋 LOGS DE HOY: {log_path}")
            self.colors.info("=" * 80)

            if log_content == "No hay log para hoy.":
                self.colors.warning("📝 No hay logs registrados para hoy.")
            else:
                # Formatear y mostrar logs
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
            self.logger.log_operation("VIEW_LOGS", "Logs consultados", "INFO")

        except Exception as e:
            self.colors.error(f"❌ Error al leer logs: {str(e)}")
            self.logger.log_error(str(e), "view_today_logs")

    def reset_to_base_with_backup(self) -> None:
        """Hace reset completo a la rama base con backup opcional"""
        self.ask_pass()

        try:
            # Obtener rama actual
            current = self.run_git_command("git branch --show-current")
            current_branch = current["stdout"].strip()

            self.colors.info(f"\n🔄 RESET COMPLETO A RAMA BASE:")
            self.colors.info(f"📁 Repo: {Fore.MAGENTA}{self.repo_path}{Fore.RESET}")
            self.colors.info(
                f"🌿 Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )
            self.colors.info(
                f"📥 Resetear a: {Fore.BLUE}{self.base_branch}{Fore.RESET}"
            )

            # Verificar cambios
            status = self.run_git_command("git status --porcelain")
            has_changes = bool(status["stdout"].strip())

            if has_changes:
                self.colors.info("📋 Cambios detectados:")
                self.run_git_command("git status --short")

            # Confirmar operación
            if not self.confirm_action(
                f"⚠️ ADVERTENCIA: Esta operación borrará TODOS tus cambios actuales.\n"
                f"Tu rama será una copia EXACTA de '{self.base_branch}'.\n"
                f"¿Continuar?"
            ):
                self.colors.info("❌ Operación cancelada.")
                return

            # Crear backup si el usuario lo desea
            backup_branch = "N/A"
            if self.confirm_action("¿Crear backup de los cambios actuales?"):
                backup_branch = self._create_backup_branch(has_changes)

            # Resetear a la rama base
            self._reset_to_base()

            # Mostrar resultado
            self.colors.success("✅ OPERACIÓN COMPLETADA")
            self.colors.success(
                f"📄 Rama actual: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
            )
            if backup_branch != "N/A":
                self.colors.success(
                    f"💾 Backup en: {Fore.GREEN}{backup_branch}{Fore.RESET}"
                )
                self.colors.info(f"💡 Para recuperar: git checkout {backup_branch}")

            self.logger.log_operation(
                "RESET_TO_BASE",
                f"Reset a {self.base_branch}, backup: {backup_branch}",
                "SUCCESS",
            )

            # Mostrar estado final
            self.colors.info("\n📊 Estado final:")
            self.run_git_command("git status")

        except Exception as e:
            self.colors.error(f"❌ Error durante reset: {str(e)}")
            self.logger.log_error(str(e), "reset_to_base_with_backup")

    def _create_backup_branch(self, has_changes: bool) -> str:
        """Crea una rama de backup con los cambios actuales"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_branch = f"{self.feature_branch}_backup_{timestamp}"

        if has_changes:
            self.colors.info("💾 Guardando cambios no commiteados...")
            stash_msg = f"Backup antes de reset - {timestamp}"
            self.run_git_command(f'git stash push -m "{stash_msg}"')

        self.colors.info(f"🔄 Creando rama de backup: {backup_branch}")
        self.run_git_command(f"git checkout -b {backup_branch}")

        if has_changes:
            self.colors.info("📦 Aplicando cambios guardados...")
            self.run_git_command("git stash pop")
            self.run_git_command("git add .")
            commit_msg = f"Backup de cambios antes de reset - {timestamp}"
            self.run_git_command(f'git commit -m "{commit_msg}"')

        self.colors.warning(f"⚠️ El backup '{backup_branch}' es solo local.")
        return backup_branch

    def _reset_to_base(self) -> None:
        """Resetea la rama feature a la rama base"""
        # Verificar si la rama base existe localmente
        base_check = self.run_git_command(
            f"git rev-parse --verify {self.base_branch}", allow_failure=True
        )

        if base_check["returncode"] != 0:
            self.colors.warning(f"⚠️ Descargando rama base '{self.base_branch}'...")
            self.run_git_command(
                f"git fetch origin {self.base_branch}:{self.base_branch}"
            )

        # Cambiar a rama base y actualizar
        self.colors.info(f"🔄 Actualizando {self.base_branch}...")
        self.run_git_command(f"git checkout {self.base_branch}")
        self.run_git_command("git fetch origin")
        self.run_git_command(f"git reset --hard origin/{self.base_branch}")

        # Resetear rama feature
        self.colors.info(f"🌿 Reseteando {self.feature_branch}...")

        feature_exists = self.run_git_command(
            f"git rev-parse --verify {self.feature_branch}", allow_failure=True
        )

        if feature_exists["returncode"] == 0:
            self.run_git_command(f"git checkout {self.feature_branch}")
            self.run_git_command(f"git reset --hard {self.base_branch}")
        else:
            self.run_git_command(f"git checkout -b {self.feature_branch}")
