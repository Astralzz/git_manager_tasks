import os
import subprocess
import sys
from colorama import Fore

from classes.GlobalClass import GlobalClass
from classes.GitLogClass import GitLogClass


# Clase para manejar comandos git
class GitClass(GlobalClass):

    # Constructor de la clase
    def __init__(self, config: dict):
        self.config = config
        self.repo_path = config.get("repo_path")

        # Inicializa la clase GlobalClass
        super().__init__()

        # Inicializa el sistema de logs
        self.logger = GitLogClass(self.repo_path)

        # Registra el inicio del programa con la configuración seleccionada
        self.logger.log_program_start(self.config)

    # Funcion para ejecutar comandos git
    def run_git_command(self, command: str) -> dict:
        """
        Ejecuta un comando git y retorna la salida
        @param {str} command: El comando git que se va a ejecutar
        @param {str} cwd: La ruta del directorio de trabajo
        @return {str}: La salida del comando [stdout y stderr]
        """
        try:
            # Imprime el comando que se va a ejecutar
            self.colors.info(f"▶ Ejecutando: {command}")
            # Ejecuta el comando git y captura la salida
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
                cwd=self.repo_path,
            )
            # Imprime la salida del comando
            self.colors.success(result.stdout)

            # Registra el comando en el log
            result_dict = {
                "returncode": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            }
            self.logger.log_git_command(command, result_dict)

            # Retorna la salida del comando
            return result_dict
        except subprocess.CalledProcessError as e:
            # Imprime el error que se produjo
            self.colors.error(f"❌ Error al ejecutar '{command}':\n{e.stderr}")

            # Registra el error en el log
            error_result = {
                "returncode": e.returncode,
                "stdout": e.stdout.strip() if e.stdout else "",
                "stderr": e.stderr.strip() if e.stderr else "",
            }
            self.logger.log_git_command(command, error_result)
            self.logger.log_error(
                f"Error al ejecutar comando Git: {e.stderr}", "run_git_command"
            )

            sys.exit(1)

    # Funcion para mostrar el menu de opciones
    def display_git_menu(self) -> None:
        """
        Muestra el menú de opciones de forma persistente hasta que el usuario decida salir.
        """
        # Definir las opciones del menú
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
                "description": f"📥 PULL: Obtener cambios de mi equipo en mi rama actual (feature/{Fore.YELLOW}{self.config.get('feature_branch')})",
            },
            {
                "function": self._handle_rebase,
                "description": f"🔄 REBASE: Integrar cambios de {Fore.BLUE}{self.config.get('base_branch')} a mi rama feature {Fore.YELLOW}{self.config.get('feature_branch')}",
            },
            {
                "function": self.upload_changes,
                "description": "📤 Subir mis cambios al repositorio remoto",
            },
            {
                "function": self.create_branch_feature,
                "description": f"🌱 Crear la rama feature: {Fore.YELLOW}{self.config.get('feature_branch')} {(Fore.RED + 'SOLO SI NO EXISTE') if not self.config.get('feature_branch') else ''}",
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
        # Mostrar el menu de opciones
        self.show_menu(options)

    # Funcion para manejar el rebase
    def _handle_rebase(self) -> None:
        """
        Integra los cambios más recientes de la rama base (main/master) a tu rama feature
        """
        # Mostrar información del proceso
        base_branch = self.config.get("base_branch")
        feature_branch = self.config.get("feature_branch")

        self.colors.info(
            f"🔄 REBASE: Integrando cambios de {Fore.BLUE}{base_branch} → {Fore.YELLOW}{feature_branch}"
        )

        # Verificar si hay cambios locales antes de preguntar
        status = self.run_git_command("git status --porcelain")
        has_local_changes = bool(status["stdout"].strip())

        if has_local_changes:
            # Preguntamos si queremos guardar los cambios locales
            if self.confirm_action(
                "¿Quieres guardar tus cambios locales antes del rebase?"
            ):
                # Guardamos los cambios locales
                self.save_changes_locally()
                # Actualizamos desde la rama base
                self.get_latest_changes()
                # Restauramos los cambios locales
                self.restore_local_changes()
            else:
                # Actualizamos desde la rama base
                self.get_latest_changes()
        else:
            # No hay cambios locales, hacer rebase directamente
            self.colors.info(
                "✅ No hay cambios locales pendientes. Procediendo con el rebase..."
            )
            self.get_latest_changes()

    # Funcion para obtener el estado del repositorio
    def get_repo_status(self) -> None:
        """
        Obtiene el estado del repositorio
        """
        self.run_git_command("git status")

    # Funcion para obtener la rama actual
    def get_current_branch(self) -> None:
        """
        Obtiene la rama actual
        """
        self.run_git_command("git branch")

    # Funcion para restaurar los cambios locales [Despues de actualizar desde la rama base / git stash pop]
    def restore_local_changes(self) -> None:
        """
        Restaura los cambios locales
        """
        # Verifica si hay stash para aplicar
        result = self.run_git_command("git stash list")

        # Verifica si hay stash para aplicar
        if not result["stdout"].strip():
            self.colors.warning("⚠ No hay stash para aplicar.")
            return

        # Imprime el ultimo stash
        self.colors.info("📦 Último stash:")
        self.run_git_command("git stash show -p stash@{0}")

        # Preguntamos si se quiere aplicar el ultimo stash
        if not self.confirm_action("¿Deseas aplicar este stash?"):
            return

        # Aplica el ultimo stash
        self.run_git_command("git stash pop")
        self.colors.success("✅ Cambios locales restaurados.")
        self.logger.log_stash_operation("pop", "", "SUCCESS")

    # Funcion para guardar mis cambios localmente [Antes de actualizar desde la rama base / git stash]
    def save_changes_locally(self) -> None:
        """
        Guarda los cambios localmente
        """
        # Verifica si hay cambios locales para guardar
        status = self.run_git_command("git status --porcelain")
        if not status["stdout"].strip():
            self.colors.warning("⚠ No hay cambios locales para guardar.")
            return

        # Mostrar los cambios que se van a guardar
        self.colors.info("📋 Cambios que se guardarán:")
        self.run_git_command("git status --short")

        # Pide el mensaje del commit
        commit_message = input("📝 Escribe el mensaje del stash: ").strip()
        if not commit_message:
            self.colors.warning("⚠ No se escribió un mensaje de stash.")
            self.logger.log_warning(
                "No se escribió mensaje de stash", "save_changes_locally"
            )
            return

        # Registra la entrada del usuario
        self.logger.log_user_input("stash_message", commit_message)

        # Guarda los cambios localmente
        self.run_git_command(f'git stash push -m "{commit_message}"')
        # Imprime el mensaje de exito
        self.colors.success("📦 Cambios guardados localmente con `stash`.")

        # Registra el éxito en el log
        self.logger.log_stash_operation("save", commit_message, "SUCCESS")

    # Funcion para obtener los cambios mas recientes desde la rama base a la rama feature
    def get_latest_changes(self) -> None:
        """
        Obtiene los cambios más recientes desde la rama base a la rama feature
        """
        # Valida los campos requeridos
        self.validate_required_fields(["base_branch", "feature_branch"], self.repo_path)

        # Obtiene las ramas desde config
        base_branch = self.config.get("base_branch")
        feature_branch = self.config.get("feature_branch")

        # Imprime información del proceso
        self.colors.info(f"\n🔄 PROCESO DE REBASE:")
        self.colors.info(f"📁 Repo: {Fore.MAGENTA}{self.repo_path}")
        self.colors.info(f"🌿 Rama feature: {Fore.YELLOW}{feature_branch}")
        self.colors.info(f"📥 Integrando desde: {Fore.BLUE}{base_branch}\n")

        # Cambia a la rama feature
        self.run_git_command(f"git checkout {feature_branch}")

        # Fetch de ramas remotas
        self.run_git_command("git fetch origin")

        # Verifica si la rama base existe localmente
        result = subprocess.run(
            ["git", "rev-parse", "--verify", base_branch],
            cwd=self.repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Si la rama base no existe localmente, intenta descargarla desde remoto
        if result.returncode != 0:
            # Si la rama base no existe localmente, intenta descargarla desde remoto
            self.colors.warning(
                f"⚠️ La rama base '{base_branch}' no existe localmente. Intentando descargarla desde remoto..."
            )
            # Descarga la rama base desde remoto
            fetch_result = self.run_git_command(
                f"git fetch origin {base_branch}:{base_branch}",
            )
            # Si no se pudo obtener la rama remota, imprime un error
            if fetch_result["returncode"] != 0:
                self.colors.error(
                    f"❌ No se pudo obtener la rama remota '{base_branch}'. Verifica que exista en el repositorio remoto."
                )
                sys.exit(1)

        # Ejecuta el rebase
        rebase_result = self.run_git_command(
            f"git rebase {base_branch}",
        )

        # Si el rebase se realizo correctamente, imprime un mensaje de exito
        if rebase_result["returncode"] == 0:
            self.colors.success(
                f"✅ REBASE EXITOSO: Los cambios más recientes de {Fore.BLUE}{base_branch} han sido integrados a tu rama {Fore.YELLOW}{feature_branch}."
            )
            # Registra el éxito del rebase
            self.logger.log_rebase_operation(base_branch, feature_branch, "SUCCESS")
        # Si el rebase no se realizo correctamente, imprime un mensaje de error
        else:
            error_msg = f"Falló el rebase con la rama base '{base_branch}'. Revisa si la rama existe correctamente y no tiene conflictos."
            self.colors.error(f"❌ {error_msg}")
            # Registra el error del rebase
            self.logger.log_rebase_operation(base_branch, feature_branch, "ERROR")
            self.logger.log_error(error_msg, "get_latest_changes")
            sys.exit(1)

    # Funcion para crear una nueva rama
    def create_branch_feature(self) -> None:
        """
        Crea una nueva rama desde la rama actual.
        """

        # Pedir pass para acciones sensibles
        self.ask_pass()

        # Obtiene la rama feature desde config
        feature_branch = self.config.get("feature_branch")

        # Valida los campos requeridos
        self.validate_required_fields(["feature_branch"], self.repo_path)

        # Verifica si la rama ya existe localmente
        result_local = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", feature_branch],
            cwd=self.repo_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Si la rama ya existe localmente, imprime un mensaje de advertencia
        if result_local.returncode == 0:
            self.colors.warning(
                f"⚠️ La rama '{feature_branch}' ya existe localmente. No se creará nuevamente."
            )
            return

        # Verifica si la rama existe en el remoto
        result_remote = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", feature_branch],
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Si la rama ya existe en el remoto, imprime un mensaje de advertencia
        if result_remote.stdout.strip():
            self.colors.warning(
                f"⚠️ La rama '{feature_branch}' ya existe en el remoto. Puedes hacer fetch o checkout desde origin."
            )
            return

        # Intenta crear la rama con Git
        try:
            self.colors.info(f"🌿 Creando nueva rama: {feature_branch}")
            subprocess.run(
                ["git", "checkout", "-b", feature_branch],
                cwd=self.repo_path,
                check=True,
            )
            self.colors.success(f"✅ Rama '{feature_branch}' creada exitosamente.")
            self.logger.log_branch_operation(
                "create", feature_branch, "Rama creada exitosamente"
            )
        except subprocess.CalledProcessError as e:
            error_msg = f"Error al crear la rama: {e}"
            self.colors.error(f"❌ {error_msg}")
            self.logger.log_branch_operation("create", feature_branch, "Error al crear")
            self.logger.log_error(error_msg, "create_branch_feature")
            sys.exit(1)

    # Funcion para eliminar una rama
    def delete_branch(self) -> None:
        """
        Elimina una rama
        """

        # Pedir pass para acciones sensibles
        self.ask_pass()

        # Pedimos el nombre de la rama a eliminar
        branch_name = input("📝 Escribe el nombre de la rama a eliminar: ").strip()
        if not branch_name:
            self.colors.warning("⚠ No se escribió un nombre de rama.")
            return

        # Valida los campos requeridos
        self.validate_required_fields(["feature_branch"], self.repo_path)

        # Ejecuta el comando para eliminar la rama
        self.run_git_command(f"git branch -D {branch_name}")
        self.colors.success(f"✅ Rama '{branch_name}' eliminada exitosamente.")
        self.logger.log_branch_operation(
            "delete", branch_name, "Rama eliminada exitosamente"
        )

    # Subir cambios al repositorio remoto
    def upload_changes(self) -> None:
        """
        Sube los cambios actuales al repositorio remoto
        """

        # Pedir pass para acciones sensibles
        self.ask_pass()

        try:
            # Verificar si hay cambios para subir
            status = self.run_git_command("git status --porcelain")
            has_changes = bool(status["stdout"].strip())

            if not has_changes:
                self.colors.warning(
                    "⚠ No hay cambios para subir. El repositorio está limpio."
                )
                return

            # Mostrar los cambios que se van a subir
            self.colors.info("📋 Cambios detectados:")
            self.run_git_command("git status --short")

            commit_message = input("📝 Escribe el mensaje del commit: ").strip()
            if not commit_message:
                self.colors.warning("⚠ No se escribió un mensaje de commit.")
                self.logger.log_warning(
                    "No se escribió mensaje de commit", "upload_changes"
                )
                return

            # Registra la entrada del usuario
            self.logger.log_user_input("commit_message", commit_message)

            self.run_git_command("git add .")
            self.run_git_command(f'git commit -m "{commit_message}"')

            # Intentar hacer push
            push_result = self.run_git_command("git push")

            # Validar si falló por falta de upstream
            if "has no upstream branch" in push_result["stderr"]:
                # Obtener la rama actual
                branch_result = self.run_git_command("git branch --show-current")
                current_branch = branch_result["stdout"]
                self.colors.warning(
                    f"⚠ La rama '{current_branch}' no tiene un upstream remoto. Configurando..."
                )
                self.logger.log_warning(
                    f"Rama '{current_branch}' sin upstream, configurando...",
                    "upload_changes",
                )

                # Subir con --set-upstream
                self.run_git_command(f"git push --set-upstream origin {current_branch}")

            self.colors.success(
                "✅ Cambios subidos exitosamente al repositorio remoto."
            )

            # Registra el éxito del push
            branch_result = self.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"]
            self.logger.log_push_operation(current_branch, commit_message, "SUCCESS")

        except Exception as e:
            self.colors.error(f"❌ Ocurrió un error al subir los cambios: {str(e)}")

    # Cancelar rebase
    def cancel_rebase(self) -> None:
        """
        Cancela un rebase
        """
        # Pedir pass para acciones sensibles
        self.ask_pass()

        # Ejecuta el comando para cancelar el rebase
        self.run_git_command("git rebase --abort")
        self.colors.success("✅ Rebase cancelado exitosamente.")
        self.logger.log_operation(
            "REBASE_CANCEL", "Rebase cancelado exitosamente", "SUCCESS"
        )

    # Funcion para hacer pull de la rama actual
    def pull_current_branch(self) -> None:
        """
        Hace un pull de la rama feature actual para obtener cambios del equipo
        """
        # Pedir pass para acciones sensibles
        self.ask_pass()

        try:
            # Obtener la rama actual
            branch_result = self.run_git_command("git branch --show-current")
            current_branch = branch_result["stdout"].strip()

            # Mostrar información de la rama actual
            self.colors.info(f"🌿 Rama actual: {Fore.YELLOW}{current_branch}")

            # Verificar que estemos en una rama feature (no en la base)
            if current_branch == self.config.get("base_branch"):
                self.colors.error(
                    f"❌ Estás en la rama base '{current_branch}'. Para obtener cambios del equipo, debes estar en tu rama feature."
                )
                self.colors.info(
                    f"💡 Usa la opción REBASE para integrar cambios de {current_branch} a tu feature."
                )
                return

            # Verificar si hay cambios locales
            status = self.run_git_command("git status --porcelain")
            has_local_changes = bool(status["stdout"].strip())

            if has_local_changes:
                self.colors.warning("⚠️ Hay cambios locales sin commitear.")

                # Preguntar si quiere guardar los cambios locales
                if self.confirm_action(
                    "¿Quieres guardar los cambios locales antes del pull?"
                ):
                    # Guardar cambios locales
                    self.save_changes_locally()

                    # Hacer pull de la rama actual
                    self.run_git_command(f"git pull origin {current_branch}")

                    # Restaurar cambios locales
                    self.restore_local_changes()

                    self.colors.success(
                        f"✅ PULL EXITOSO: Cambios del equipo descargados en {Fore.YELLOW}{current_branch} con tus cambios locales preservados."
                    )
                    self.logger.log_pull_operation(current_branch, "SUCCESS")
                else:
                    # Hacer pull sin guardar cambios (puede causar conflictos)
                    self.colors.warning(
                        "⚠️ Haciendo pull sin guardar cambios locales. Pueden surgir conflictos."
                    )
                    self.run_git_command(f"git pull origin {current_branch}")
                    self.colors.success(
                        f"✅ PULL EXITOSO: Cambios del equipo descargados en {Fore.YELLOW}{current_branch}."
                    )
                    self.logger.log_pull_operation(current_branch, "SUCCESS")
            else:
                # No hay cambios locales, hacer pull directamente
                self.run_git_command(f"git pull origin {current_branch}")
                self.colors.success(
                    f"✅ PULL EXITOSO: Cambios del equipo descargados en {Fore.YELLOW}{current_branch}."
                )
                self.logger.log_pull_operation(current_branch, "SUCCESS")

        except Exception as e:
            self.colors.error(f"❌ Ocurrió un error al hacer pull: {str(e)}")
            self.logger.log_error(f"Error en pull: {str(e)}", "pull_current_branch")

    # Funcion para ver los logs de hoy
    def view_today_logs(self) -> None:
        """
        Muestra los logs del día actual
        """
        try:
            log_content = self.logger.read_today_log()
            log_path = self.logger.get_today_log_path()

            self.colors.info(f"📋 LOGS DE HOY: {log_path}")
            self.colors.info("=" * 80)

            if log_content == "No hay log para hoy.":
                self.colors.warning("📝 No hay logs registrados para hoy.")
            else:
                # Mostrar el contenido del log con formato
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

            # Registra que se consultaron los logs
            self.logger.log_operation("VIEW_LOGS", "Logs del día consultados", "INFO")

        except Exception as e:
            self.colors.error(f"❌ Error al leer los logs: {str(e)}")
            self.logger.log_error(f"Error al leer logs: {str(e)}", "view_today_logs")
