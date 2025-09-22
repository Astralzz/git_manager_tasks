import subprocess
import sys
import datetime
from colorama import Fore
from typing import Optional, List

from classes.GlobalClass import GlobalClass
from classes.GitLogClass import GitLogClass
from byTypes.configTypes import ExtendedConfigType, GitCommandResult, MenuOptionType
from consts.env import GIT_CONFIG_ID


class GitClass(GlobalClass):
    """Clase para manejar operaciones Git de forma interactiva y segura"""

    def __init__(self, config: "ExtendedConfigType"):
        """
        Inicializa la clase GitClass con la configuración proporcionada

        Args:
            config: Configuración del repositorio con tipado ExtendedConfigType
        """

        # Inicializa la clase padre primero
        super().__init__(selected_config=config)

        # Configuración específica de Git
        self.git_config: ExtendedConfigType = config
        self.repo_path: Optional[str] = config.get("repo_path")

        # Inicializa el sistema de logs específico de Git
        if self.repo_path:
            self.git_logger: GitLogClass = GitLogClass(self.repo_path)
        else:
            raise ValueError("repo_path es requerido para GitClass")

        # Valida los campos requeridos
        self.validate_required_fields(["base_branch", "feature_branch"], self.repo_path)

        # Obtiene las ramas del repositorio
        self.base_branch: Optional[str] = config.get("base_branch")
        self.feature_branch: Optional[str] = config.get("feature_branch")

        # Validaciones de seguridad
        self._validate_branch_configuration()

        # Intentar cambiar automáticamente a la rama feature
        self._auto_checkout_to_feature_branch()

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

    def _validate_branch_configuration(self) -> None:
        """Valida que la configuración de ramas sea correcta"""
        # Verificar que las ramas existan
        if not self.feature_branch:
            self.colors.error("La rama feature no está configurada.")
            sys.exit(1)

        if not self.base_branch:
            self.colors.error("La rama base no está configurada.")
            sys.exit(1)

        # La rama feature nunca debe ser main o master
        if self.feature_branch.lower() in ["main", "master"]:
            self.colors.error(f"La rama feature no puede ser '{self.feature_branch}'.")
            if hasattr(self, "logger"):
                self.git_logger.log_error(
                    f"Configuración inválida: feature_branch = {self.feature_branch}",
                    "_validate_branch_configuration",
                )
            sys.exit(1)

        # Las ramas no pueden ser iguales
        if self.base_branch == self.feature_branch:
            self.colors.error("La rama base y la rama feature no pueden ser iguales.")
            if hasattr(self, "logger"):
                self.git_logger.log_error(
                    "Configuración inválida: base_branch == feature_branch",
                    "_validate_branch_configuration",
                )
            sys.exit(1)
        """Valida que la configuración de ramas sea correcta"""
        # Verificar que las ramas existan
        if not self.feature_branch:
            self.colors.error("La rama feature no está configurada.")
            sys.exit(1)

        if not self.base_branch:
            self.colors.error("La rama base no está configurada.")
            sys.exit(1)

        # La rama feature nunca debe ser main o master
        if self.feature_branch.lower() in ["main", "master"]:
            self.colors.error(f"La rama feature no puede ser '{self.feature_branch}'.")
            if hasattr(self, "logger"):
                self.git_logger.log_error(
                    f"Configuración inválida: feature_branch = {self.feature_branch}",
                    "_validate_branch_configuration",
                )
            sys.exit(1)

        # Las ramas no pueden ser iguales
        if self.base_branch == self.feature_branch:
            self.colors.error("La rama base y la rama feature no pueden ser iguales.")
            if hasattr(self, "logger"):
                self.git_logger.log_error(
                    "Configuración inválida: base_branch == feature_branch",
                    "_validate_branch_configuration",
                )
            sys.exit(1)

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
                    self.colors.success(f"\n{result.stdout.strip()}\n")
            else:
                # Solo muestra error si no se permite fallo
                if not allow_failure:
                    if result.stderr.strip():
                        self.colors.error(f"Error: {result.stderr.strip()}")

            # Prepara el resultado
            result_dict: "GitCommandResult" = {
                "returncode": result.returncode,
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
            }

            # Registra el comando en el log
            self.git_logger.log_git_command(command, result_dict)

            # Si hubo error y no se permite fallo, termina el programa
            if result.returncode != 0 and not allow_failure:
                self.git_logger.log_error(
                    f"Error al ejecutar comando: {result.stderr}", "run_git_command"
                )
                sys.exit(1)

            return result_dict

        except Exception as e:
            # Maneja excepciones inesperadas
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

            # Limpiar el nombre de la rama objetivo
            target_branch = self.feature_branch.strip() if self.feature_branch else ""

            # Si ya estamos en la rama feature, no hacer nada
            if current_branch == target_branch:
                self.colors.success(
                    f"Ya estás en la rama feature: {Fore.YELLOW}{target_branch}{Fore.RESET}"
                )
                return

            # Verificar si la rama feature existe localmente con git branch
            check_local = self.run_git_command(
                f"git show-ref --verify --quiet refs/heads/{target_branch}",
                allow_failure=True,
            )

            if check_local["returncode"] == 0:
                # La rama existe localmente, hacer checkout
                self.colors.info(
                    f"🔄 Cambiando a la rama feature: {Fore.YELLOW}{target_branch}{Fore.RESET}"
                )
                checkout_result = self.run_git_command(
                    f"git checkout {target_branch}", allow_failure=True
                )

                if checkout_result["returncode"] == 0:
                    self.colors.success(
                        f"Posicionado en la rama: {Fore.YELLOW}{target_branch}{Fore.RESET}"
                    )
                    self.git_logger.log_operation(
                        "AUTO_CHECKOUT",
                        f"Cambio automático a {target_branch}",
                        "SUCCESS",
                    )
                else:
                    # Verificar si hay cambios no commiteados que impiden el checkout
                    status_check = self.run_git_command("git status --porcelain", allow_failure=True)
                    if status_check["stdout"].strip():
                        self._handle_checkout_with_changes(current_branch, target_branch, checkout_result)
                    else:
                        # Otro tipo de error
                        self.colors.warning(
                            f"⚠️ No se pudo cambiar a la rama {target_branch}"
                        )
                        self.colors.error(f"Error específico: {checkout_result.get('stderr', 'Sin error específico')}")
                        self.colors.info(
                            f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}"
                        )
                        
                        # Log del error
                        self.git_logger.log_operation(
                            "AUTO_CHECKOUT",
                            f"Error al cambiar a {target_branch}: {checkout_result.get('stderr', '')}",
                            "ERROR",
                        )
            else:
                # Verificar en remoto
                self._check_remote_branch(current_branch)

        except Exception as e:
            self.colors.warning(f"⚠️ Error al verificar rama: {str(e)}")
            self.colors.info("💡 El programa continuará normalmente.")

    def _handle_checkout_with_changes(self, current_branch: str, target_branch: str, checkout_result: "GitCommandResult") -> None:
        """Maneja el checkout cuando hay cambios locales pendientes"""
        self.colors.warning("⚠️ Tienes cambios sin commitear que impiden el checkout:")
        self.run_git_command("git status --short")
        
        self.colors.info("\n💡 Opciones disponibles:")
        self.colors.info("  1. 📦 Guardar cambios temporalmente (stash) y cambiar de rama")
        self.colors.info("  2. 📍 Permanecer en la rama actual y continuar")
        self.colors.info("  3. 📝 Ver detalles de los cambios antes de decidir")
        
        while True:
            try:
                choice = input("\n🔍 Selecciona una opción (1-3): ").strip()
                
                if choice == "1":
                    # Guardar cambios y cambiar de rama
                    if self._stash_and_checkout(current_branch, target_branch):
                        return
                    else:
                        break
                        
                elif choice == "2":
                    # Permanecer en rama actual
                    self.colors.info(f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")
                    self.git_logger.log_operation(
                        "AUTO_CHECKOUT",
                        f"Usuario decidió permanecer en {current_branch}",
                        "INFO",
                    )
                    return
                    
                elif choice == "3":
                    # Mostrar detalles de cambios
                    self.colors.info("📋 Detalles de los cambios:")
                    self.run_git_command("git diff --name-status")
                    self.colors.info("\n📝 Vista previa de cambios:")
                    self.run_git_command("git diff --stat")
                    continue
                    
                else:
                    self.colors.warning("⚠️ Opción inválida. Selecciona 1, 2 o 3.")
                    continue
                    
            except KeyboardInterrupt:
                self.colors.info(f"\n📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")
                return
        
        # Si llegamos aquí, algo falló
        self.colors.info(f"📍 Permaneciendo en: {Fore.CYAN}{current_branch}{Fore.RESET}")

    def _stash_and_checkout(self, current_branch: str, target_branch: str) -> bool:
        """Guarda cambios con stash y hace checkout usando las funciones existentes"""
        try:
            # Usar la función existente save_changes_locally
            self.colors.info("📦 Guardando cambios temporalmente...")
            
            # Llamar a la función existente que ya maneja todo el stash
            self.save_changes_locally()
            
            # Intentar checkout nuevamente
            self.colors.info(f"🔄 Cambiando a {Fore.YELLOW}{target_branch}{Fore.RESET}...")
            checkout_result = self.run_git_command(
                f"git checkout {target_branch}", 
                allow_failure=True
            )
            
            if checkout_result["returncode"] == 0:
                self.colors.success(f"✅ Posicionado en: {Fore.YELLOW}{target_branch}{Fore.RESET}")
                self.colors.info(f"📦 Tus cambios están guardados en stash. Usa la opción del menú para restaurarlos.")
                
                self.git_logger.log_operation(
                    "AUTO_CHECKOUT_WITH_STASH",
                    f"Checkout exitoso a {target_branch} con stash",
                    "SUCCESS",
                )
                return True
            else:
                self.colors.error("❌ Error al cambiar de rama incluso después del stash")
                self.colors.info("🔄 Restaurando cambios...")
                
                # Usar la función existente para restaurar
                self.restore_local_changes()
                return False
                
        except Exception as e:
            self.colors.error(f"❌ Error inesperado durante stash y checkout: {str(e)}")
            return False

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
                    f"Rama descargada y posicionado en: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
                )
                self.git_logger.log_operation(
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
                        f"Rama rastreada: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
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
        self.git_logger.log_operation(
            "NEW_TASK_DETECTED",
            f"Nueva tarea detectada: {self.feature_branch} no existe",
            "INFO",
        )

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

    def _handle_rebase(self) -> None:
        """Integra los cambios de la rama base a la rama feature"""
        self.colors.info(
            f"🔄 REBASE: Integrando cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} → {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
        )
        
        # Verificar cambios locales
        status = self.run_git_command("git status --porcelain", allow_failure=True)
        has_local_changes = bool(status["stdout"].strip())
        
        stashed = False
        if has_local_changes:
            if self.confirm_action("¿Quieres guardar tus cambios locales antes del rebase?"):
                self.save_changes_locally()
                stashed = True
        
        try:
            # IMPORTANTE: Actualizar main desde el remoto
            self.colors.info(f"📥 Actualizando {self.base_branch} desde remoto...")
            self.run_git_command(f"git fetch origin {self.base_branch}:{self.base_branch}")
            
            # Ahora sí hacer el rebase con main actualizado
            self.colors.info(f"🔄 Aplicando rebase...")
            self.run_git_command(f"git rebase {self.base_branch}")
            
            self.colors.success("✅ REBASE EXITOSO: Cambios integrados")
            
        except Exception as e:
            self.colors.error(f"Error en rebase: {str(e)}")
            # Manejar conflictos o errores
            
        finally:
            if stashed:
                self.restore_local_changes()

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
            self.colors.success("Cambios locales restaurados.")
            self.git_logger.log_stash_operation("pop", "", "SUCCESS")
        else:
            self.colors.error("Error al aplicar stash. Puede haber conflictos.")
            self.git_logger.log_stash_operation("pop", "", "ERROR")

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

        self.git_logger.log_user_input("stash_message", stash_message)

        # Guardar cambios
        self.run_git_command(f'git stash push -m "{stash_message}"')
        self.colors.success("📦 Cambios guardados localmente con stash.")
        self.git_logger.log_stash_operation("save", stash_message, "SUCCESS")

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
            self.colors.error(f"No se pudo cambiar a la rama {self.feature_branch}")
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
                self.colors.error(f"No se pudo obtener la rama '{self.base_branch}'")
                return

        # Ejecutar rebase
        rebase_result = self.run_git_command(
            f"git rebase {self.base_branch}", allow_failure=True
        )

        if rebase_result["returncode"] == 0:
            self.colors.success(
                f"REBASE EXITOSO: Cambios de {Fore.BLUE}{self.base_branch}{Fore.RESET} integrados"
            )
            self.git_logger.log_rebase_operation(
                self._get_base_branch(), self._get_feature_branch(), "SUCCESS"
            )
        else:
            if "CONFLICT" in rebase_result.get("stdout", "") + rebase_result.get(
                "stderr", ""
            ):
                self.colors.error("Hay conflictos durante el rebase.")
                self.colors.info("💡 Resuelve los conflictos y ejecuta:")
                self.colors.info("   git add <archivos resueltos>")
                self.colors.info("   git rebase --continue")
                self.colors.info("   O usa la opción 9 para cancelar el rebase")
            else:
                self.colors.error(
                    f"Error durante el rebase: {rebase_result.get('stderr', '')}"
                )

            self.git_logger.log_rebase_operation(
                self._get_base_branch(), self._get_feature_branch(), "ERROR"
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
            self.colors.success(f"Rama '{self.feature_branch}' creada exitosamente.")
            self.git_logger.log_branch_operation(
                "create", self._get_feature_branch(), "SUCCESS"
            )
        else:
            self.colors.error(
                f"Error al crear la rama: {create_result.get('stderr', '')}"
            )
            self.git_logger.log_branch_operation(
                "create", self._get_feature_branch(), "ERROR"
            )

    def delete_branch(self) -> None:
        """Elimina una rama específica con menú interactivo"""
        self.ask_pass()

        # Obtener todas las ramas locales
        branches_result = self.run_git_command("git branch", allow_failure=True)
        if branches_result["returncode"] != 0:
            self.colors.error("Error al obtener las ramas locales.")
            return

        # Procesar ramas
        all_branches: List[str] = []
        current_branch: str = ""

        for line in branches_result["stdout"].split("\n"):
            line = line.strip()
            if line:
                if line.startswith("* "):
                    current_branch = line[2:].strip()
                    all_branches.append(current_branch)
                else:
                    all_branches.append(line.strip())

        # Filtrar ramas que se pueden eliminar (excluir actual y protegidas)
        deletable_branches: List[str] = []
        protected_branches = ["main", "master", "develop", "development"]

        for branch in all_branches:
            if branch != current_branch and branch.lower() not in protected_branches:
                deletable_branches.append(branch)

        # Verificar si hay ramas para eliminar
        if not deletable_branches:
            self.colors.warning("⚠️ No hay ramas disponibles para eliminar.")
            self.colors.info(f"📍 Rama actual: {Fore.CYAN}{current_branch}{Fore.RESET}")
            return

        # Mostrar menú de ramas
        self.colors.info("🗑️ SELECCIONAR RAMA PARA ELIMINAR")
        self.colors.info("━" * 50)
        self.colors.info(f"📍 Rama actual: {Fore.CYAN}{current_branch}{Fore.RESET}")
        self.colors.info("━" * 50)

        # Mostrar opciones numeradas
        for i, branch in enumerate(deletable_branches, 1):
            self.colors.info(f"  {i}. {Fore.YELLOW}{branch}{Fore.RESET}")

        self.colors.info(
            f"  {len(deletable_branches) + 1}. 📝 Escribir otra rama manualmente"
        )
        self.colors.info(f"  {len(deletable_branches) + 2}. Salir")
        self.colors.info("━" * 50)

        # Solicitar selección
        try:
            choice = input("📋 Selecciona una opción (número): ").strip()
            if not choice:
                self.colors.warning("⚠️ No se seleccionó ninguna opción.")
                return

            choice_num = int(choice)

            # Opción: Salir
            if choice_num == len(deletable_branches) + 2:
                self.colors.info("Operación cancelada.")
                return

            # Opción: Escribir manualmente
            elif choice_num == len(deletable_branches) + 1:
                branch_name = input("📝 Nombre de la rama a eliminar: ").strip()
                if not branch_name:
                    self.colors.warning("⚠ No se especificó ninguna rama.")
                    return

            # Opción: Rama de la lista
            elif 1 <= choice_num <= len(deletable_branches):
                branch_name = deletable_branches[choice_num - 1]

            else:
                self.colors.error("Opción inválida.")
                return

        except ValueError:
            self.colors.error("Debes introducir un número válido.")
            return

        # Registrar selección del usuario
        self.git_logger.log_user_input("branch_to_delete", branch_name)

        # Verificaciones adicionales para ramas escritas manualmente
        if branch_name == current_branch:
            self.colors.error("No puedes eliminar la rama en la que estás.")
            return

        # Verificar que no sea una rama protegida (para ramas escritas manualmente)
        if branch_name.lower() in protected_branches:
            if not self.confirm_action(
                f"⚠️ '{branch_name}' es una rama protegida. ¿Seguro que deseas eliminarla?"
            ):
                return

        # Confirmar eliminación
        self.colors.warning(
            f"⚠️ Vas a eliminar la rama: {Fore.YELLOW}{branch_name}{Fore.RESET}"
        )
        if not self.confirm_action("¿Continuar con la eliminación?"):
            self.colors.info("Eliminación cancelada.")
            return

        # Eliminar la rama (solo localmente)
        delete_result = self.run_git_command(
            f"git branch -D {branch_name}", allow_failure=True
        )

        if delete_result["returncode"] == 0:
            self.colors.success(f"Rama '{branch_name}' eliminada localmente.")
            self.colors.info(
                "ℹ️ Solo se eliminó la rama local, el remoto no fue afectado."
            )
            self.git_logger.log_branch_operation("delete", branch_name, "SUCCESS")
        else:
            self.colors.error(
                f"Error al eliminar la rama: {delete_result.get('stderr', '')}"
            )
            self.git_logger.log_branch_operation("delete", branch_name, "ERROR")

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
            self.colors.error(f"Error al subir cambios: {str(e)}")
            self.git_logger.log_error(str(e), "upload_changes")

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
            self.git_logger.log_warning(
                "No se escribió mensaje de commit", "upload_changes"
            )
            return False

        self.git_logger.log_user_input("commit_message", commit_message)

        self.run_git_command("git add .")
        self.run_git_command(f'git commit -m "{commit_message}"')
        self.colors.success("Commit realizado exitosamente.")
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
                        self.colors.error("Hay conflictos. Resuélvelos manualmente.")
                        self.git_logger.log_error(
                            "Conflictos durante pull", "upload_changes"
                        )
                        return False

        return True

    def _handle_push_success(self, branch: str) -> None:
        """Maneja el éxito del push"""
        self.colors.success("Cambios subidos exitosamente.")

        # Obtener último commit
        last_commit = self.run_git_command("git log -1 --oneline", allow_failure=True)
        commit_msg = (
            last_commit["stdout"].strip() if last_commit["stdout"] else "Unknown"
        )

        self.git_logger.log_push_operation(branch, commit_msg, "SUCCESS")

        self.colors.info(f"📊 Rama: {branch}")
        self.colors.info(f"📝 Último commit: {commit_msg}")

    def _handle_push_error(self, branch: str, result: GitCommandResult) -> None:
        """Maneja errores de push"""
        error_msg = result.get("stderr", "")

        if "rejected" in error_msg:
            self.colors.error("Push rechazado. Necesitas hacer pull primero.")
            self.colors.info(f"💡 Intenta: git pull --rebase origin {branch}")
            self.git_logger.log_push_operation(branch, "Push rejected", "WARNING")
        elif "Everything up-to-date" in result.get("stdout", ""):
            self.colors.info("ℹ️ Todo está actualizado.")
        else:
            self.colors.error(f"Error al hacer push: {error_msg}")
            self.git_logger.log_error(error_msg, "upload_changes")

    def cancel_rebase(self) -> None:
        """Cancela un rebase en progreso"""
        self.ask_pass()

        abort_result = self.run_git_command("git rebase --abort", allow_failure=True)

        if abort_result["returncode"] == 0:
            self.colors.success("Rebase cancelado exitosamente.")
            self.git_logger.log_operation(
                "REBASE_CANCEL", "Rebase cancelado", "SUCCESS"
            )
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
                self.colors.error(f"Estás en la rama base '{current_branch}'.")
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
                self.colors.success(f"Rama {current_branch} publicada.")
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
            self.colors.error(f"Error al hacer pull: {str(e)}")
            self.git_logger.log_error(str(e), "pull_current_branch")

    def _do_pull(self, branch: str) -> None:
        """Ejecuta el pull con rebase"""
        pull_result = self.run_git_command(
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
                    "💡 Resuelve los conflictos y ejecuta: git rebase --continue"
                )
            else:
                self.colors.error(
                    f"Error durante el pull: {pull_result.get('stderr', '')}"
                )
            self.git_logger.log_pull_operation(branch, "ERROR")

    def update_base_branch(self) -> None:
        """Actualiza la rama base con los últimos cambios del remoto"""
        self.ask_pass()

        try:
            # Obtener rama actual para regresar después
            current_result = self.run_git_command("git branch --show-current")
            current_branch = current_result["stdout"].strip()

            self.colors.info(f"\n🔄 ACTUALIZANDO RAMA BASE:")
            self.colors.info(f"📁 Repo: {Fore.MAGENTA}{self.repo_path}{Fore.RESET}")
            self.colors.info(
                f"🌿 Rama actual: {Fore.YELLOW}{current_branch}{Fore.RESET}"
            )
            self.colors.info(
                f"📥 Actualizando: {Fore.BLUE}{self.base_branch}{Fore.RESET}"
            )

            # Verificar si hay cambios locales en la rama actual
            status = self.run_git_command("git status --porcelain", allow_failure=True)
            has_local_changes = bool(status["stdout"].strip())

            if has_local_changes:
                self.colors.warning("⚠️ Hay cambios locales sin commitear.")
                if self.confirm_action("¿Guardar cambios antes de actualizar la base?"):
                    self.save_changes_locally()

            # Verificar si la rama base existe localmente
            base_check = self.run_git_command(
                f"git rev-parse --verify {self.base_branch}", allow_failure=True
            )

            if base_check["returncode"] != 0:
                self.colors.warning(
                    f"⚠️ Descargando rama base '{self.base_branch}' desde remoto..."
                )
                self.run_git_command(
                    f"git fetch origin {self.base_branch}:{self.base_branch}"
                )

            # Cambiar a la rama base
            self.colors.info(f"🔄 Cambiando a {self.base_branch}...")
            checkout_result = self.run_git_command(
                f"git checkout {self.base_branch}", allow_failure=True
            )

            if checkout_result["returncode"] != 0:
                self.colors.error(f"Error al cambiar a la rama {self.base_branch}")
                return

            # Actualizar referencias remotas
            self.colors.info("📡 Actualizando referencias remotas...")
            self.run_git_command("git fetch origin")

            # Hacer pull/reset de la rama base
            self.colors.info(f"📥 Descargando últimos cambios de {self.base_branch}...")

            # Verificar si hay commits locales en la rama base
            ahead_result = self.run_git_command(
                f"git rev-list --count origin/{self.base_branch}..HEAD",
                allow_failure=True,
            )

            has_local_commits = False
            if ahead_result["returncode"] == 0:
                ahead_count = int(ahead_result["stdout"].strip() or 0)
                has_local_commits = ahead_count > 0

            if has_local_commits:
                self.colors.warning(
                    f"⚠️ La rama {self.base_branch} tiene commits locales."
                )
                if self.confirm_action(
                    f"¿Hacer reset hard a origin/{self.base_branch}? (Se perderán los commits locales)"
                ):
                    self.run_git_command(f"git reset --hard origin/{self.base_branch}")
                    self.colors.success(
                        f"Rama {self.base_branch} reseteada a la versión remota."
                    )
                else:
                    # Intentar merge
                    merge_result = self.run_git_command(
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
                # No hay commits locales, hacer reset hard es seguro
                self.run_git_command(f"git reset --hard origin/{self.base_branch}")
                self.colors.success(
                    f"Rama {self.base_branch} actualizada exitosamente."
                )

            # Mostrar información de la actualización
            last_commit = self.run_git_command(
                "git log -1 --oneline", allow_failure=True
            )
            if last_commit["stdout"]:
                self.colors.info(f"📝 Último commit: {last_commit['stdout'].strip()}")

            # Regresar a la rama original
            if current_branch != self.base_branch:
                self.colors.info(f"🔄 Regresando a {current_branch}...")
                return_result = self.run_git_command(
                    f"git checkout {current_branch}", allow_failure=True
                )

                if return_result["returncode"] == 0:
                    self.colors.success(
                        f"De vuelta en: {Fore.YELLOW}{current_branch}{Fore.RESET}"
                    )

                    # Restaurar cambios si se guardaron
                    if has_local_changes:
                        if self.confirm_action("¿Restaurar los cambios guardados?"):
                            self.restore_local_changes()
                else:
                    self.colors.error(f"Error al regresar a {current_branch}")

            self.git_logger.log_operation(
                "UPDATE_BASE_BRANCH",
                f"Rama base {self.base_branch} actualizada",
                "SUCCESS",
            )

            # Sugerir rebase si estamos en una rama feature
            if current_branch == self.feature_branch:
                self.colors.info(
                    "💡 Recomendación: Considera hacer REBASE para integrar los nuevos cambios."
                )

        except Exception as e:
            self.colors.error(f"Error al actualizar rama base: {str(e)}")
            self.git_logger.log_error(str(e), "update_base_branch")

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
            self.git_logger.log_operation("VIEW_LOGS", "Logs consultados", "INFO")

        except Exception as e:
            self.colors.error(f"Error al leer logs: {str(e)}")
            self.git_logger.log_error(str(e), "view_today_logs")

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
                self.colors.info("Operación cancelada.")
                return

            # Crear backup si el usuario lo desea
            backup_branch = "N/A"
            if self.confirm_action("¿Crear backup de los cambios actuales?"):
                backup_branch = self._create_backup_branch(has_changes)

            # Resetear a la rama base
            self._reset_to_base()

            # Mostrar resultado
            self.colors.success("OPERACIÓN COMPLETADA")
            self.colors.success(
                f"📄 Rama actual: {Fore.YELLOW}{self.feature_branch}{Fore.RESET}"
            )
            if backup_branch != "N/A":
                self.colors.success(
                    f"💾 Backup en: {Fore.GREEN}{backup_branch}{Fore.RESET}"
                )
                self.colors.info(f"💡 Para recuperar: git checkout {backup_branch}")

            self.git_logger.log_operation(
                "RESET_TO_BASE",
                f"Reset a {self.base_branch}, backup: {backup_branch}",
                "SUCCESS",
            )

            # Mostrar estado final
            self.colors.info("\n📊 Estado final:")
            self.run_git_command("git status")

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

    # ---------- Flujos Complejos para tareas especificas ----------

    def feature_branch_workflow(self):
        """Flujo completo de feature branch según GitFlow CONACYT - Arquitectura GitFlow"""
        self.ask_pass()

        self.colors.info("\n=== FLUJO DE FEATURE BRANCH - CONACYT ===")

        # Verificar contexto específico
        if (
            self.feature_branch != "develop"
            or self.base_branch != "main"
            or not self.git_config
            or self.git_config.get("id") != GIT_CONFIG_ID
        ):
            self.colors.error(
                f"Este flujo solo es muy especifico y solo válido para: "
                f"'develop' con base 'main' y "
                f"configuración de ID única ?????."
            )
            return

        # Confirmar que el usuario entiende el contexto
        if not self.confirm_action(
            "Esto solo es para una tarea especifica, estas seguro?"
        ):
            self.colors.info("Operación cancelada.")
            return

        # Solicitar información al usuario
        version = input("Ingresa la versión (ej: [N].[N].[N]): ").strip()
        if not version:
            self.colors.error("La versión es requerida")
            return

        message = input("Ingresa el mensaje del commit: ").strip()
        if not message:
            self.colors.error("El mensaje del commit es requerido")
            return

        feature_name = f"feature/version-{version.replace('.', '-')}"

        # Registrar inputs
        self.git_logger.log_user_input("version", version)
        self.git_logger.log_user_input("commit_message", message)
        self.git_logger.log_user_input("feature_name", feature_name)

        self.colors.info(
            f"\n🚀 Iniciando flujo: {Fore.YELLOW}{feature_name}{Fore.RESET}"
        )

        try:
            # PASO 1: Asegurarse de estar en develop y actualizada
            self.colors.info("\n📍 PASO 1: Actualizando rama develop...")

            # Cambiar a develop
            checkout_result = self.run_git_command(
                "git checkout develop", allow_failure=True
            )
            if checkout_result["returncode"] != 0:
                self.colors.error("Error al cambiar a develop")
                return

            # Pull de develop
            pull_result = self.run_git_command(
                "git pull origin develop", allow_failure=True
            )
            if pull_result[
                "returncode"
            ] != 0 and "Already up to date" not in pull_result.get("stdout", ""):
                self.colors.error("Error al actualizar develop")
                return

            # PASO 2: Crear nueva rama feature
            self.colors.info(
                f"\n🌿 PASO 2: Creando rama {Fore.YELLOW}{feature_name}{Fore.RESET}..."
            )

            # Verificar si ya existe
            exists = self.run_git_command(
                f"git rev-parse --verify {feature_name}", allow_failure=True
            )
            if exists["returncode"] == 0:
                self.colors.warning(f"⚠️ La rama {feature_name} ya existe")
                # Cambiar a ella
                self.run_git_command(f"git checkout {feature_name}")
            else:
                # Crear y cambiar a la nueva rama
                create_result = self.run_git_command(
                    f"git checkout -b {feature_name}", allow_failure=True
                )
                if create_result["returncode"] != 0:
                    self.colors.error(f"Error al crear la rama {feature_name}")
                    return

            # PASO 3: Realizar cambios y hacer commit
            self.colors.info("\n💾 PASO 3: Realizando cambios y commit...")

            # Verificar si hay cambios
            status = self.run_git_command("git status --porcelain", allow_failure=True)
            if not status["stdout"].strip():
                self.colors.warning("⚠️ No hay cambios para commitear")
                if not self.confirm_action("¿Continuar sin cambios?"):
                    return
            else:
                # Mostrar cambios
                self.colors.info("📋 Cambios detectados:")
                self.run_git_command("git status --short")

                # git add .
                self.colors.info("▶ Ejecutando: git add .")
                add_result = self.run_git_command("git add .", allow_failure=True)
                if add_result["returncode"] != 0:
                    self.colors.error("Error al añadir cambios")
                    return

                # git commit
                self.colors.info(f"▶ Ejecutando: git commit -m '{message}'")
                commit_result = self.run_git_command(
                    f'git commit -m "{message}"', allow_failure=True
                )
                if commit_result["returncode"] != 0:
                    # Si no hay cambios para commitear, es normal
                    if "nothing to commit" in commit_result.get("stdout", ""):
                        self.colors.warning("⚠️ No hay cambios nuevos para commitear")
                    else:
                        self.colors.error("Error al hacer commit")
                        return
                else:
                    self.colors.success("✅ Commit realizado exitosamente")

            # PASO 4: Volver a develop y actualizar
            self.colors.info("\n🔄 PASO 4: Volviendo a develop y actualizando...")

            # Cambiar a develop
            checkout_dev = self.run_git_command(
                "git checkout develop", allow_failure=True
            )
            if checkout_dev["returncode"] != 0:
                self.colors.error("Error al cambiar a develop")
                return

            # Pull de develop nuevamente
            pull_dev = self.run_git_command(
                "git pull origin develop", allow_failure=True
            )
            if pull_dev["returncode"] != 0 and "Already up to date" not in pull_dev.get(
                "stdout", ""
            ):
                self.colors.warning("⚠️ Advertencia al actualizar develop")

            # Hacer merge de la feature branch
            self.colors.info(
                f"🔀 Haciendo merge de {Fore.YELLOW}{feature_name}{Fore.RESET}..."
            )
            merge_result = self.run_git_command(
                f"git merge {feature_name}", allow_failure=True
            )

            if merge_result["returncode"] != 0:
                if "Already up to date" in merge_result.get("stdout", ""):
                    self.colors.info("ℹ️ Ya está actualizado")
                else:
                    self.colors.error(f"Error al hacer merge de {feature_name}")
                    return
            else:
                self.colors.success("✅ Merge completado")

            # PASO 5: Subir cambios a develop
            self.colors.info("\n⬆️ PASO 5: Subiendo cambios a develop...")
            push_result = self.run_git_command(
                "git push origin develop", allow_failure=True
            )

            if push_result["returncode"] != 0:
                if "Everything up-to-date" in push_result.get("stdout", ""):
                    self.colors.info("ℹ️ Todo está actualizado")
                else:
                    self.colors.error("Error al subir cambios a develop")
                    self.colors.info("💡 Intenta: git push origin develop")
                    return
            else:
                self.colors.success("✅ Cambios subidos exitosamente a develop")

            # PASO 6: Eliminar rama feature (opcional)
            self.colors.info("\n🧹 PASO 6: Limpieza opcional...")
            cleanup = input("¿Eliminar la rama feature local? (s/N): ").strip().lower()

            if cleanup in ["s", "si", "sí", "y", "yes"]:
                # Eliminar rama local
                delete_local = self.run_git_command(
                    f"git branch -d {feature_name}", allow_failure=True
                )
                if delete_local["returncode"] == 0:
                    self.colors.success(f"✅ Rama local {feature_name} eliminada")
                else:
                    # Intentar con -D si falló
                    self.run_git_command(
                        f"git branch -D {feature_name}", allow_failure=True
                    )

                # Preguntar por rama remota
                remote_delete = (
                    input("¿Eliminar también del remoto? (s/N): ").strip().lower()
                )
                if remote_delete in ["s", "si", "sí", "y", "yes"]:
                    delete_remote = self.run_git_command(
                        f"git push origin --delete {feature_name}", allow_failure=True
                    )
                    if delete_remote["returncode"] == 0:
                        self.colors.success(f"✅ Rama remota {feature_name} eliminada")

            # RESUMEN FINAL
            self.colors.success("\n" + "=" * 60)
            self.colors.success("✅ FLUJO GITFLOW COMPLETADO EXITOSAMENTE")
            self.colors.success("=" * 60)
            self.colors.info(f"📋 Resumen de operaciones:")
            self.colors.info(
                f"   ✓ Rama feature: {Fore.YELLOW}{feature_name}{Fore.RESET}"
            )
            self.colors.info(f"   ✓ Mensaje commit: {Fore.CYAN}{message}{Fore.RESET}")
            self.colors.info(f"   ✓ Integrado en: {Fore.BLUE}develop{Fore.RESET}")
            self.colors.info(f"   ✓ Subido a: {Fore.GREEN}origin/develop{Fore.RESET}")

            # Mostrar estado final
            self.colors.info("\n📊 Estado final:")
            self.run_git_command("git status")

            # Log de éxito
            self.git_logger.log_operation(
                "FEATURE_BRANCH_WORKFLOW",
                f"GitFlow completado: {feature_name} → develop",
                "SUCCESS",
            )

        except Exception as e:
            self.colors.error(f"Error en el flujo: {str(e)}")
            self.git_logger.log_error(str(e), "feature_branch_workflow")
